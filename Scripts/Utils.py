import threading
import pyttsx3
import json
import urllib3
import requests
import random
import platform
import os
import sys

lock = threading.Lock()

def get_ui_font_family():
    return os.environ.get("RAINCLASSROOM_UI_FONT", "Microsoft YaHei")

def get_title_font_family():
    return os.environ.get("RAINCLASSROOM_TITLE_FONT", get_ui_font_family())

def say_something(text):
    lock.acquire()
    pyttsx3.speak(text)
    lock.release()
    
def dict_result(text):
    return dict(json.loads(text))

def test_network():
    try:
        http = urllib3.PoolManager()
        http.request('GET', 'https://baidu.com')
        return True
    except Exception:
        return False

LLM_PROVIDERS = {
    "DeepSeek": {"base_url": "https://api.deepseek.com", "model": "deepseek-reasoner"},
    "OpenAI": {"base_url": "https://api.openai.com/v1", "model": "gpt-5.4"},
    "Gemini": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "model": "gemini-3.1-pro-preview"},
    "DeepSeek-R1": {"base_url": "https://api.deepseek.com", "model": "deepseek-reasoner"},
    "智谱": {"base_url": "https://open.bigmodel.cn/api/paas/v4/", "model": "glm-5"},
    "Kimi": {"base_url": "https://api.moonshot.cn/v1", "model": "kimi-k2.5"},
    "通义千问": {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "model": "qwen3.5-plus"},
    "OpenRouter": {"base_url": "https://openrouter.ai/api/v1", "model": "openai/gpt-5.4"},
    "自定义": {"base_url": "", "model": ""}
}

DEFAULT_LLM_PROVIDER = "DeepSeek"
LEGACY_PROVIDER_MODELS = {
    "DeepSeek": {"deepseek-chat"},
    "OpenAI": {"gpt-4o-mini"},
    "Gemini": {"gemini-2.5-flash", "gemini-2.5-pro"},
    "智谱": {"glm-4-flash"},
    "Kimi": {"moonshot-v1-8k", "kimi-thinking-preview"},
    "通义千问": {"qwen-plus"},
    "OpenRouter": {"openai/gpt-4o-mini"},
}

def get_provider_names():
    return list(LLM_PROVIDERS.keys())

def get_provider_config(provider):
    return LLM_PROVIDERS.get(provider, LLM_PROVIDERS[DEFAULT_LLM_PROVIDER])

def normalize_answer_config(answer_config):
    answer_config = dict(answer_config or {})
    provider = answer_config.get("llm_provider", DEFAULT_LLM_PROVIDER)
    if provider not in LLM_PROVIDERS:
        provider = DEFAULT_LLM_PROVIDER
    provider_cfg = get_provider_config(provider)
    current_model = answer_config.get("llm_model", "").strip()
    if not current_model or current_model in LEGACY_PROVIDER_MODELS.get(provider, set()):
        current_model = provider_cfg.get("model", "")

    answer_config.setdefault("is_random", True)
    answer_config.setdefault("apikey", "")
    answer_config["llm_provider"] = provider
    answer_config["llm_model"] = current_model
    answer_config.setdefault("llm_base_url", provider_cfg.get("base_url", ""))
    answer_config.setdefault("api_test_status", {"tested": False})
    answer_config.setdefault("answer_delay", {"type": 1, "custom": {"time": 0}})
    answer_config["answer_delay"].setdefault("type", 1)
    answer_config["answer_delay"].setdefault("custom", {"time": 0})
    answer_config["answer_delay"]["custom"].setdefault("time", 0)
    return answer_config

def normalize_config(config):
    config = dict(config or {})
    initial_data = get_initial_data()
    for key, value in initial_data.items():
        if key not in config:
            config[key] = value
    if "checkin_mode" not in config:
        config["checkin_mode"] = "pc"
    config.setdefault("danmu_config", {}).setdefault("danmu_limit", 5)
    config.setdefault("audio_config", {}).setdefault("audio_type", {})
    for key, value in initial_data["audio_config"]["audio_type"].items():
        config["audio_config"]["audio_type"].setdefault(key, value)
    config["answer_config"] = normalize_answer_config(config.get("answer_config", {}))
    return config

def calculate_waittime(limit, type, custom_time):
    def default_calculate(limit):
        if limit == -1:
            wait_time = random.randint(5,20)
        else:
            if limit > 15:
                wait_time = random.randint(5,limit-10)
            else:
                wait_time = 0
        return wait_time

    if type == 1:
        wait_time = default_calculate(limit)
    elif type == 2:
        if limit != -1 and custom_time > limit:
            wait_time = default_calculate(limit)
        else:
            wait_time = custom_time
    return wait_time

def get_initial_data():
    initial_data = {
        "checkin_mode": "pc",
        "sessionid": "",
        "sid": "",
        "mobile_phone": "",
        "checkin_delay": 15,
        "poll_interval": 3,
        "auto_danmu": True,
        "danmu_config": {
            "danmu_limit": 5
        },
        "audio_on": False,
        "audio_config": {
            "audio_type": {
                "send_danmu": False,
                "others_danmu": False,
                "receive_problem": True,
                "answer_result": True,
                "im_called": True,
                "others_called": True,
                "course_info": True,
                "network_info": True
            }
        },
        "auto_answer": True,
        "answer_config": {
            "is_random": True,
            "apikey": "",
            "llm_provider": DEFAULT_LLM_PROVIDER,
            "llm_model": LLM_PROVIDERS[DEFAULT_LLM_PROVIDER]["model"],
            "llm_base_url": LLM_PROVIDERS[DEFAULT_LLM_PROVIDER]["base_url"],
            "api_test_status": {"tested": False},
            "answer_delay": {"type": 1, "custom": {"time": 0}}
        }
    }
    return initial_data

def get_config_path():
    return os.path.join(get_config_dir(), "config.json")

def get_config_dir():
    if platform.system() == "Windows":
        base_dir = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:
        base_dir = os.environ.get("XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config"))
    dir_route = os.path.join(base_dir, "RainClassroomAssistant")
    return dir_route

def get_user_info(sessionid):
    try:
        url = "https://www.yuketang.cn/api/v3/user/basic-info"
        r = requests.get(url=url, cookies={"sessionid": sessionid}, timeout=5,
                         proxies={"http": None, "https": None})
        rtn = dict_result(r.text)
        return (rtn.get("code", -1), rtn.get("data", {}))
    except:
        return (-1, {})

def get_on_lesson(sessionid):
    headers = {"Cookie": "sessionid=%s" % sessionid}
    r = requests.get("https://www.yuketang.cn/api/v3/classroom/on-lesson", headers=headers, proxies={"http": None, "https": None})
    rtn = dict_result(r.text)
    return rtn["data"]["onLessonClassrooms"]

def get_on_lesson_old(sessionid):
    headers = {
        "Cookie":"sessionid=%s" % sessionid,
    }
    r = requests.get("https://www.yuketang.cn/v/course_meta/on_lesson_courses",headers=headers,proxies={"http": None,"https":None})
    rtn = dict_result(r.text)
    return rtn["on_lessons"]

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    normalized_relative_path = relative_path.replace("\\", os.sep).replace("/", os.sep)
    return os.path.join(base_path, normalized_relative_path)

def verify_mobile_sms_code(phone: str, code: str):
    url = "https://www.yuketang.cn/api/v3/user/login/app"
    headers = {"xtbz": "ykt"}
    data = {"type": 3, "phoneNumber": phone, "code": code}
    try:
        r = requests.post(url, headers=headers, json=data, timeout=10)
        res = r.json()
        if res.get("code") == 0:
            sid = r.cookies.get("sid")
            return True, "登录成功", sid
        else:
            return False, res.get("msg", "验证码错误"), ""
    except Exception as e:
        return False, f"网络错误: {str(e)}", ""