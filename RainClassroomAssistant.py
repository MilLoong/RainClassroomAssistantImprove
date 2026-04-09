import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from UI.MainWindow import MainWindow_Ui

def _configure_qt_runtime():
    # WSL + pip 安装的 PyQt5 在 conda 环境中通常需要补齐运行时变量。
    is_wsl = "microsoft" in os.uname().release.lower() if hasattr(os, "uname") else False
    env_prefix = os.path.dirname(os.path.dirname(sys.executable))
    env_lib_dir = os.path.join(env_prefix, "lib")

    if os.path.isdir(env_lib_dir):
        current_ld_library_path = os.environ.get("LD_LIBRARY_PATH", "")
        if env_lib_dir not in current_ld_library_path.split(":"):
            os.environ["LD_LIBRARY_PATH"] = (
                env_lib_dir if not current_ld_library_path
                else env_lib_dir + ":" + current_ld_library_path
            )
    # 后续可以直接删去，如果不在 WSL 调试
    if is_wsl:
        wslg_runtime_dir = "/mnt/wslg/runtime-dir"
        wayland_display = os.environ.get("WAYLAND_DISPLAY", "wayland-0")
        wayland_socket = os.path.join(wslg_runtime_dir, wayland_display)

        if os.path.exists(wayland_socket):
            os.environ["QT_QPA_PLATFORM"] = "wayland"
            os.environ["WAYLAND_DISPLAY"] = wayland_display
            os.environ["XDG_RUNTIME_DIR"] = wslg_runtime_dir
        elif os.environ.get("DISPLAY"):
            os.environ["QT_QPA_PLATFORM"] = "xcb"

_configure_qt_runtime()

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts, True)
if sys.platform != "win32":
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

def _configure_ui_fonts(app):
    font_db = QtGui.QFontDatabase()
    candidate_font_files = [
        "/mnt/c/Windows/Fonts/msyh.ttc",
        "/mnt/c/Windows/Fonts/msyhbd.ttc",
        "/mnt/c/Windows/Fonts/msyhui.ttc",
        "/mnt/c/Windows/Fonts/simhei.ttf",
    ]
    for font_file in candidate_font_files:
        if os.path.exists(font_file):
            font_db.addApplicationFont(font_file)

    preferred_ui_families = [
        "Microsoft YaHei UI",
        "Microsoft YaHei",
        "Noto Sans CJK SC",
        "WenQuanYi Micro Hei",
        "SimHei",
        "Arial Unicode MS",
        "DejaVu Sans",
        "Sans Serif",
    ]
    available_families = set(font_db.families())
    chosen_family = next(
        (family for family in preferred_ui_families if family in available_families),
        app.font().family()
    )
    os.environ["RAINCLASSROOM_UI_FONT"] = chosen_family
    os.environ["RAINCLASSROOM_TITLE_FONT"] = chosen_family

    app_font = app.font()
    app_font.setFamily(chosen_family)
    app.setFont(app_font)

if __name__ == "__main__":
    # 初始化
    app = QtWidgets.QApplication(sys.argv)
    _configure_ui_fonts(app)
    main = QtWidgets.QMainWindow()
    ui = MainWindow_Ui()
    ui.setupUi(main)
    main.show()
    # 启动监听
    ui.active()
    # 主窗体循环
    app.exec_()
