import json
import os
import requests

from PyQt5.QtCore import Qt, QObject, pyqtSlot, QUrl
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel


YKT_SEND_URL = "https://www.yuketang.cn/api/v3/user/code/send"
YKT_HEADERS = {
    "x-client": "app"
}
TCAPTCHA_AID = "2091064951"


def _get_captcha_prehandle() -> dict:
    url = "https://turing.captcha.qcloud.com/cap_union_prehandle"
    params = {
        "aid": TCAPTCHA_AID,
        "protocol": "https",
        "accver": "1",
        "showtype": "popup",
        "noheader": "0",
        "fb": "1",
        "aged": "0",
        "enableAged": "0",
        "enableDarkMode": "0",
        "grayscale": "1",
        "clientype": "1",
        "entry_url": "file:///android_asset/flutter_assets/packages/flutter_tencent_captcha/assets/captcha.html",
        "elder_captcha": "0",
        "js": "/tcaptcha-frame.5bae14dd.js",
        "wb": "1",
        "subsid": "1",
        "callback": "_captchaCallback",
        "sess": "",
        "cap_cd": "",
        "uid": "",
        "login_appid": "",
    }
    resp = requests.get(url, params=params, timeout=10)
    text = resp.text.strip()
    if text.startswith("_captchaCallback("):
        text = text[len("_captchaCallback("):-1]
    return json.loads(text)


def _send_sms_code(phone_number: str, ticket: str, rand: str) -> dict:
    payload = {
        "phoneNumber": phone_number,
        "email": "",
        "ticket": ticket,
        "rand": rand,
    }
    resp = requests.post(YKT_SEND_URL, headers=YKT_HEADERS, json=payload, timeout=10)
    return resp.json()


class _CaptchaBridge(QObject):
    def __init__(self, dialog):
        super().__init__()
        self._dialog = dialog

    @pyqtSlot(str, str)
    def onSuccess(self, ticket, randstr):
        self._dialog.on_captcha_done(ticket, randstr)

    @pyqtSlot(int, str)
    def onError(self, _code, msg):
        self._dialog.set_status("验证失败（%s），请刷新重试" % msg)

    @pyqtSlot()
    def onRefresh(self):
        self._dialog.refresh_captcha()


class CaptchaSmsDialog(QDialog):
    def __init__(self, phone_number: str, data: dict, parent=None):
        super().__init__(parent)
        self._phone_number = phone_number
        self._data = data
        self.result_success = False
        self.result_message = ""
        self._setup_ui()
        self._load(data)

    def _setup_ui(self):
        self.setWindowTitle("雨课堂 · 图形验证")
        self.setFixedSize(640, 560)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        self._status = QLabel("正在加载验证码...")
        self._status.setAlignment(Qt.AlignCenter)
        self._status.setStyleSheet("font-size:14px; color:#555;")
        layout.addWidget(self._status)

        self._web = QWebEngineView()
        layout.addWidget(self._web)

        self._channel = QWebChannel()
        self._bridge = _CaptchaBridge(self)
        self._channel.registerObject("pyBridge", self._bridge)
        self._web.page().setWebChannel(self._channel)

    def set_status(self, text: str):
        self._status.setText(text)

    def _load(self, data):
        dyn = data.get("data", {}).get("dyn_show_info", {})
        sess = data.get("sess", "")
        instruction = dyn.get("instruction", "请依次点击指定汉字")
        img_path = dyn.get("bg_elem_cfg", {}).get("img_url", "")
        img_url = "https://turing.captcha.qcloud.com" + img_path
        pow_cfg = data.get("data", {}).get("comm_captcha_cfg", {}).get("pow_cfg", {})
        pow_prefix = pow_cfg.get("prefix", "")
        pow_md5 = pow_cfg.get("md5", "")

        self.set_status(instruction)

        html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="qrc:///qtwebchannel/qwebchannel.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/spark-md5/3.0.2/spark-md5.min.js"></script>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: "Microsoft YaHei", sans-serif;
  background: #f0f2f5;
  display: flex; flex-direction: column;
  align-items: center; padding: 16px;
  user-select: none;
}
#wrap {
  position: relative; cursor: crosshair;
  border-radius: 8px; overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,.2);
}
#img {
  display: block; width: 560px; height: 400px; object-fit: cover;
}
.dot {
  position: absolute; width: 30px; height: 30px;
  border-radius: 50%; background: #1a79ff;
  border: 2px solid #fff; color: #fff;
  font-size: 13px; font-weight: bold;
  display: flex; align-items: center; justify-content: center;
  transform: translate(-50%,-50%);
  pointer-events: none;
  box-shadow: 0 1px 4px rgba(0,0,0,.35);
}
#bar { display: flex; gap: 10px; margin-top: 12px; }
button {
  padding: 8px 28px; border-radius: 6px;
  border: none; cursor: pointer; font-size: 14px;
}
#btn-ok  { background:#1a79ff; color:#fff; display:none; }
#btn-ref { background:#fff; color:#888; border:1px solid #ddd; }
#msg { margin-top: 8px; font-size: 13px; color: #e53e3e; min-height: 20px; }
</style>
</head>
<body>
<div id="wrap">
  <img id="img" src="__IMG_URL__" crossorigin="anonymous" draggable="false">
</div>
<div id="bar">
  <button id="btn-ok"  onclick="submitAns()">&#10003; 确认</button>
  <button id="btn-ref" onclick="refreshCaptcha()">&#8635; 刷新</button>
</div>
<div id="msg"></div>
<script>
const REQUIRED = 3;
const clicks = [];
const wrap = document.getElementById('wrap');
const imgEl = document.getElementById('img');
let pyBridge = null;

new QWebChannel(qt.webChannelTransport, function(ch) {
  pyBridge = ch.objects.pyBridge;
});

imgEl.addEventListener('load', function() {
  wrap.addEventListener('click', function(e) {
    if (clicks.length >= REQUIRED) return;
    const r = wrap.getBoundingClientRect();
    const px = Math.round((e.clientX - r.left) * 672 / wrap.offsetWidth);
    const py = Math.round((e.clientY - r.top)  * 480 / wrap.offsetHeight);
    clicks.push({x: px, y: py});
    const dot = document.createElement('div');
    dot.className = 'dot';
    dot.textContent = clicks.length;
    dot.style.left = (e.clientX - r.left) + 'px';
    dot.style.top  = (e.clientY - r.top)  + 'px';
    wrap.appendChild(dot);
    if (clicks.length === REQUIRED)
      document.getElementById('btn-ok').style.display = 'inline-block';
  });
});

function submitAns() {
  const msg = document.getElementById('msg');
  const btn = document.getElementById('btn-ok');
  msg.textContent = '验证中...';
  btn.disabled = true;

  var powAnswer = '', powTime = 0;
  var prefix = '__POW_PREFIX__';
  var target = '__POW_MD5__';
  if (prefix && target && typeof SparkMD5 !== 'undefined') {
    var t0 = Date.now();
    for (var i = 0; i < 2000000; i++) {
      var c = prefix + i;
      if (SparkMD5.hash(c) === target) {
        powAnswer = c; powTime = Date.now() - t0; break;
      }
    }
  }

  var ans = clicks.map(function(c, i) {
    return {elem_id: i+1, type: 'DynAnswerType_POS', data: c.x+','+c.y};
  });

  var body = 'sess=' + encodeURIComponent('__SESS__')
    + '&ans=' + encodeURIComponent(JSON.stringify(ans))
    + '&pow_answer=' + encodeURIComponent(powAnswer)
    + '&pow_calc_time=' + powTime
    + '&collect=&eks=&tlg=1048';

  fetch('https://turing.captcha.qcloud.com/cap_union_new_verify', {
    method: 'POST',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: body
  })
  .then(function(r) { return r.json(); })
  .then(function(d) {
    if (d.ticket) {
      msg.style.color = '#22c55e';
      msg.textContent = '验证成功，正在发送验证码...';
      if (pyBridge) pyBridge.onSuccess(d.ticket, d.randstr || '');
    } else {
      msg.textContent = '验证失败（' + (d.errCode||d.msg||'未知') + '），请刷新重试';
      btn.disabled = false;
    }
  })
  .catch(function(err) {
    msg.textContent = '网络错误: ' + err;
    if (pyBridge) pyBridge.onError(-1, String(err));
    btn.disabled = false;
  });
}

function refreshCaptcha() {
  const msg = document.getElementById('msg');
  msg.style.color = '#666';
  msg.textContent = '正在刷新挑战...';
  if (pyBridge && pyBridge.onRefresh) {
    pyBridge.onRefresh();
  } else {
    location.reload();
  }
}
</script>
</body>
</html>"""

        html = (
            html.replace("__IMG_URL__", img_url)
            .replace("__POW_PREFIX__", pow_prefix)
            .replace("__POW_MD5__", pow_md5)
            .replace("__SESS__", sess)
        )
        self._web.setHtml(html, QUrl("https://turing.captcha.gtimg.com/"))

    def refresh_captcha(self):
        self.set_status("正在刷新验证码挑战...")
        try:
            new_data = _get_captcha_prehandle()
            self._data = new_data
            self._load(new_data)
        except Exception as e:
            self.set_status("刷新失败：%s" % e)

    def on_captcha_done(self, ticket: str, randstr: str):
        self.set_status("正在发送验证码...")
        try:
            result = _send_sms_code(self._phone_number, ticket, randstr)
            code = result.get("code", -1)
            msg = result.get("msg", "")
            if code == 0 or msg in ("ok", "success", ""):
                self.result_success = True
                self.result_message = "验证码已发送"
                self.accept()
            else:
                self.result_success = False
                self.result_message = "发送失败：%s" % result
                self.set_status(self.result_message)
        except Exception as e:
            self.result_success = False
            self.result_message = "请求异常：%s" % e
            self.set_status(self.result_message)


def request_sms_code_with_captcha(phone_number: str, parent=None):
    if not phone_number:
        return False, "请先输入手机号"
    if not phone_number.isdigit() or len(phone_number) != 11:
        return False, "手机号格式不正确"

    os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--no-sandbox")
    os.environ.setdefault("QTWEBENGINE_DISABLE_SANDBOX", "1")

    try:
        data = _get_captcha_prehandle()
    except Exception as e:
        return False, "获取验证码挑战失败：%s" % e

    dialog = CaptchaSmsDialog(phone_number, data, parent=parent)
    dialog.exec_()
    if dialog.result_success:
        return True, dialog.result_message
    return False, dialog.result_message or "已取消或发送失败"
