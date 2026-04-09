# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from UI.Config import Config_Ui
from Scripts.Utils import (
    DEFAULT_LLM_PROVIDER,
    dict_result,
    get_config_dir,
    get_config_path,
    get_initial_data,
    get_user_info,
    get_title_font_family,
    get_ui_font_family,
    normalize_config,
    resource_path,
    say_something,
)
from Scripts.Monitor import monitor
import os
import json
import datetime
import threading
import requests
import websocket


class MainWindow_Ui(QtCore.QObject):
    # 信号槽，解决在线程中修改UI的问题
    add_message_signal    = QtCore.pyqtSignal(str, int)
    add_course_signal     = QtCore.pyqtSignal(list, int)
    del_course_signal     = QtCore.pyqtSignal(int)
    update_status_signal  = QtCore.pyqtSignal(str)
    update_problem_signal = QtCore.pyqtSignal(str)
    # 用户信息面板专用信号（跨线程安全更新右侧面板）
    _user_panel_signal    = QtCore.pyqtSignal(str, str, str, QtGui.QPixmap)

    @QtCore.pyqtSlot()
    def refresh_login_status(self):
        sessionid = self.config.get("sessionid", "")

        if sessionid:
            self.update_status_signal.emit("已登录")
            threading.Thread(
                target=self._fetch_and_emit_user_info,
                args=(sessionid,),
                daemon=True
            ).start()
        else:
            self.update_status_signal.emit("未登录")
            self._user_panel_signal.emit("未登录", "---", "---", QtGui.QPixmap())

    def setupUi(self, MainWindow):
        ui_font_family = get_ui_font_family()
        title_font_family = get_title_font_family()
        self.table_index = []
        self.is_active   = False

        # 最先加载配置和登录状态，供后续控件初始化使用
        dir_route = get_config_dir()
        config_route = get_config_path()
        self.config, _config_msg = self.check_config(dir_route, config_route)
        _login_status, _user_info = self.check_login()

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1070, 800)
        MainWindow.setWindowTitle("摸鱼课堂")
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet("background-color: rgb(255, 255, 255);")
        MainWindow.setWindowIcon(QtGui.QIcon(resource_path("UI\\Image\\favicon.ico")))

        self.Window = QtWidgets.QWidget(MainWindow)
        self.Window.setStyleSheet("background-color: rgb(255, 255, 255);")
        rootLayout = QtWidgets.QVBoxLayout(self.Window)
        rootLayout.setContentsMargins(0, 0, 0, 0)
        rootLayout.setSpacing(0)

        # 顶部菜单栏
        self.Menu = QtWidgets.QWidget(self.Window)
        self.Menu.setStyleSheet("background-color: rgb(17, 17, 17);")
        menuLayout = QtWidgets.QHBoxLayout(self.Menu)
        menuLayout.setContentsMargins(9, 9, 9, 9)
        menuLayout.setSpacing(6)

        icon_lbl = QtWidgets.QLabel(self.Menu)
        icon_lbl.setMaximumSize(32, 32)
        icon_lbl.setStyleSheet("border-radius:10px;")
        icon_lbl.setPixmap(QtGui.QPixmap(resource_path("UI\\Image\\NoRainClassroom.jpg")))
        icon_lbl.setScaledContents(True)
        menuLayout.addWidget(icon_lbl)

        title_lbl = QtWidgets.QLabel("摸鱼课堂", self.Menu)
        title_lbl.setStyleSheet(f"color: #fff; font: 16pt '{title_font_family}';")
        menuLayout.addWidget(title_lbl)

        menuLayout.addStretch()

        btn_style = "background-color: rgb(255,255,255);"
        self.active_btn = QtWidgets.QPushButton("启用", self.Menu)
        self.active_btn.setMaximumSize(100, 400)
        self.active_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.active_btn.setStyleSheet(btn_style)
        menuLayout.addWidget(self.active_btn)

        self.config_btn = QtWidgets.QPushButton("配置", self.Menu)
        self.config_btn.setMaximumSize(100, 400)
        self.config_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.config_btn.setStyleSheet(btn_style)
        menuLayout.addWidget(self.config_btn)

        rootLayout.addWidget(self.Menu)

        # 主体：左右分栏
        bodyWidget = QtWidgets.QWidget(self.Window)
        bodyLayout = QtWidgets.QHBoxLayout(bodyWidget)
        bodyLayout.setContentsMargins(0, 0, 0, 0)
        bodyLayout.setSpacing(0)

        # 左侧：现有功能区
        leftWidget = QtWidgets.QWidget(bodyWidget)
        leftLayout = QtWidgets.QVBoxLayout(leftWidget)
        leftLayout.setContentsMargins(6, 6, 6, 6)
        leftLayout.setSpacing(4)

        # 监听列表
        self.Table = QtWidgets.QGroupBox("监听列表", leftWidget)
        self.Table.setStyleSheet(f"font: 10pt '{ui_font_family}'; color: rgb(0,0,0);")
        tableBoxLayout = QtWidgets.QVBoxLayout(self.Table)
        self.tableWidget = QtWidgets.QTableWidget(self.Table)
        self.tableWidget.setStyleSheet(f"font: 9pt '{ui_font_family}';")
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        for i, h in enumerate(["课程名", "课程标题", "教师", "上课时间"]):
            self.tableWidget.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(h))
        self.tableWidget.horizontalHeader().setHighlightSections(False)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setHighlightSections(False)
        tableBoxLayout.addWidget(self.tableWidget)
        leftLayout.addWidget(self.Table, 3)

        # 信息框
        self.Output = QtWidgets.QGroupBox("信息", leftWidget)
        self.Output.setStyleSheet(f"font: 10pt '{ui_font_family}'; color: rgb(0,0,0);")
        outputBoxLayout = QtWidgets.QVBoxLayout(self.Output)
        self.output_textarea = QtWidgets.QTextBrowser(self.Output)
        self.output_textarea.setStyleSheet(
            f"background-color: rgb(100,100,100); color: #fff; font: 9pt '{ui_font_family}';"
        )
        self.output_textarea.setMinimumHeight(80)
        outputBoxLayout.addWidget(self.output_textarea)
        leftLayout.addWidget(self.Output, 2)

        # 题目框
        self.ProblemBox = QtWidgets.QGroupBox("当前题目", leftWidget)
        self.ProblemBox.setStyleSheet(f"font: 10pt '{ui_font_family}'; color: rgb(0,0,0);")
        problemBoxLayout = QtWidgets.QVBoxLayout(self.ProblemBox)
        self.problem_textarea = QtWidgets.QTextBrowser(self.ProblemBox)
        self.problem_textarea.setStyleSheet(
            f"background-color: rgb(245,245,245); color: #000; font: 10pt '{ui_font_family}';"
        )
        self.problem_textarea.setMinimumHeight(80)
        self.problem_textarea.setText("当前没有题目")
        problemBoxLayout.addWidget(self.problem_textarea)
        leftLayout.addWidget(self.ProblemBox, 2)

        bodyLayout.addWidget(leftWidget, 3)

        # 右侧：登录 / 用户信息面板
        self.rightPanel = QtWidgets.QWidget(bodyWidget)
        self.rightPanel.setFixedWidth(260)
        self.rightPanel.setStyleSheet(
            "background-color: #f7f8fa;"
            "border-left: 1px solid #e8e8e8;"
        )
        rightLayout = QtWidgets.QVBoxLayout(self.rightPanel)
        rightLayout.setContentsMargins(12, 16, 12, 16)
        rightLayout.setSpacing(10)
        rightLayout.setAlignment(QtCore.Qt.AlignTop)

        # 头像 / 二维码容器
        self.avatarLabel = QtWidgets.QLabel(self.rightPanel)
        self.avatarLabel.setFixedSize(180, 180)
        self.avatarLabel.setScaledContents(True)
        self.avatarLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.avatarLabel.setStyleSheet(
            "border: 1px solid #e0e0e0; border-radius: 8px; background: #fafafa;"
        )
        rightLayout.addWidget(self.avatarLabel, 0, QtCore.Qt.AlignHCenter)

        # 扫码提示 / 登录成功提示
        self.qrHint = QtWidgets.QLabel(
            "加载中..." if _login_status else "微信扫码登录",
            self.rightPanel
        )
        self.qrHint.setAlignment(QtCore.Qt.AlignCenter)
        self.qrHint.setWordWrap(True)
        self.qrHint.setStyleSheet(f"font: 9pt '{ui_font_family}'; color: #888;")
        rightLayout.addWidget(self.qrHint)

        # 状态徽标
        self.statusBadge = QtWidgets.QLabel(self.rightPanel)
        self.statusBadge.setFixedHeight(50)
        self.statusBadge.setAlignment(QtCore.Qt.AlignCenter)
        if _login_status:
            self._badge_success()
        else:
            self._badge_waiting()
        rightLayout.addWidget(self.statusBadge, 0, QtCore.Qt.AlignHCenter)

        # 分割线
        line1 = QtWidgets.QFrame(self.rightPanel)
        line1.setFrameShape(QtWidgets.QFrame.HLine)
        line1.setStyleSheet("color: #e0e0e0;")
        rightLayout.addWidget(line1)

        # 姓名
        self.nameLabel = QtWidgets.QLabel("—", self.rightPanel)
        self.nameLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.nameLabel.setWordWrap(True)
        self.nameLabel.setStyleSheet(f"font: bold 13pt '{ui_font_family}'; color: #222;")
        rightLayout.addWidget(self.nameLabel)

        # 学校
        schoolRow = QtWidgets.QWidget(self.rightPanel)
        schoolRowL = QtWidgets.QHBoxLayout(schoolRow)
        schoolRowL.setContentsMargins(0, 0, 0, 0)
        schoolKey = QtWidgets.QLabel("学校", schoolRow)
        schoolKey.setStyleSheet(f"font: 9pt '{ui_font_family}'; color: #999;")
        schoolKey.setFixedWidth(36)
        self.schoolVal = QtWidgets.QLabel("—", schoolRow)
        self.schoolVal.setStyleSheet(f"font: 9pt '{ui_font_family}'; color: #444;")
        self.schoolVal.setWordWrap(True)
        schoolRowL.addWidget(schoolKey)
        schoolRowL.addWidget(self.schoolVal)
        rightLayout.addWidget(schoolRow)

        # 学号
        snoRow = QtWidgets.QWidget(self.rightPanel)
        snoRowL = QtWidgets.QHBoxLayout(snoRow)
        snoRowL.setContentsMargins(0, 0, 0, 0)
        snoKey = QtWidgets.QLabel("学号", snoRow)
        snoKey.setStyleSheet(f"font: 9pt '{ui_font_family}'; color: #999;")
        snoKey.setFixedWidth(36)
        self.snoVal = QtWidgets.QLabel("—", snoRow)
        self.snoVal.setStyleSheet(f"font: 9pt '{ui_font_family}'; color: #444;")
        self.snoVal.setWordWrap(True)
        snoRowL.addWidget(snoKey)
        snoRowL.addWidget(self.snoVal)
        rightLayout.addWidget(snoRow)

        # 手机号（仅手机端签到时显示）
        self.phoneRow = QtWidgets.QWidget(self.rightPanel)
        phoneRowL = QtWidgets.QHBoxLayout(self.phoneRow)
        phoneRowL.setContentsMargins(0, 0, 0, 0)
        phoneKey = QtWidgets.QLabel("手机", self.phoneRow)
        phoneKey.setStyleSheet(f"font: 9pt '{ui_font_family}'; color: #999;")
        phoneKey.setFixedWidth(36)
        self.phoneVal = QtWidgets.QLabel("—", self.phoneRow)
        self.phoneVal.setStyleSheet(f"font: 9pt '{ui_font_family}'; color: #444;")
        self.phoneVal.setWordWrap(True)
        phoneRowL.addWidget(phoneKey)
        phoneRowL.addWidget(self.phoneVal)
        self.phoneRow.setVisible(False)  # 默认隐藏，手机端签到时显示
        rightLayout.addWidget(self.phoneRow)

        rightLayout.addStretch()

        # 分割线
        line2 = QtWidgets.QFrame(self.rightPanel)
        line2.setFrameShape(QtWidgets.QFrame.HLine)
        line2.setStyleSheet("color: #e0e0e0;")
        rightLayout.addWidget(line2)

        # 答题状态
        self.answer_mode_label = QtWidgets.QLabel("当前答题状态：—", self.rightPanel)
        self.answer_mode_label.setStyleSheet(f"font: 9pt '{ui_font_family}'; color: #555;")
        self.answer_mode_label.setWordWrap(False)
        rightLayout.addWidget(self.answer_mode_label)

        # API 测试状态
        self.api_status_label = QtWidgets.QLabel("", self.rightPanel)
        self.api_status_label.setStyleSheet(f"font: 8pt '{ui_font_family}'; color: #888;")
        self.api_status_label.setWordWrap(False)
        self.api_status_label.setVisible(False)
        rightLayout.addWidget(self.api_status_label)

        # 签到方式显示
        self.checkin_mode_label = QtWidgets.QLabel("签到方式：—", self.rightPanel)
        self.checkin_mode_label.setStyleSheet(
            f"""
            font: 9pt '{ui_font_family}';
            color: #d46b08;
            background: #fff7e6;
            border-left: 3px solid #fa8c16;
            border-radius: 6px;
            padding: 4px 8px;
            """
        )
        self.checkin_mode_label.setWordWrap(True)
        rightLayout.addWidget(self.checkin_mode_label)

        # 重新登录按钮
        self.relogin_btn = QtWidgets.QPushButton("重新登录", self.rightPanel)
        self.relogin_btn.setFixedHeight(32)
        self.relogin_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.relogin_btn.setStyleSheet(
            "QPushButton {"
            "  background: #fff; border: 1px solid #d0d0d0;"
            f"  border-radius: 6px; font: 9pt '{ui_font_family}'; color: #555;"
            "}"
            "QPushButton:hover { background: #f0f0f0; }"
        )
        rightLayout.addWidget(self.relogin_btn)

        bodyLayout.addWidget(self.rightPanel, 1)

        rootLayout.addWidget(bodyWidget, 1)

        # 状态栏
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        MainWindow.setCentralWidget(self.Window)

        # 信号槽绑定
        self.active_btn.clicked.connect(self.active_clicked)
        self.config_btn.clicked.connect(self.show_config)
        self.relogin_btn.clicked.connect(self.show_login)

        self.add_message_signal.connect(self.add_message,       QtCore.Qt.QueuedConnection)
        self.add_course_signal.connect(self.add_course,         QtCore.Qt.QueuedConnection)
        self.del_course_signal.connect(self.del_course,         QtCore.Qt.QueuedConnection)
        self.update_problem_signal.connect(self.update_problem, QtCore.Qt.QueuedConnection)
        self.update_status_signal.connect(self.statusbar.showMessage, QtCore.Qt.QueuedConnection)
        self._user_panel_signal.connect(self._on_user_info_ready, QtCore.Qt.QueuedConnection)

        self.add_message_signal.emit(_config_msg, 0)
        self.add_message_signal.emit("初始化完成", 0)

        # 根据登录状态启动对应流程
        if _login_status:
            _token = self.config.get("sessionid", "")
            threading.Thread(
                target=self._fetch_and_emit_user_info,
                args=(_token,),
                daemon=True
            ).start()
            self.add_message_signal.emit("登录成功，当前登录用户：" + _user_info.get("name", ""), 0)
        else:
            if not self.config.get("sessionid"):
                self._start_login_ws()

        self.refresh_answer_mode()

        QtCore.QTimer.singleShot(0, self.refresh_login_status)

    # 右侧面板：状态徽标辅助
    def _badge_waiting(self):
        self.statusBadge.setVisible(True)
        self.statusBadge.setText("等待扫码")
        self.statusBadge.setStyleSheet(
            f"font: 9pt '{get_ui_font_family()}'; color: #888;"
            "background: #efefef; border-radius: 11px; padding: 0 10px;"
        )

    def _badge_success(self):
        self.statusBadge.setVisible(True)
        self.statusBadge.setText("已登录 √")
        self.statusBadge.setStyleSheet(
            f"font: 9pt '{get_ui_font_family()}'; color: #07c160;"
            "background: #edfbf3; border-radius: 11px; padding: 0 10px;"
        )

    # 右侧面板：登录 WebSocket（内嵌，不弹窗）
    def _start_login_ws(self):
        # 启动二维码刷新 WebSocket，登录成功后自动更新面板。
        # 若已有旧连接先关掉
        if hasattr(self, '_ws_flush_on'):
            self._ws_flush_on = False
        if hasattr(self, '_wsapp'):
            try:
                self._wsapp.close()
            except Exception:
                pass

        def on_open(wsapp):
            wsapp.send(json.dumps(
                {"op": "requestlogin", "role": "web", "version": 1.4,
                 "type": "qrcode", "from": "web"}
            ))

        def on_close(wsapp):
            pass

        def on_message(wsapp, message):
            data = dict_result(message)
            op = data.get("op")

            if op == "requestlogin":
                try:
                    img = requests.get(
                        data["ticket"], proxies={"http": None, "https": None}, timeout=5
                    ).content
                    px = QtGui.QPixmap()
                    px.loadFromData(img)
                    # QLabel.setPixmap 必须在主线程，借用信号传一张空 QPixmap 占位触发刷新
                    # 直接用 invokeMethod 更简洁
                    QtCore.QMetaObject.invokeMethod(
                        self.avatarLabel, "setPixmap",
                        QtCore.Qt.QueuedConnection,
                        QtCore.Q_ARG(QtGui.QPixmap, px)
                    )
                    QtCore.QMetaObject.invokeMethod(
                        self.qrHint, "setText",
                        QtCore.Qt.QueuedConnection,
                        QtCore.Q_ARG(str, "微信扫码登录")
                    )
                except Exception:
                    pass

            elif op == "loginsuccess":
                web_login_url = "https://www.yuketang.cn/pc/web_login"
                login_data = json.dumps({
                    "UserID": data["UserID"],
                    "Auth":   data["Auth"]
                })
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; "
                                  "rv:104.0) Gecko/20100101 Firefox/104.0"
                }
                try:
                    r = requests.post(
                        web_login_url, data=login_data, headers=headers,
                        proxies={"http": None, "https": None}
                    )
                    sessionid = dict(r.cookies)["sessionid"]
                    self.config["sessionid"] = sessionid
                    # 保存 config
                    config_path = get_config_path()
                    with open(config_path, "w+") as f:
                        json.dump(self.config, f)
                    # 标记为扫码登录，_on_user_info_ready 里会打消息
                    self._login_from_scan = True
                    threading.Thread(
                        target=self._fetch_and_emit_user_info,
                        args=(sessionid,), daemon=True
                    ).start()
                except Exception as e:
                    self.add_message_signal.emit(f"登录处理异常: {e}", 0)

        self._wsapp = websocket.WebSocketApp(
            url="wss://www.yuketang.cn/wsapp/",
            on_open=on_open,
            on_message=on_message,
            on_close=on_close
        )
        self._ws_thread = threading.Thread(
            target=self._wsapp.run_forever, daemon=True
        )
        self._ws_thread.start()

        # 定时刷新二维码（每 60 秒）
        self._ws_flush_on = True

        def _flush():
            count = 0
            while self._ws_flush_on:
                if count == 60:
                    count = 0
                    try:
                        self._wsapp.send(json.dumps(
                            {"op": "requestlogin", "role": "web", "version": 1.4,
                             "type": "qrcode", "from": "web"}
                        ))
                    except Exception:
                        pass
                else:
                    import time as _t
                    _t.sleep(1)
                    count += 1

        self._ws_flush_thread = threading.Thread(target=_flush, daemon=True)
        self._ws_flush_thread.start()

    def _fetch_and_emit_user_info(self, sessionid):
        # 子线程：拉取用户信息后 emit 信号更新右侧面板。
        try:
            code, data = get_user_info(sessionid)
            if code != 0 or not data:
                return
            name   = data.get("name", "—")
            school = data.get("school", "—")
            sno    = data.get("schoolNumber", "—")
            avatar_url = data.get("avatar", "")
            px = QtGui.QPixmap()
            if avatar_url:
                try:
                    img = requests.get(
                        avatar_url, proxies={"http": None, "https": None}, timeout=5
                    ).content
                    px.loadFromData(img)
                except Exception:
                    pass
            self._user_panel_signal.emit(name, school, sno, px)
        except Exception:
            pass

    def _on_user_info_ready(self, name, school, sno, avatar_px):
        # 主线程槽：更新右侧用户信息面板。
        # 头像变圆
        if not avatar_px.isNull():
            size = 180
            avatar_px = avatar_px.scaled(
                size, size,
                QtCore.Qt.KeepAspectRatioByExpanding,
                QtCore.Qt.SmoothTransformation
            )
            rounded = QtGui.QPixmap(size, size)
            rounded.fill(QtCore.Qt.transparent)
            painter = QtGui.QPainter(rounded)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            path = QtGui.QPainterPath()
            path.addEllipse(0, 0, size, size)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, avatar_px)
            painter.end()
            self.avatarLabel.setPixmap(rounded)
            self.avatarLabel.setStyleSheet(
                "border: 2px solid #07c160; border-radius: 90px; background: #fff;"
            )

        self.qrHint.setText("登录成功")
        self.qrHint.setStyleSheet(f"font: 9pt '{get_ui_font_family()}'; color: #07c160;")
        self._badge_success()
        self.nameLabel.setText(name)
        self.schoolVal.setText(school)
        self.snoVal.setText(sno)

        # 停止刷二维码
        self._ws_flush_on = False
        # 只有扫码登录时才打消息，已登录启动时已经在 setupUi 打过了
        if getattr(self, '_login_from_scan', False):
            self.add_message_signal.emit("登录成功，当前登录用户：" + name, 0)
            self._login_from_scan = False

    def retranslateUi(self, MainWindow):
        pass  # 已在 setupUi 中直接设置文本

    def add_course(self, row, row_count):
        self.tableWidget.insertRow(row_count)
        for i in range(len(row)):
            content = QtWidgets.QTableWidgetItem(str(row[i]))
            self.tableWidget.setItem(row_count, i, content)
        model_index     = self.tableWidget.indexFromItem(content)
        per_model_index = QtCore.QPersistentModelIndex(model_index)
        self.table_index.append((row_count, per_model_index))

    def del_course(self, index):
        for row_count, per_model_index in self.table_index:
            if row_count == index:
                self.tableWidget.removeRow(per_model_index.row())
                self.table_index.remove((row_count, per_model_index))

    def refresh_answer_mode(self):
        # 根据配置刷新右侧答题状态显示，不发任何网络请求。
        auto_answer = self.config.get("auto_answer", False)
        if not auto_answer:
            self.answer_mode_label.setText("当前答题状态：已关闭")
            self.answer_mode_label.setStyleSheet(f"font: 9pt '{get_ui_font_family()}'; color: #aaa;")
            self.api_status_label.setVisible(False)
            return

        is_random = self.config.get("answer_config", {}).get("is_random", True)
        if is_random:
            self.answer_mode_label.setText("当前答题状态：随机做答")
            self.answer_mode_label.setStyleSheet(f"font: 9pt '{get_ui_font_family()}'; color: #555;")
            self.api_status_label.setVisible(False)
        else:
            provider = self.config.get("answer_config", {}).get("llm_provider", DEFAULT_LLM_PROVIDER)
            model = self.config.get("answer_config", {}).get("llm_model", "")
            provider_desc = provider if not model else f"{provider} / {model}"
            self.answer_mode_label.setText(f"当前答题状态：LLM 做答\n{provider_desc}")
            self.answer_mode_label.setStyleSheet(f"font: 9pt '{get_ui_font_family()}'; color: #1677ff;")
            # 读取上次测试结果，不发请求
            test_status = self.config.get("answer_config", {}).get("api_test_status", {})
            if test_status.get("tested"):
                success = test_status.get("success", False)
                msg = test_status.get("msg", "")
                color = "#07c160" if success else "#f00"
                prefix = "API 正常：" if success else "API 异常："
                self.api_status_label.setText(prefix + msg)
                self.api_status_label.setStyleSheet(f"font: 8pt '{get_ui_font_family()}'; color: {color};")
            else:
                api_key = self.config.get("answer_config", {}).get("apikey", "").strip()
                if api_key:
                    self.api_status_label.setText("API Key 已填写，请在配置页点击测试")
                    self.api_status_label.setStyleSheet(f"font: 8pt '{get_ui_font_family()}'; color: #fa8c16;")
                else:
                    self.api_status_label.setText("未填写 API Key")
                    self.api_status_label.setStyleSheet(f"font: 8pt '{get_ui_font_family()}'; color: #f00;")
            self.api_status_label.setVisible(True)
        mode = self.config.get("checkin_mode", "pc")
        if mode == "pc":
            text = "签到方式：💻 电脑端签到"
            self.phoneRow.setVisible(False)
        else:
            text = "签到方式：📱 手机端签到"
            # 手机端：显示已绑定的手机号（若有）
            phone = self.config.get("mobile_phone", "")
            self.phoneVal.setText(phone if phone else "—")
            self.phoneRow.setVisible(True)

        self.checkin_mode_label.setText(text)

    def show_config(self):
        dialog = QtWidgets.QDialog()
        dialog.setMinimumSize(600, 500)
        config_ui = Config_Ui()
        config_ui.main_win = self
        config_ui.setupUi(dialog)
        config_ui.load_config(self.config)
        config_ui.enable_delay_custom()
        if dialog.exec_():
            config_route = get_config_path()
            with open(config_route, "r", encoding="utf-8") as f:
                new_config = json.load(f)
            self.config.clear()
            self.config.update(new_config)
            self.refresh_answer_mode()
            self.refresh_right_panel()

    def show_login(self):
        # 重新登录：根据当前签到方式决定流程
        self.refresh_right_panel(force_relogin=True)

    def refresh_right_panel(self, mode=None, force_relogin=False):
        self.current_mode = mode

        sessionid = self.config.get("sessionid", "")

        if sessionid and not force_relogin:
            self._badge_success()
            threading.Thread(
                target=self._fetch_and_emit_user_info,
                args=(sessionid,),
                daemon=True
            ).start()
        else:
            self.avatarLabel.clear()
            self.avatarLabel.setStyleSheet(
                "border: 1px solid #e0e0e0; border-radius: 8px; background: #fafafa;"
            )
            self.qrHint.setText("微信扫码登录")
            self.qrHint.setStyleSheet(f"font: 9pt '{get_ui_font_family()}'; color: #888;")
            self._badge_waiting()

            self.nameLabel.setText("—")
            self.schoolVal.setText("—")
            self.snoVal.setText("—")

            self._start_login_ws()

    def check_config(self, dir_route, config_route):
        if not os.path.exists(dir_route):
            os.makedirs(dir_route)
        if not os.path.exists(config_route):
            initial_data = get_initial_data()
            with open(config_route, "w+", encoding="utf-8") as f:
                json.dump(initial_data, f, ensure_ascii=False)
            return initial_data, "没有检测到配置文件，已自动创建"
        else:
            try:
                with open(config_route, "r", encoding="utf-8") as f:
                    data = json.load(f)
                normalized = normalize_config(data)
                if normalized != data:
                    with open(config_route, "w+", encoding="utf-8") as f:
                        json.dump(normalized, f, ensure_ascii=False)
                    return normalized, "配置文件已读取，并已自动补全 LLM 配置"
                return normalized, "配置文件已读取"
            except Exception:
                with open(config_route, "w+", encoding="utf-8") as f:
                    initial_data = get_initial_data()
                    json.dump(initial_data, f, ensure_ascii=False)
                return initial_data, "配置文件读取失败，已重新生成"

    def check_login(self):
        sessionid = self.config.get("sessionid", "")
        if not sessionid:
            return False, {}
        code, user_info = get_user_info(sessionid)
        if code == 0:
            return True, user_info
        return False, {}

    def add_message(self, message, type=0):
        t = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
        self.last_event_time = datetime.datetime.now().timestamp()
        self.output_textarea.append(t + message)
        if type != 0:
            self.audio(message, type)

    def update_problem(self, message):
        self.problem_textarea.setText(message)

    def active_clicked(self):
        if self.is_active:
            self.deactive()
        else:
            self.active()

    def active(self):
        self.wakeup_event = threading.Event()
        self.monitor_t = threading.Thread(target=monitor, args=(self,), daemon=True)
        self.monitor_t.start()
        self.is_active = True
        self.active_btn.setText("停止监听")
        self.add_message_signal.emit("启动成功", 0)

    def deactive(self):
        self.active_btn.setText("停止中...")
        self.active_btn.setEnabled(False)
        QtWidgets.qApp.processEvents()
        self.is_active = False
        self.wakeup_event.set()
        self.monitor_t.join(timeout=5)
        self.active_btn.setEnabled(True)
        self.active_btn.setText("启动")
        self.add_message_signal.emit("停止成功", 0)

    def audio(self, message, type):
        audio_on = self.config["audio_on"]
        if audio_on:
            audio_type = self.config["audio_config"]["audio_type"]
            if (
                (type == 1 and audio_type["send_danmu"])   or
                (type == 2 and audio_type["others_danmu"]) or
                (type == 3 and audio_type["receive_problem"]) or
                (type == 4 and audio_type["answer_result"]) or
                (type == 5 and audio_type["im_called"])    or
                (type == 6 and audio_type["others_called"]) or
                (type == 7 and audio_type["course_info"])  or
                (type == 8 and audio_type["network_info"])
            ):
                threading.Thread(
                    target=say_something, args=(message,), daemon=True
                ).start()