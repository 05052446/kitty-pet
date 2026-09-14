import sys
import os
from qt_compat import (
    QApplication, QSystemTrayIcon, QMenu, QAction,
    QIcon, QCoreApplication, QTimer
)

from pet_window import PetWindow

def main():
    # 启用高 DPI 缩放支持
    QApplication.setAttribute(2, True)  # Qt.AA_EnableHighDpiScaling = 2
    QApplication.setAttribute(10, True) # Qt.AA_UseHighDpiPixmaps = 10

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    if getattr(sys, 'frozen', False):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")

    # 如果素材不存在，自动生成
    if not os.path.exists(assets_dir) or not os.listdir(assets_dir):
        import generate_assets
        generate_assets.ensure_dirs()
        generate_assets.generate_idle()
        generate_assets.generate_walk()
        generate_assets.generate_cute()
        generate_assets.generate_middle_finger()
        generate_assets.generate_drag()

    # 创建桌面宠物主窗口
    pet = PetWindow(assets_dir)
    pet.show()

    # 系统托盘图标
    tray_icon_path = os.path.join(assets_dir, "idle", "idle_0.png")
    tray_icon = None
    if os.path.exists(tray_icon_path):
        tray_icon = QSystemTrayIcon(QIcon(tray_icon_path), app)
        tray_menu = QMenu()

        show_act = QAction("显示/复位桌宠", tray_menu)
        show_act.triggered.connect(lambda: (pet.show(), pet.init_position()))
        tray_menu.addAction(show_act)

        tray_menu.addSeparator()

        exit_act = QAction("退出", tray_menu)
        exit_act.triggered.connect(pet.close_pet)
        tray_menu.addAction(exit_act)

        tray_icon.setContextMenu(tray_menu)
        tray_icon.setToolTip("Hello Kitty 依琳专属桌宠 💕")
        tray_icon.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
