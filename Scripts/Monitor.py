import time
import requests
import threading
from Scripts.Utils import get_on_lesson, test_network, say_something
from Scripts.Classes import Lesson

def monitor(main_ui):
    # 监听器函数

    wakeup_event = main_ui.wakeup_event  # 由 active() 提前初始化好
    main_ui.last_event_time = time.time()

    def del_onclass(lesson_obj):
        # 作为回调函数传入start_lesson
        on_lesson_list.remove(lesson_obj)
        # 下课后立即唤醒主循环，不用等满30秒
        wakeup_event.set()

    def wait_with_status(total, on_lesson_list):
        # 等待 total 秒，每秒更新状态栏，被唤醒则提前返回 True
        for _ in range(total, 0, -1):
            elapsed = int(time.time() - main_ui.last_event_time)
            if len(on_lesson_list) == 0:
                status = "当前无课程 | 距上次事件 %ds" % elapsed
            else:
                names = "、".join([l.lessonname for l in on_lesson_list])
                status = "监听中：%s | 距上次事件 %ds" % (names, elapsed)
            main_ui.update_status_signal.emit(status)
            if wakeup_event.wait(timeout=1):
                wakeup_event.clear()
                return True  # 被唤醒
        wakeup_event.clear()
        return False  # 正常超时

    def delayed_start(lesson_obj, delay):
        # 延迟签到
        if delay > 0:
            time.sleep(delay)
        lesson_obj.start_lesson(del_onclass)

    # 已经签到完成加入监听列表的课程
    on_lesson_list = []
    # 检测到的未加入监听列表的课程
    lesson_list = []
    network_status = True
    # 监听课程统一走电脑端 sessionid，手机端签到在 Lesson 内部处理
    sessionid = main_ui.config.get("sessionid", "")
    poll_interval = main_ui.config.get("poll_interval", 30)

    while True:
        # 获取课程列表
        try:
            lesson_list = get_on_lesson(sessionid)
        except requests.exceptions.ConnectionError:
            meg = "网络异常，监听中断"
            main_ui.add_message_signal.emit(meg,8)
            network_status = False
        except Exception:
            pass
        # 网络异常处理
        while not network_status:
            ret = test_network()
            if ret:
                try:
                    lesson_list = get_on_lesson(sessionid)
                    # lesson_list_old = get_on_lesson_old()
                except:
                    pass
                else:
                    network_status = True
                    meg = "网络已恢复，监听开始"
                    main_ui.add_message_signal.emit(meg,8)
                    break
            # 可结束线程的计时器
            timer = 0
            while timer <= 5:
                time.sleep(1)
                timer += 1
                if not main_ui.is_active:
                    for lesson in on_lesson_list.copy():
                        if hasattr(lesson, 'wsapp'):
                            lesson.wsapp.close()
                    return

        # 课程列表
        for lesson in lesson_list:
            lessionid = lesson["lessonId"]
            lessonname = lesson["courseName"]
            classroomid = lesson["classroomId"]
            lesson_obj = Lesson(lessionid,lessonname,classroomid,main_ui)
            if lesson_obj not in on_lesson_list:
                checkin_delay = main_ui.config.get("checkin_delay", 0)
                if checkin_delay > 0:
                    meg = "检测到课程%s正在上课，将在%d秒后签到" % (lessonname, checkin_delay)
                else:
                    meg = "检测到课程%s正在上课，即将签到" % lessonname
                main_ui.add_message_signal.emit(meg, 0)
                threading.Thread(target=say_something, args=(meg,)).start()
                thread = threading.Thread(target=delayed_start, args=(lesson_obj, checkin_delay), daemon=True)
                thread.start()
                on_lesson_list.append(lesson_obj)

        # 等待并更新状态栏
        triggered = wait_with_status(poll_interval, on_lesson_list)

        if not main_ui.is_active:
            for lesson in on_lesson_list.copy():
                if hasattr(lesson, 'wsapp'):
                    lesson.wsapp.close()
            return
        # 被下课事件唤醒后直接进入下一轮，不需要额外处理