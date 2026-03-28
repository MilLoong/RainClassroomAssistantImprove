# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets, QtGui
from Scripts.Utils import (
    get_config_path,
    resource_path,
    get_provider_names,
    get_provider_config,
    get_ui_font_family,
    DEFAULT_LLM_PROVIDER,
)
from Scripts.Classes import test_llm_api_with_config
import json
import functools
import threading

class Config_Ui(object):
    def setupUi(self, Dialog):
        ui_font_family = get_ui_font_family()
        Dialog.setObjectName("Dialog")
        Dialog.resize(430, 550)
        Dialog.setStyleSheet("background-color: rgb(255, 255, 255);\n"
f"font: 9pt \"{ui_font_family}\";")
        Dialog.setWindowIcon(QtGui.QIcon(resource_path("UI\\Image\\favicon.ico")))
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QtWidgets.QScrollArea(Dialog)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, -56, 393, 580))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.danmu_config = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.danmu_config.setObjectName("danmu_config")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.danmu_config)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.danmu_on = QtWidgets.QCheckBox(self.danmu_config)
        self.danmu_on.setObjectName("danmu_on")
        self.verticalLayout_2.addWidget(self.danmu_on)
        self.when_danmu_on = QtWidgets.QWidget(self.danmu_config)
        self.when_danmu_on.setEnabled(False)
        self.when_danmu_on.setObjectName("when_danmu_on")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.when_danmu_on)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtWidgets.QLabel(self.when_danmu_on)
        self.label.setScaledContents(False)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.danmu_spinBox = QtWidgets.QSpinBox(self.when_danmu_on)
        self.danmu_spinBox.setMaximum(32767)
        self.danmu_spinBox.setProperty("value", 5)
        self.danmu_spinBox.setObjectName("danmu_spinBox")
        self.verticalLayout_3.addWidget(self.danmu_spinBox)
        self.verticalLayout_2.addWidget(self.when_danmu_on)
        self.verticalLayout_12.addWidget(self.danmu_config)
        self.audio_config = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.audio_config.setObjectName("audio_config")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.audio_config)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.audio_on = QtWidgets.QCheckBox(self.audio_config)
        self.audio_on.setObjectName("audio_on")
        self.verticalLayout_4.addWidget(self.audio_on)
        self.when_audio_on = QtWidgets.QWidget(self.audio_config)
        self.when_audio_on.setEnabled(False)
        self.when_audio_on.setObjectName("when_audio_on")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.when_audio_on)
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.widget_4 = QtWidgets.QWidget(self.when_audio_on)
        self.widget_4.setObjectName("widget_4")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.widget_4)
        self.verticalLayout_11.setContentsMargins(9, 0, 0, 0)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.label_4 = QtWidgets.QLabel(self.widget_4)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_11.addWidget(self.label_4)
        self.verticalLayout_10.addWidget(self.widget_4)
        self.widget_3 = QtWidgets.QWidget(self.when_audio_on)
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.when_audio_on_1 = QtWidgets.QWidget(self.widget_3)
        self.when_audio_on_1.setObjectName("when_audio_on_1")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.when_audio_on_1)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.self_danmu = QtWidgets.QCheckBox(self.when_audio_on_1)
        self.self_danmu.setObjectName("self_danmu")
        self.verticalLayout_7.addWidget(self.self_danmu)
        self.others_danmu = QtWidgets.QCheckBox(self.when_audio_on_1)
        self.others_danmu.setObjectName("others_danmu")
        self.verticalLayout_7.addWidget(self.others_danmu)
        self.receive_problem = QtWidgets.QCheckBox(self.when_audio_on_1)
        self.receive_problem.setObjectName("receive_problem")
        self.verticalLayout_7.addWidget(self.receive_problem)
        self.answer_result = QtWidgets.QCheckBox(self.when_audio_on_1)
        self.answer_result.setObjectName("answer_result")
        self.verticalLayout_7.addWidget(self.answer_result)
        self.horizontalLayout_4.addWidget(self.when_audio_on_1)
        self.when_audio_on_2 = QtWidgets.QWidget(self.widget_3)
        self.when_audio_on_2.setObjectName("when_audio_on_2")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.when_audio_on_2)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.self_called = QtWidgets.QCheckBox(self.when_audio_on_2)
        self.self_called.setObjectName("self_called")
        self.verticalLayout_6.addWidget(self.self_called)
        self.others_called = QtWidgets.QCheckBox(self.when_audio_on_2)
        self.others_called.setObjectName("others_called")
        self.verticalLayout_6.addWidget(self.others_called)
        self.course = QtWidgets.QCheckBox(self.when_audio_on_2)
        self.course.setObjectName("course")
        self.verticalLayout_6.addWidget(self.course)
        self.network = QtWidgets.QCheckBox(self.when_audio_on_2)
        self.network.setObjectName("network")
        self.verticalLayout_6.addWidget(self.network)
        self.horizontalLayout_4.addWidget(self.when_audio_on_2)
        self.verticalLayout_10.addWidget(self.widget_3)
        self.verticalLayout_4.addWidget(self.when_audio_on)
        self.verticalLayout_12.addWidget(self.audio_config)

        # 答题配置
        self.answer_config = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.answer_config.setObjectName("answer_config")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.answer_config)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.answer_on = QtWidgets.QCheckBox(self.answer_config)
        self.answer_on.setObjectName("answer_on")
        self.verticalLayout_5.addWidget(self.answer_on)
        self.when_answer_on = QtWidgets.QWidget(self.answer_config)
        self.when_answer_on.setEnabled(False)
        self.when_answer_on.setObjectName("when_answer_on")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.when_answer_on)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.label_3 = QtWidgets.QLabel(self.when_answer_on)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_8.addWidget(self.label_3)
        self.delay_time_radio_1 = QtWidgets.QRadioButton(self.when_answer_on)
        self.delay_time_radio_1.setChecked(True)
        self.delay_time_radio_1.setObjectName("delay_time_radio_1")
        self.verticalLayout_8.addWidget(self.delay_time_radio_1)
        self.delay_time_radio_2 = QtWidgets.QRadioButton(self.when_answer_on)
        self.delay_time_radio_2.setObjectName("delay_time_radio_2")
        self.verticalLayout_8.addWidget(self.delay_time_radio_2)
        self.when_delay_time_2 = QtWidgets.QWidget(self.when_answer_on)
        self.when_delay_time_2.setEnabled(False)
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.when_delay_time_2)
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 3)
        self.delay_time_2_input = QtWidgets.QSpinBox(self.when_delay_time_2)
        self.verticalLayout_9.addWidget(self.delay_time_2_input)
        self.label_2 = QtWidgets.QLabel(self.when_delay_time_2)
        self.label_2.setWordWrap(True)
        self.verticalLayout_9.addWidget(self.label_2)
        self.verticalLayout_8.addWidget(self.when_delay_time_2)
        self.is_random_answer = QtWidgets.QCheckBox(self.when_answer_on)
        self.is_random_answer.setObjectName("is_random_answer")
        self.is_random_answer.setText("随机做答")
        self.verticalLayout_8.addWidget(self.is_random_answer)

        # 模型选择行
        self.provider_widget = QtWidgets.QWidget(self.when_answer_on)
        self.horizontalLayout_provider = QtWidgets.QHBoxLayout(self.provider_widget)
        self.horizontalLayout_provider.setContentsMargins(0, 5, 0, 0)
        self.label_provider = QtWidgets.QLabel("模型:", self.provider_widget)
        self.horizontalLayout_provider.addWidget(self.label_provider)
        self.llm_provider = QtWidgets.QComboBox(self.provider_widget)
        self.llm_provider.addItems(get_provider_names())
        self.llm_provider.setFixedWidth(180)
        self.horizontalLayout_provider.addWidget(self.llm_provider)
        self.horizontalLayout_provider.addStretch()
        self.verticalLayout_8.addWidget(self.provider_widget)

        self.llm_widget = QtWidgets.QWidget(self.when_answer_on)
        self.horizontalLayout_llm = QtWidgets.QHBoxLayout(self.llm_widget)
        self.horizontalLayout_llm.setContentsMargins(0, 5, 0, 0)
        self.label_apikey = QtWidgets.QLabel("API Key:", self.llm_widget)
        self.horizontalLayout_llm.addWidget(self.label_apikey)
        self.apikey_input = QtWidgets.QLineEdit(self.llm_widget)
        self.apikey_input.setPlaceholderText("在此输入 API Key...")
        self.apikey_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.horizontalLayout_llm.addWidget(self.apikey_input)
        self.test_api_btn = QtWidgets.QPushButton("测试", self.llm_widget)
        self.test_api_btn.setFixedWidth(48)
        self.test_api_btn.setFixedHeight(24)
        self.test_api_btn.setStyleSheet(
            f"QPushButton {{ background: #1677ff; color: #fff; border-radius: 4px; font: 8pt '{ui_font_family}'; }}"
            "QPushButton:hover { background: #4096ff; }"
            "QPushButton:disabled { background: #aaa; }"
        )
        self.test_api_btn.clicked.connect(self.test_api)
        self.horizontalLayout_llm.addWidget(self.test_api_btn)
        self.verticalLayout_8.addWidget(self.llm_widget)

        self.model_widget = QtWidgets.QWidget(self.when_answer_on)
        self.horizontalLayout_model = QtWidgets.QHBoxLayout(self.model_widget)
        self.horizontalLayout_model.setContentsMargins(0, 5, 0, 0)
        self.label_model = QtWidgets.QLabel("模型名:", self.model_widget)
        self.horizontalLayout_model.addWidget(self.label_model)
        self.llm_model_input = QtWidgets.QLineEdit(self.model_widget)
        self.llm_model_input.setPlaceholderText("例如：gpt-4o-mini / deepseek-chat")
        self.horizontalLayout_model.addWidget(self.llm_model_input)
        self.verticalLayout_8.addWidget(self.model_widget)

        self.base_url_widget = QtWidgets.QWidget(self.when_answer_on)
        self.horizontalLayout_base_url = QtWidgets.QHBoxLayout(self.base_url_widget)
        self.horizontalLayout_base_url.setContentsMargins(0, 5, 0, 0)
        self.label_base_url = QtWidgets.QLabel("Base URL:", self.base_url_widget)
        self.horizontalLayout_base_url.addWidget(self.label_base_url)
        self.llm_base_url_input = QtWidgets.QLineEdit(self.base_url_widget)
        self.llm_base_url_input.setPlaceholderText("例如：https://api.openai.com/v1")
        self.horizontalLayout_base_url.addWidget(self.llm_base_url_input)
        self.verticalLayout_8.addWidget(self.base_url_widget)

        # 测试结果提示行
        self.api_test_result = QtWidgets.QLabel("", self.when_answer_on)
        self.api_test_result.setWordWrap(True)
        self.api_test_result.setStyleSheet(f"font: 8pt '{ui_font_family}'; color: #888;")
        self.verticalLayout_8.addWidget(self.api_test_result)
        self.verticalLayout_5.addWidget(self.when_answer_on)
        self.verticalLayout_12.addWidget(self.answer_config)
        self.is_random_answer.stateChanged.connect(self.update_llm_visibility)

        # 监听配置
        self.poll_config = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.poll_config.setObjectName("poll_config")
        self.verticalLayout_poll = QtWidgets.QVBoxLayout(self.poll_config)
        self.verticalLayout_poll.setObjectName("verticalLayout_poll")

        # 签到配置
        self.CheckinGroup = QtWidgets.QGroupBox("签到配置", Dialog)
        self.CheckinGroup.setStyleSheet(f"font: 10pt '{ui_font_family}';")
        checkinLayout = QtWidgets.QVBoxLayout(self.CheckinGroup)

        self.checkin_mode_label = QtWidgets.QLabel("签到方式", self.CheckinGroup)
        self.checkin_mode_label.setStyleSheet(f"font: 9pt '{ui_font_family}'; color: #666;")
        self.checkin_mode_combo = QtWidgets.QComboBox(self.CheckinGroup)
        self.checkin_mode_combo.addItems(["电脑端签到", "手机端签到"])
        self.checkin_mode_combo.setStyleSheet(f"font: 9pt '{ui_font_family}'; padding: 4px;")
        checkinLayout.addWidget(self.checkin_mode_label)
        checkinLayout.addWidget(self.checkin_mode_combo)

        # 手机端签到专属区域（切换为手机端时才显示）
        self.mobile_checkin_widget = QtWidgets.QWidget(self.CheckinGroup)
        self.mobile_checkin_widget.setVisible(False)
        mobileLayout = QtWidgets.QVBoxLayout(self.mobile_checkin_widget)
        mobileLayout.setContentsMargins(0, 6, 0, 0)
        mobileLayout.setSpacing(6)

        # 提示文字
        mobile_hint = QtWidgets.QLabel(
            "手机端签到需要绑定手机号，请输入手机号并获取验证码后点击验证登录。",
            self.mobile_checkin_widget
        )
        mobile_hint.setWordWrap(True)
        mobile_hint.setStyleSheet(f"font: 8pt '{ui_font_family}'; color: #888;")
        mobileLayout.addWidget(mobile_hint)

        # 手机号输入行
        phoneInputRow = QtWidgets.QWidget(self.mobile_checkin_widget)
        phoneInputRowL = QtWidgets.QHBoxLayout(phoneInputRow)
        phoneInputRowL.setContentsMargins(0, 0, 0, 0)
        phone_label = QtWidgets.QLabel("手机号：", phoneInputRow)
        phone_label.setStyleSheet(f"font: 9pt '{ui_font_family}'; color: #555;")
        phone_label.setFixedWidth(56)
        self.mobile_phone_input = QtWidgets.QLineEdit(phoneInputRow)
        self.mobile_phone_input.setPlaceholderText("请输入手机号")
        self.mobile_phone_input.setMaxLength(11)
        self.mobile_phone_input.setStyleSheet(f"font: 9pt '{ui_font_family}'; padding: 3px;")
        phoneInputRowL.addWidget(phone_label)
        phoneInputRowL.addWidget(self.mobile_phone_input)
        mobileLayout.addWidget(phoneInputRow)

        # 验证码输入行
        codeInputRow = QtWidgets.QWidget(self.mobile_checkin_widget)
        codeInputRowL = QtWidgets.QHBoxLayout(codeInputRow)
        codeInputRowL.setContentsMargins(0, 0, 0, 0)
        code_label = QtWidgets.QLabel("验证码：", codeInputRow)
        code_label.setStyleSheet(f"font: 9pt '{ui_font_family}'; color: #555;")
        code_label.setFixedWidth(56)
        self.sms_code_input = QtWidgets.QLineEdit(codeInputRow)
        self.sms_code_input.setPlaceholderText("请输入短信验证码")
        self.sms_code_input.setMaxLength(6)
        self.sms_code_input.setStyleSheet(f"font: 9pt '{ui_font_family}'; padding: 3px;")
        self.verify_mobile_btn = QtWidgets.QPushButton("验证登录", codeInputRow)
        self.verify_mobile_btn.setFixedWidth(80)
        self.verify_mobile_btn.setFixedHeight(26)
        self.verify_mobile_btn.setStyleSheet(
            f"QPushButton {{ background: #07c160; color: #fff; border-radius: 4px; font: 8pt '{ui_font_family}'; }}"
            "QPushButton:hover { background: #09d16b; }"
            "QPushButton:disabled { background: #aaa; }"
        )
        self.verify_mobile_btn.clicked.connect(self.verify_mobile_login)
        codeInputRowL.addWidget(code_label)
        codeInputRowL.addWidget(self.sms_code_input)
        codeInputRowL.addWidget(self.verify_mobile_btn)
        mobileLayout.addWidget(codeInputRow)

        # 状态提示标签
        self.mobile_login_status = QtWidgets.QLabel("", self.mobile_checkin_widget)
        self.mobile_login_status.setWordWrap(True)
        self.mobile_login_status.setStyleSheet(f"font: 8pt '{ui_font_family}'; color: #888;")
        mobileLayout.addWidget(self.mobile_login_status)

        checkinLayout.addWidget(self.mobile_checkin_widget)
        self.verticalLayout_12.addWidget(self.CheckinGroup)

        # 切换签到方式时显示/隐藏手机端区域
        self.checkin_mode_combo.currentIndexChanged.connect(self.on_checkin_mode_changed)

        # 签到延迟
        self.label_checkin_delay = QtWidgets.QLabel(self.poll_config)
        self.label_checkin_delay.setWordWrap(True)
        self.label_checkin_delay.setObjectName("label_checkin_delay")
        self.verticalLayout_poll.addWidget(self.label_checkin_delay)
        self.checkin_delay_spinBox = QtWidgets.QSpinBox(self.poll_config)
        self.checkin_delay_spinBox.setMinimum(0)
        self.checkin_delay_spinBox.setMaximum(300)
        self.checkin_delay_spinBox.setValue(0)
        self.checkin_delay_spinBox.setObjectName("checkin_delay_spinBox")
        self.verticalLayout_poll.addWidget(self.checkin_delay_spinBox)
        # 轮询间隔
        self.label_poll_interval = QtWidgets.QLabel(self.poll_config)
        self.label_poll_interval.setWordWrap(True)
        self.label_poll_interval.setObjectName("label_poll_interval")
        self.verticalLayout_poll.addWidget(self.label_poll_interval)
        self.poll_interval_spinBox = QtWidgets.QSpinBox(self.poll_config)
        self.poll_interval_spinBox.setMinimum(1)
        self.poll_interval_spinBox.setMaximum(300)
        self.poll_interval_spinBox.setValue(30)
        self.poll_interval_spinBox.setObjectName("poll_interval_spinBox")
        self.verticalLayout_poll.addWidget(self.poll_interval_spinBox)
        self.verticalLayout_12.addWidget(self.poll_config)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.btn_wid = QtWidgets.QWidget(Dialog)
        self.btn_wid.setObjectName("btn_wid")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.btn_wid)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.save = QtWidgets.QPushButton(self.btn_wid)
        self.save.setMaximumSize(QtCore.QSize(16777215, 40))
        self.save.setObjectName("save")
        self.horizontalLayout.addWidget(self.save)
        self.cancel = QtWidgets.QPushButton(self.btn_wid)
        self.cancel.setMaximumSize(QtCore.QSize(16777215, 40))
        self.cancel.setObjectName("cancel")
        self.horizontalLayout.addWidget(self.cancel)
        self.verticalLayout.addWidget(self.btn_wid)

        # 动作绑定
        self.cancel.clicked.connect(Dialog.reject)
        self.danmu_on.stateChanged.connect(self.enable_danmu_config)
        self.audio_on.stateChanged.connect(self.enable_audio_config)
        self.answer_on.stateChanged.connect(self.enable_answer_config)
        self.is_random_answer.stateChanged.connect(self.toggle_llm_config)
        self.delay_time_radio_1.clicked.connect(self.enable_delay_custom)
        self.delay_time_radio_2.clicked.connect(self.enable_delay_custom)
        self.llm_provider.currentTextChanged.connect(self.on_provider_changed)
        self.save.clicked.connect(functools.partial(self.save_config,dialog=Dialog))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def update_llm_visibility(self):
        # 控制模型配置框的显隐：勾选随机作答时隐藏，不勾选时展示
        # 只要勾选了随机作答，就隐藏 AI 配置
        is_hidden = self.is_random_answer.isChecked()
        
        # 这里的控件名必须和你代码中定义的一一对应
        self.provider_widget.setVisible(not is_hidden)
        self.llm_widget.setVisible(not is_hidden)
        self.model_widget.setVisible(not is_hidden)
        self.base_url_widget.setVisible(not is_hidden)
        self.api_test_result.setVisible(not is_hidden)

    def test_api(self):
        api_key = self.apikey_input.text().strip()
        model = self.llm_model_input.text().strip()
        base_url = self.llm_base_url_input.text().strip()
        if not api_key:
            self.api_test_result.setStyleSheet(f"font: 8pt '{get_ui_font_family()}'; color: #f00;")
            self.api_test_result.setText("请先输入 API Key")
            return
        if not model:
            self.api_test_result.setStyleSheet(f"font: 8pt '{get_ui_font_family()}'; color: #f00;")
            self.api_test_result.setText("请先输入模型名称")
            return
        if not base_url:
            self.api_test_result.setStyleSheet(f"font: 8pt '{get_ui_font_family()}'; color: #f00;")
            self.api_test_result.setText("请先输入 Base URL")
            return
        self.test_api_btn.setEnabled(False)
        self.api_test_result.setStyleSheet(f"font: 8pt '{get_ui_font_family()}'; color: #888;")
        self.api_test_result.setText("测试中...")

        def _do_test():
            success, msg = test_llm_api_with_config(
                api_key,
                self.llm_provider.currentText(),
                model,
                base_url
            )
            from PyQt5.QtCore import QMetaObject, Qt, Q_ARG
            color = "#07c160" if success else "#f00"
            QMetaObject.invokeMethod(
                self.api_test_result, "setText",
                Qt.QueuedConnection, Q_ARG(str, msg)
            )
            QMetaObject.invokeMethod(
                self.api_test_result, "setStyleSheet",
                Qt.QueuedConnection,
                Q_ARG(str, f"font: 8pt '{get_ui_font_family()}'; color: {color};")
            )
            QMetaObject.invokeMethod(
                self.test_api_btn, "setEnabled",
                Qt.QueuedConnection, Q_ARG(bool, True)
            )
            # 将测试结果保存到配置文件
            test_status = {
                "tested": True,
                "success": success,
                "msg": msg,
                "tested_key": api_key,
                "tested_provider": self.llm_provider.currentText(),
                "tested_model": model,
                "tested_base_url": base_url
            }
            self.dialog_config["answer_config"]["api_test_status"] = test_status
            config_path = get_config_path()
            try:
                with open(config_path, "r") as f:
                    cfg = json.load(f)
                cfg["answer_config"]["api_test_status"] = test_status
                with open(config_path, "w") as f:
                    json.dump(cfg, f)
            except Exception:
                pass

        threading.Thread(target=_do_test, daemon=True).start()

    def _on_apikey_changed(self, text):
        # 模型相关配置变化时，若与上次测试参数不同则清空测试状态。
        if not hasattr(self, "dialog_config"):
            return
        status = self.dialog_config.get("answer_config", {}).get("api_test_status", {})
        if status.get("tested") and status.get("tested_key", "") != text.strip():
            self.dialog_config["answer_config"]["api_test_status"] = {"tested": False}
            self.api_test_result.setText("API Key 已修改，请重新测试")
            self.api_test_result.setStyleSheet(f"font: 8pt '{get_ui_font_family()}'; color: #fa8c16;")

    def _on_llm_setting_changed(self):
        if not hasattr(self, "dialog_config"):
            return
        status = self.dialog_config.get("answer_config", {}).get("api_test_status", {})
        if not status.get("tested"):
            return
        if (
            status.get("tested_provider", "") != self.llm_provider.currentText() or
            status.get("tested_model", "") != self.llm_model_input.text().strip() or
            status.get("tested_base_url", "") != self.llm_base_url_input.text().strip()
        ):
            self.dialog_config["answer_config"]["api_test_status"] = {"tested": False}
            self.api_test_result.setText("模型配置已修改，请重新测试")
            self.api_test_result.setStyleSheet(f"font: 8pt '{get_ui_font_family()}'; color: #fa8c16;")

    def on_provider_changed(self, provider):
        provider_cfg = get_provider_config(provider)
        self.llm_model_input.setText(provider_cfg.get("model", ""))
        self.llm_base_url_input.setText(provider_cfg.get("base_url", ""))
        self._on_llm_setting_changed()

    def toggle_llm_config(self):
        if self.is_random_answer.isChecked():
            self.provider_widget.setEnabled(False)
            self.llm_widget.setEnabled(False)
            self.model_widget.setEnabled(False)
            self.base_url_widget.setEnabled(False)
        else:
            self.provider_widget.setEnabled(True)
            self.llm_widget.setEnabled(True)
            self.model_widget.setEnabled(True)
            self.base_url_widget.setEnabled(True)
    
    def enable_danmu_config(self):
        if self.danmu_on.isChecked():
            self.when_danmu_on.setEnabled(True)
        else:
            self.when_danmu_on.setEnabled(False)

    def enable_audio_config(self):
        if self.audio_on.isChecked():
            self.when_audio_on.setEnabled(True)
        else:
            self.when_audio_on.setEnabled(False)

    def enable_answer_config(self):
        if self.answer_on.isChecked():
            self.when_answer_on.setEnabled(True)
        else:
            self.when_answer_on.setEnabled(False)

    def enable_delay_custom(self):
        if self.delay_time_radio_2.isChecked():
            self.when_delay_time_2.setEnabled(True)
        else:
            self.when_delay_time_2.setEnabled(False)

    def load_config(self, config):
        # 弹幕配置
        self.danmu_on.setChecked(config["auto_danmu"])
        self.danmu_spinBox.setValue(config["danmu_config"]["danmu_limit"])
        # 语音配置
        self.audio_on.setChecked(config["audio_on"])
        self.self_danmu.setChecked(config["audio_config"]["audio_type"]["send_danmu"])
        self.others_danmu.setChecked(config["audio_config"]["audio_type"]["others_danmu"])
        self.receive_problem.setChecked(config["audio_config"]["audio_type"]["receive_problem"])
        self.answer_result.setChecked(config["audio_config"]["audio_type"]["answer_result"])
        self.self_called.setChecked(config["audio_config"]["audio_type"]["im_called"])
        self.others_called.setChecked(config["audio_config"]["audio_type"]["others_called"])
        self.course.setChecked(config["audio_config"]["audio_type"]["course_info"])
        self.network.setChecked(config["audio_config"]["audio_type"]["network_info"])
        # 签到方式
        mode = config.get("checkin_mode", "pc")
        if mode == "pc":
            self.checkin_mode_combo.setCurrentIndex(0)
        else:
            self.checkin_mode_combo.setCurrentIndex(1)
        # 加载已保存的手机号
        self.mobile_phone_input.setText(config.get("mobile_phone", ""))
        self.on_checkin_mode_changed(self.checkin_mode_combo.currentIndex())
        self.answer_on.setChecked(config["auto_answer"])
        if config["answer_config"]["answer_delay"]["type"] == 1:
            self.delay_time_radio_1.setChecked(True)
        elif config["answer_config"]["answer_delay"]["type"] == 2:
            self.delay_time_radio_2.setChecked(True)
        self.delay_time_2_input.setValue(config["answer_config"]["answer_delay"]["custom"]["time"])
        ans_cfg = config.get("answer_config", {})
        self.is_random_answer.setChecked(ans_cfg.get("is_random", True))
        self.llm_provider.setCurrentText(ans_cfg.get("llm_provider", DEFAULT_LLM_PROVIDER))
        self.apikey_input.setText(ans_cfg.get("apikey", ""))
        self.llm_model_input.setText(ans_cfg.get("llm_model", get_provider_config(self.llm_provider.currentText()).get("model", "")))
        self.llm_base_url_input.setText(ans_cfg.get("llm_base_url", get_provider_config(self.llm_provider.currentText()).get("base_url", "")))
        self.toggle_llm_config()
        self.enable_delay_custom()
        # 答题配置
        self.update_llm_visibility()
        # 加载上次测试结果
        test_status = ans_cfg.get("api_test_status", {})
        if test_status.get("tested"):
            success = test_status.get("success", False)
            msg = test_status.get("msg", "")
            color = "#07c160" if success else "#f00"
            self.api_test_result.setText(msg)
            self.api_test_result.setStyleSheet(f"font: 8pt '{get_ui_font_family()}'; color: {color};")
        else:
            self.api_test_result.setText("未测试")
            self.api_test_result.setStyleSheet(f"font: 8pt '{get_ui_font_family()}'; color: #aaa;")
        # 绑定 Key 变化监听（先断开防止重复绑定）
        try:
            self.apikey_input.textChanged.disconnect()
        except Exception:
            pass
        self.apikey_input.textChanged.connect(self._on_apikey_changed)
        for widget in [self.llm_model_input, self.llm_base_url_input]:
            try:
                widget.textChanged.disconnect()
            except Exception:
                pass
            widget.textChanged.connect(self._on_llm_setting_changed)
        # 监听配置
        self.checkin_delay_spinBox.setValue(config.get("checkin_delay", 0))
        self.poll_interval_spinBox.setValue(config.get("poll_interval", 30))
        self.dialog_config = config

    def save_config(self, dialog):
        config_path = get_config_path()
        try:
            with open(config_path, "r", encoding='utf-8') as f:
                config = json.load(f)
        except Exception:
            config = self.dialog_config
        # 弹幕配置
        config["auto_danmu"] = self.danmu_on.isChecked()
        config["danmu_config"]["danmu_limit"] = self.danmu_spinBox.value()
        # 语音配置
        config["audio_on"] = self.audio_on.isChecked()
        config["audio_config"]["audio_type"]["send_danmu"] = self.self_danmu.isChecked()
        config["audio_config"]["audio_type"]["others_danmu"] = self.others_danmu.isChecked()
        config["audio_config"]["audio_type"]["receive_problem"] = self.receive_problem.isChecked()
        config["audio_config"]["audio_type"]["answer_result"] = self.answer_result.isChecked()
        config["audio_config"]["audio_type"]["im_called"] = self.self_called.isChecked()
        config["audio_config"]["audio_type"]["others_called"] = self.others_called.isChecked()
        config["audio_config"]["audio_type"]["course_info"] = self.course.isChecked()
        config["audio_config"]["audio_type"]["network_info"] = self.network.isChecked()
        # 签到方式
        config["checkin_mode"] = "pc" if self.checkin_mode_combo.currentIndex() == 0 else "mobile"
        # 手机号（手机端签到时保存输入框里的值）
        config["mobile_phone"] = self.mobile_phone_input.text().strip()
        # 答题配置
        config["auto_answer"] = self.answer_on.isChecked()
        if self.delay_time_radio_1.isChecked():
            config["answer_config"]["answer_delay"]["type"] = 1
        elif self.delay_time_radio_2.isChecked():
            config["answer_config"]["answer_delay"]["type"] = 2
        config["answer_config"]["answer_delay"]["custom"]["time"] = self.delay_time_2_input.value()
        config["answer_config"]["is_random"] = self.is_random_answer.isChecked()
        config["answer_config"]["llm_provider"] = self.llm_provider.currentText()
        config["answer_config"]["apikey"] = self.apikey_input.text()
        config["answer_config"]["llm_model"] = self.llm_model_input.text().strip()
        config["answer_config"]["llm_base_url"] = self.llm_base_url_input.text().strip()
        # 监听配置
        config["checkin_delay"] = self.checkin_delay_spinBox.value()
        config["poll_interval"] = self.poll_interval_spinBox.value()
        # 保存
        config_path = get_config_path()
        with open(config_path,"w+") as f:
            json.dump(config,f)
        dialog.accept()

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "配置"))
        self.danmu_config.setTitle(_translate("Dialog", "弹幕配置"))
        self.danmu_on.setText(_translate("Dialog", "启用自动发送弹幕"))
        self.label.setText(_translate("Dialog", "自动弹幕阈值（每分钟内收到n条弹幕后自动发送相同弹幕）"))
        self.audio_config.setTitle(_translate("Dialog", "语音配置"))
        self.audio_on.setText(_translate("Dialog", "启用语音提醒"))
        self.label_4.setText(_translate("Dialog", "需要语音提醒的内容"))
        self.self_danmu.setText(_translate("Dialog", "自动发送弹幕情况提醒"))
        self.others_danmu.setText(_translate("Dialog", "他人弹幕发送语音提醒"))
        self.receive_problem.setText(_translate("Dialog", "收到题目提醒"))
        self.answer_result.setText(_translate("Dialog", "自动答题情况提醒"))
        self.self_called.setText(_translate("Dialog", "自己被点名提醒"))
        self.others_called.setText(_translate("Dialog", "他人被点名提醒"))
        self.course.setText(_translate("Dialog", "课程相关提醒"))
        self.network.setText(_translate("Dialog", "网络断开/重连提醒"))
        self.answer_config.setTitle(_translate("Dialog", "答题配置"))
        self.answer_on.setText(_translate("Dialog", "启用自动答题"))
        self.label_3.setText(_translate("Dialog", "答题延迟时长"))
        self.delay_time_radio_1.setText(_translate("Dialog", "系统默认（随机决定时间）"))
        self.delay_time_radio_2.setText(_translate("Dialog", "自定义（于收到题目n秒后自动回答）"))
        self.label_2.setText(_translate("Dialog", "注：如果您采用自定义延迟时长，当延迟时长大于题目所给时限时，将按照系统默认算法重新计算延迟时长。"))
        self.answer_config.setTitle(_translate("Dialog", "答题配置"))
        self.answer_on.setText(_translate("Dialog", "启用自动答题"))
        self.label_3.setText(_translate("Dialog", "答题延迟时长"))
        self.label_provider.setText(_translate("Dialog", "供应商:"))
        self.label_model.setText(_translate("Dialog", "模型名:"))
        self.label_base_url.setText(_translate("Dialog", "Base URL:"))
        self.save.setText(_translate("Dialog", "保存"))
        self.cancel.setText(_translate("Dialog", "取消"))
        self.poll_config.setTitle(_translate("Dialog", "监听配置"))
        self.label_checkin_delay.setText(_translate("Dialog", "签到延迟（秒）：检测到课程后延迟n秒再签到，0为立即签到"))
        self.label_poll_interval.setText(_translate("Dialog", "轮询间隔（秒）：每隔n秒检测一次是否有课程"))

    #  签到方式切换
    def on_checkin_mode_changed(self, index):
        # 切换签到方式时显示/隐藏手机端登录区域。
        is_mobile = (index == 1)
        self.mobile_checkin_widget.setVisible(is_mobile)
        if not is_mobile:
            # 切回电脑端时清空状态提示，不清空手机号（方便再切回来）
            self.mobile_login_status.setText("")

    def verify_mobile_login(self):
        phone = self.mobile_phone_input.text().strip()
        code  = self.sms_code_input.text().strip() 
        
        if not phone or not code:
            self.mobile_login_status.setStyleSheet(f"color: #f00;")
            self.mobile_login_status.setText("请填写手机号和验证码")
            return

        self.verify_mobile_btn.setEnabled(False)
        self.mobile_login_status.setText("验证中...")

        def _do_verify():
            from Scripts.Utils import verify_mobile_sms_code, get_config_path
            from PyQt5.QtCore import QMetaObject, Qt, Q_ARG

            success, msg, sid = verify_mobile_sms_code(phone, code)

            if success and sid:
                config_path = get_config_path()
                try:
                    with open(config_path, "r", encoding='utf-8') as f:
                        cfg = json.load(f)

                    cfg["checkin_mode"] = "mobile"
                    # 这里直接覆盖第一层字典即可，不再用什么 mobile_config 的占位符了
                    cfg["sid"] = sid
                    cfg["mobile_phone"] = phone

                    with open(config_path, "w", encoding='utf-8') as f:
                        json.dump(cfg, f, indent=4, ensure_ascii=False)

                    if hasattr(self, "main_win"):
                        QMetaObject.invokeMethod(self.main_win, "refresh_login_status", Qt.QueuedConnection)

                    msg = "登录成功"
                except Exception as e:
                    success = False
                    msg = f"保存配置失败: {e}"

            color = "#07c160" if success else "#f00"
            QMetaObject.invokeMethod(self.mobile_login_status, "setText", Qt.QueuedConnection, Q_ARG(str, msg))
            QMetaObject.invokeMethod(self.mobile_login_status, "setStyleSheet", Qt.QueuedConnection, Q_ARG(str, f"color: {color};"))
            QMetaObject.invokeMethod(self.verify_mobile_btn, "setEnabled", Qt.QueuedConnection, Q_ARG(bool, True))

        threading.Thread(target=_do_verify, daemon=True).start()