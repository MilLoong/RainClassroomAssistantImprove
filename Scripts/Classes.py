import requests
import threading
import random
import time
import re
import websocket
import json
import os
from openai import OpenAI
from Scripts.Utils import (
    get_user_info,
    dict_result,
    calculate_waittime,
    say_something,
    get_config_dir,
    get_provider_config,
    DEFAULT_LLM_PROVIDER,
)

wss_url = "wss://www.yuketang.cn/wsapp/"

def build_llm_request_kwargs(provider, model):
    request_kwargs = {}
    normalized_model = (model or "").strip().lower()

    if provider in {"OpenAI", "Gemini"}:
        request_kwargs["reasoning_effort"] = "high"

    if provider == "OpenRouter" and "gpt-5" in normalized_model:
        request_kwargs["extra_body"] = {"reasoning": {"effort": "high"}}

    if provider == "智谱":
        request_kwargs["extra_body"] = {"thinking": {"type": "enabled"}}

    if provider == "通义千问" and "thinking" not in normalized_model:
        request_kwargs["extra_body"] = {"enable_thinking": True}

    if provider == "Kimi" and "thinking" not in normalized_model:
        request_kwargs["extra_body"] = {"enable_thinking": True}

    return request_kwargs

def test_llm_api(api_key, provider="DeepSeek"):
    # 测试 LLM API Key 是否可用。
    if not api_key or len(api_key.strip()) < 10:
        return False, "API Key 格式不正确"
    cfg = get_provider_config(provider)
    try:
        client = OpenAI(
            api_key=api_key.strip(),
            base_url=cfg["base_url"]
        )
        response = client.chat.completions.create(
            model=cfg["model"],
            messages=[{"role": "user", "content": "回复数字1"}],
            max_tokens=5,
            **build_llm_request_kwargs(provider, cfg["model"])
        )
        reply = (response.choices[0].message.content or "（模型未返回文字，但连接正常）").strip()
        return True, f"连接成功，模型回复：{reply}"
    except Exception as e:
        return False, f"连接失败：{str(e)}"

def test_llm_api_with_config(api_key, provider, model=None, base_url=None):
    if not api_key or len(api_key.strip()) < 10:
        return False, "API Key 格式不正确"
    provider_cfg = get_provider_config(provider)
    model = (model or provider_cfg.get("model", "")).strip()
    base_url = (base_url or provider_cfg.get("base_url", "")).strip()
    if not model:
        return False, "请先填写模型名称"
    if not base_url:
        return False, "请先填写 Base URL"
    try:
        client = OpenAI(api_key=api_key.strip(), base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "回复数字1"}],
            max_tokens=5,
            **build_llm_request_kwargs(provider, model)
        )
        reply = (response.choices[0].message.content or "（模型未返回文字，但连接正常）").strip()
        return True, f"连接成功，模型回复：{reply}"
    except Exception as e:
        return False, f"连接失败：{str(e)}"

class Lesson:
    def __init__(self, lessonid, lessonname, classroomid, main_ui):
        self.main_ui = main_ui
        self.config = main_ui.config
        self.lessonid = lessonid
        self.lessonname = lessonname
        self.classroomid = classroomid
        # 所有逻辑统一走电脑端 sessionid
        sessionid = self.config.get("sessionid", "")
        self.headers = {"Cookie": "sessionid=%s" % sessionid}

        checkin_mode = self.config.get("checkin_mode", "pc")
        if checkin_mode == "mobile":
            sid = self.config.get("sid", "")
            self.checkin_headers = {
                "x-client": "app",
                "Cookie": "sid=%s" % sid,
            }
        else:
            self.checkin_headers = self.headers

        self.receive_danmu = {}
        self.sent_danmu_dict = {}
        self.danmu_dict = {}
        self.problems_ls = []
        self.unlocked_problem = []
        self.classmates_ls = []
        self.ws_running = False
        self.add_message = main_ui.add_message_signal.emit
        self.add_course = main_ui.add_course_signal.emit
        self.del_course = main_ui.del_course_signal.emit
        self.update_problem = main_ui.update_problem_signal.emit
        code, rtn = get_user_info(sessionid)
        self.user_uid = rtn.get("id", "0")
        self.user_uname = rtn.get("name", "未知用户")

    def _get_ppt(self, presentationid):
        r = requests.get(
            url="https://www.yuketang.cn/api/v3/lesson/presentation/fetch?presentation_id=%s" % presentationid,
            headers=self.headers, proxies={"http": None, "https": None}
        )
        return dict_result(r.text)["data"]

    def _generate_random_answers(self, p_type, options, problem):
        answers = []
        if p_type in ["1", "2"]:
            if options:
                possible_keys = [opt['key'] for opt in options]
                if p_type == "1":
                    answers = [random.choice(possible_keys)]
                else:
                    num_to_select = random.randint(1, len(possible_keys))
                    answers = sorted(random.sample(possible_keys, num_to_select))
            else:
                answers = ["A"]
        return answers

    def _call_llm(self, quiz_dump):
        # 调用 LLM API 获取答案。
        api_key = self.config.get("answer_config", {}).get("apikey", "").strip()
        answer_cfg = self.config.get("answer_config", {})
        provider = answer_cfg.get("llm_provider", DEFAULT_LLM_PROVIDER)
        provider_cfg = get_provider_config(provider)
        model = answer_cfg.get("llm_model", provider_cfg.get("model", "")).strip()
        base_url = answer_cfg.get("llm_base_url", provider_cfg.get("base_url", "")).strip()
        p_type = str(quiz_dump.get("type", ""))
        type_str = "单选题" if p_type == "1" else "多选题"
        prompt = (
            f"你是一个答题助手。请根据题目和选项，选出正确答案。\n"
            f"题型：{type_str}\n"
            f"题目：{quiz_dump['question']}\n"
            + "选项：\n" + "\n".join(quiz_dump["options"]) + "\n\n"
            + "要求：只返回选项字母，单选返回一个字母如 A，多选返回多个字母用英文逗号分隔如 A,C，不要有任何其他内容。"
        )
        try:
            client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0.0,
                **build_llm_request_kwargs(provider, model)
            )
            raw = (response.choices[0].message.content or "").strip().upper()
            answers = [c for c in raw if c.isalpha()]
            if p_type == "1" and len(answers) > 1:
                answers = [answers[0]]
            return answers if answers else None
        except Exception as e:
            self.add_message(f"大模型调用异常：{e}", 0)
            return None

    def get_problems(self, presentationid):
        data = self._get_ppt(presentationid)
        problems = [problem["problem"] for problem in data["slides"] if "problem" in problem.keys()]
        return problems

    def answer_questions(self, problemid, problemtype, answer, limit):
        if answer and problemtype != 3:
            wait_time = calculate_waittime(
                limit,
                self.config["answer_config"]["answer_delay"]["type"],
                self.config["answer_config"]["answer_delay"]["custom"]["time"]
            )
            if wait_time != 0:
                meg = "将在%s秒后自动回答，答案为%s" % (wait_time, answer)
                self.add_message(meg, 3)
                time.sleep(wait_time)
            else:
                meg = "剩余时间小于15秒，将立即自动回答，答案为%s" % answer
                self.add_message(meg, 3)
            data = {"problemId": problemid, "problemType": problemtype, "dt": int(time.time()), "result": answer}
            r = requests.post(
                url="https://www.yuketang.cn/api/v3/lesson/problem/answer",
                headers=self.headers, data=json.dumps(data), proxies={"http": None, "https": None}
            )
            return_dict = dict_result(r.text)
            if return_dict["code"] == 0:
                meg = "%s自动回答成功" % self.lessonname
                self.add_message(meg, 4)
                return True
            else:
                meg = "%s自动回答失败，原因：%s" % (self.lessonname, return_dict["msg"].replace("_", " "))
                self.add_message(meg, 4)
                return False
        else:
            if limit == -1:
                meg = "该题不限时，请尽快前往雨课堂回答"
            else:
                meg = "请在%s秒内前往雨课堂回答" % limit
            self.add_message(meg, 4)
            return False

    def on_open(self, wsapp):
        self.add_message(f"WebSocket 连接成功！正在监听：{self.lessonname}", 0)
        self.handshark = {
            "op": "hello",
            "userid": self.user_uid,
            "role": "student",
            "auth": self.auth,
            "lessonid": self.lessonid
        }
        wsapp.send(json.dumps(self.handshark))
        self.retry_count = 0

    def checkin_class(self):
        r = requests.post(
            url="https://www.yuketang.cn/api/v3/lesson/checkin",
            headers=self.checkin_headers,
            data=json.dumps(
                {
                    "source": 5,
                    "lessonId": self.lessonid
                }
            ),
            proxies={"http": None, "https": None}
        )
        try:
            res_json = r.json()
        except Exception:
            self.add_message("签到接口返回格式异常", 7)
            return None
        if res_json.get("code") != 0:
            msg = res_json.get('msg', '未知错误')
            if msg == 'LESSON_END':
                return None
            elif 'DYNAMIC_QR_CHECK_IN_REFUSED' in msg:
                self.add_message("%s为动态二维码签到，请切换签到方式" % (self.lessonname), 7)
                return None
            elif msg == 'UNAUTHENTICATED':
                checkin_mode = self.config.get("checkin_mode", "pc")
                if checkin_mode == "mobile":
                    self.add_message("%s签到失败：sid 异常" % self.lessonname, 7)
                else:
                    self.add_message("%s签到失败：sessionid 异常" % self.lessonname, 7)
                return None
            else:
                self.add_message("%s签到失败，原因：%s" % (self.lessonname, msg), 7)
                return None
        set_auth = r.headers.get("Set-Auth", None)
        times = 1
        while not set_auth and times <= 3:
            set_auth = r.headers.get("Set-Auth", None)
            if set_auth:
                break
            times += 1
            time.sleep(1)
        if set_auth:
            self.headers["Authorization"] = "Bearer %s" % set_auth
        return res_json.get("data", {}).get("lessonToken")

    def on_message(self, wsapp, message):
        data = dict_result(message)
        op = data["op"]
        if op == "hello":
            presentations = list(set([slide["pres"] for slide in data["timeline"] if slide["type"] == "slide"]))
            current_presentation = data.get("presentation")
            if current_presentation and current_presentation not in presentations:
                presentations.append(current_presentation)
            for presentationid in presentations:
                self.problems_ls.extend(self.get_problems(presentationid))
            self.unlocked_problem = data.get("unlockedproblem", [])
            for problemid in self.unlocked_problem:
                self._current_problem(wsapp, problemid)
        elif op == "unlockproblem":
            self.start_answer(data["problem"]["sid"], data["problem"]["limit"])
        elif op == "lessonfinished":
            meg = "%s下课了" % self.lessonname
            self.add_message(meg, 7)
            self.ws_running = False
            wsapp.close()
        elif op == "presentationupdated":
            self.problems_ls.extend(self.get_problems(data["presentation"]))
        elif op == "presentationcreated":
            self.problems_ls.extend(self.get_problems(data["presentation"]))
        elif op == "newdanmu" and self.config["auto_danmu"]:
            current_content = data["danmu"].lower()
            uid = data["userid"]
            sent_danmu_user = User(uid)
            if sent_danmu_user in self.classmates_ls:
                for i in self.classmates_ls:
                    if i == sent_danmu_user:
                        meg = "%s课程的%s%s发送了弹幕：%s" % (self.lessonname, i.sno, i.name, data["danmu"])
                        self.add_message(meg, 2)
                        break
            else:
                self.classmates_ls.append(sent_danmu_user)
                sent_danmu_user.get_userinfo(self.classroomid, self.headers)
                meg = "%s课程的%s%s发送了弹幕：%s" % (self.lessonname, sent_danmu_user.sno, sent_danmu_user.name, data["danmu"])
                self.add_message(meg, 2)
            now = time.time()
            try:
                same_content_ls = self.danmu_dict[current_content]
            except KeyError:
                self.danmu_dict[current_content] = []
                same_content_ls = self.danmu_dict[current_content]
            for i in same_content_ls:
                if now - i > 60:
                    same_content_ls.remove(i)
            if current_content not in self.sent_danmu_dict.keys() or now - self.sent_danmu_dict[current_content] > 60:
                if len(same_content_ls) + 1 >= self.config["danmu_config"]["danmu_limit"]:
                    self.send_danmu(current_content)
                    same_content_ls = []
                    self.sent_danmu_dict[current_content] = now
                else:
                    same_content_ls.append(now)
        elif op == "callpaused":
            meg = "%s点名了，点到了：%s" % (self.lessonname, data["name"])
            if self.user_uname == data["name"]:
                self.add_message(meg, 5)
            else:
                self.add_message(meg, 6)
        elif op == "probleminfo":
            if data["limit"] != -1:
                time_left = int(data["limit"] - (int(data["now"]) - int(data["dt"])) / 1000)
            else:
                time_left = data["limit"]
            if time_left > 0 or time_left == -1:
                if self.config["auto_answer"]:
                    self.start_answer(data["problemid"], time_left)
                else:
                    if time_left == -1:
                        self.add_message("%s检测到问题，该题不限时，请尽快前往雨课堂回答" % self.lessonname, 3)
                    else:
                        self.add_message("%s检测到问题，请在%s秒内前往雨课堂回答" % (self.lessonname, time_left), 4)
        elif op == "extendtime":
            prob_data = data.get("problem", {})
            prob_id = prob_data.get("sid")
            limit = prob_data.get("limit")
            dt = prob_data.get("dt")
            now = prob_data.get("now")
            if not prob_id:
                self.add_message("延长时限: 收到信号但未解析出题目ID", 7)
                return
            if limit != -1 and now and dt:
                time_left = int(limit - (int(now) - int(dt)) / 1000)
            else:
                time_left = limit
            if time_left > 0 or time_left == -1:
                if self.config.get("auto_answer"):
                    self.add_message("%s的问题已延时" % self.lessonname, 3)
                    self.start_answer(prob_id, time_left)

    def start_answer(self, problemid, limit):
        for problem in self.problems_ls:
            if problem["problemId"] == problemid:
                if problem["result"] is not None:
                    self.add_message(f"{self.lessonname}的问题已回答过了，跳过自动回答", 7)
                    return
                raw_body = problem.get("body", "无题干内容")
                clean_body = re.sub(r'<[^>]+>', '', raw_body)
                options = problem.get("options", [])
                options_list = []
                for opt in options:
                    val = re.sub(r'<[^>]+>', '', str(opt.get('value', '')))
                    options_list.append(f"{opt['key']}: {val}")

                quiz_dump = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "lesson": self.lessonname,
                    "problemId": problemid,
                    "type": problem.get("problemType", "未知"),
                    "question": clean_body,
                    "options": options_list,
                    "raw_data": {
                        "blanks": problem.get("blanks", []),
                        "answers": problem.get("answers", [])
                    }
                }
                try:
                    quiz_dump_dir = os.path.join(get_config_dir(), "quiz_dump.json")
                    with open(quiz_dump_dir, "a", encoding="utf-8") as f:
                        f.write(json.dumps(quiz_dump, ensure_ascii=False) + "\n")
                except Exception as e:
                    print(f"写入 JSON 失败: {e}")

                time_str = f"{limit}秒" if limit != -1 else "不限时"
                box_options = "\n".join(options_list) if options_list else "该题无选项"
                display_text = (
                    f"课程: {self.lessonname}\n"
                    f"限时: {time_str}\n"
                    f"题目: {clean_body}\n"
                    f"选项: \n{box_options}"
                )
                self.main_ui.update_problem_signal.emit(display_text)

                p_type = str(problem.get("problemType", ""))

                # 非选择题：提示后直接返回，不走答题流程
                if p_type not in ["1", "2"]:
                    type_map = {"3": "投票题", "4": "填空题"}
                    type_name = type_map.get(p_type, "主观题")
                    if limit == -1:
                        meg = f"{self.lessonname}检测到{type_name}（不限时），请手动前往雨课堂作答"
                    else:
                        meg = f"{self.lessonname}检测到{type_name}，请在{limit}秒内前往雨课堂作答"
                    self.add_message(meg, 3)
                    return

                # 先告知检测到问题
                if limit == -1:
                    self.add_message(f"{self.lessonname}检测到问题（不限时），正在处理...", 3)
                else:
                    self.add_message(f"{self.lessonname}检测到问题，限时{limit}秒，正在处理...", 3)

                answers = []
                is_random = self.config.get("answer_config", {}).get("is_random", True)

                if is_random:
                    answers = self._generate_random_answers(p_type, options, problem)
                else:
                    api_key = self.config.get("answer_config", {}).get("apikey", "").strip()
                    if not api_key:
                        meg = "未配置 API Key，已切换为随机做答模式"
                        self.add_message(meg, 0)
                        answers = self._generate_random_answers(p_type, options, problem)
                    else:
                        meg = "正在请求大模型生成答案..."
                        self.add_message(meg, 0)
                        answers = self._call_llm(quiz_dump)
                        if answers:
                            self.add_message(f"大模型给出答案：{answers}", 0)
                        else:
                            meg = "大模型响应失败，已切换为随机做答"
                            self.add_message(meg, 0)
                            answers = self._generate_random_answers(p_type, options, problem)

                problem["result"] = answers
                threading.Thread(
                    target=self.answer_questions,
                    args=(problem["problemId"], problem["problemType"], answers, limit)
                ).start()
                break
        else:
            if limit == -1:
                self.add_message("%s的问题没有找到答案，该题不限时，请尽快前往雨课堂回答" % self.lessonname, 3)
            else:
                self.add_message("%s的问题没有找到答案，请在%s秒内前往雨课堂回答" % (self.lessonname, limit), 4)

    def _current_problem(self, wsapp, promblemid):
        query_problem = {"op": "probleminfo", "lessonid": self.lessonid, "problemid": promblemid, "msgid": 1}
        wsapp.send(json.dumps(query_problem))

    def start_lesson(self, callback):
        self.auth = self.checkin_class()
        if not self.auth:
            return
        meg = "%s已成功签到" % self.lessonname
        self.add_message(meg, 0)
        threading.Thread(target=say_something, args=(meg,)).start()
        index = None
        try:
            rtn = self.get_lesson_info()
            if not rtn:
                raise ValueError("课程信息为空")
            teacher = rtn.get("teacher", {}).get("name", "未知")
            title = rtn.get("title", "未知")
            if title == "未知" and teacher == "未知":
                raise ValueError("课程信息获取不完整，跳过添加")
            timestamp_ms = rtn.get("startTime", int(time.time() * 1000))
            timestamp = timestamp_ms // 1000
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
            index = self.main_ui.tableWidget.rowCount()
            self.add_course([self.lessonname, title, teacher, time_str], index)
        except Exception as e:
            self.add_message(f"获取课程详情失败，跳过信息展示: {e}", 0)

        # WebSocket 重连

        self.ws_running = True
        self.retry_count = 0
        max_retry = 5

        while self.ws_running and self.retry_count < max_retry:
            try:
                self.add_message(f"WebSocket 连接中...（第 {self.retry_count + 1} 次）", 0)

                self.normal_close = False

                def _on_close(ws, *args):
                    self.add_message("WebSocket 已断开", 7)
                    if not self.ws_running:
                        self.normal_close = True

                def _on_error(ws, err):
                    try:
                        self.add_message(f"WebSocket 错误: {err}", 7)
                    except:
                        pass

                self.wsapp = websocket.WebSocketApp(
                    url=wss_url,
                    header=self.headers,
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_close=_on_close,
                    on_error=_on_error
                )

                self.wsapp.run_forever(ping_interval=30, ping_timeout=10)

                if self.normal_close:
                    break

                self.retry_count += 1
                time.sleep(3)

            except Exception as e:
                self.add_message(f"WebSocket 连接异常: {e}", 7)
                self.retry_count += 1
                time.sleep(3)
            
        if self.ws_running and self.retry_count >= max_retry:
            self.add_message("WebSocket 重连次数已达上限，停止监听", 7)

        meg = "%s监听结束" % self.lessonname
        self.add_message(meg, 7)
        
        if index is not None:
            try:
                self.del_course(index)
            except Exception:
                pass
        
        return callback(self)

    def send_danmu(self, content):
        url = "https://www.yuketang.cn/api/v3/lesson/danmu/send"
        data = {
            "extra": "", "fromStart": "50", "lessonId": self.lessonid,
            "message": content, "requiredCensor": False, "showStatus": True,
            "target": "", "userName": "", "wordCloud": True
        }
        r = requests.post(url=url, headers=self.headers, data=json.dumps(data),
                          proxies={"http": None, "https": None})
        if dict_result(r.text)["code"] == 0:
            meg = "%s弹幕发送成功！内容：%s" % (self.lessonname, content)
        else:
            meg = "%s弹幕发送失败！内容：%s" % (self.lessonname, content)
        self.add_message(meg, 1)

    def get_lesson_info(self):
        url = "https://www.yuketang.cn/api/v3/lesson/basic-info"
        r = requests.get(url=url, headers=self.headers, proxies={"http": None, "https": None})
        return dict_result(r.text)["data"]

    def __eq__(self, other):
        return self.lessonid == other.lessonid


class User:
    def __init__(self, uid):
        self.uid = uid

    def get_userinfo(self, classroomid, headers):
        r = requests.get(
            "https://www.yuketang.cn/v/course_meta/fetch_user_info_new?query_user_id=%s&classroom_id=%s" % (
                self.uid, classroomid),
            headers=headers, proxies={"http": None, "https": None}
        )
        data = dict_result(r.text)["data"]
        self.sno = data["school_number"]
        self.name = data["name"]