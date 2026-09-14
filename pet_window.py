import os
import random
from qt_compat import (
    Qt, QTimer, QPoint, QRect,
    QPixmap, QTransform, QCursor,
    QWidget, QLabel, QMenu, QAction, QApplication
)

from pet_state import StateManager, PetState, GRUMPY_LINES, CUTE_LINES
from bubble import SpeechBubble

class PetWindow(QWidget):
    def __init__(self, assets_dir):
        super().__init__()
        self.assets_dir = assets_dir
        self.manager = StateManager()

        # 窗口属性：无边框、背景完全透明、独立置顶窗口（Mac/Win 通用，永不后台休眠隐藏）
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        if hasattr(Qt, 'WA_MacAlwaysShowToolWindow'):
            self.setAttribute(Qt.WA_MacAlwaysShowToolWindow, True)
        self.is_stay_on_top = True

        # 缩放比例与尺寸 (默认 0.75 精致比例，尺寸 135x180，小巧灵动)
        self.scale_factor = 0.75
        self.base_width = 180
        self.base_height = 240
        self.cur_width = int(self.base_width * self.scale_factor)
        self.cur_height = int(self.base_height * self.scale_factor)
        self.resize(self.cur_width, self.cur_height)

        # 宠物显示 Label
        self.image_label = QLabel(self)
        self.image_label.setGeometry(0, 0, self.cur_width, self.cur_height)
        self.image_label.setScaledContents(True)

        # 气泡对话框
        self.bubble = SpeechBubble()

        # 加载素材帧
        self.frames = {}
        self.load_all_assets()

        # 当前帧索引
        self.frame_index = 0

        # 拖拽状态变量
        self.is_dragging = False
        self.drag_start_pos = QPoint()
        self.mouse_press_pos = QPoint()

        # 定时器 1：动画帧循环播放 (160ms/帧)
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation_frame)
        self.anim_timer.start(160)

        # 定时器 2：移动与游走物理计算 (40ms/步)
        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.update_movement)
        self.move_timer.start(40)

        # 定时器 3：状态自动决策 (每 3~5 秒一次随机判定)
        self.ai_timer = QTimer(self)
        self.ai_timer.timeout.connect(self.update_ai_decision)
        self.ai_timer.start(3500)

        # 初始化起始位置（屏幕右下角靠近任务栏上方）
        self.init_position()
        self.update_animation_frame()

        # 依琳专属：软件启动 800ms 后弹出甜蜜表白惊喜
        QTimer.singleShot(800, self.trigger_confession)

    def trigger_confession(self):
        """依琳专属表白：动作切换为甜美卖萌，气泡停留 6 秒"""
        state, line = self.manager.get_confession()
        self.bubble.show_message(line, self.geometry(), 6000)

    def init_position(self):
        screen = QApplication.primaryScreen().availableGeometry()
        init_x = screen.right() - self.cur_width - 150
        init_y = screen.bottom() - self.cur_height - 20
        self.move(init_x, init_y)
        self.set_stay_on_top(True)

    def set_stay_on_top(self, enable=True):
        self.is_stay_on_top = enable
        self.setWindowFlag(Qt.WindowStaysOnTopHint, enable)
        self.show()
        try:
            import win32gui, win32con
            hwnd = int(self.winId())
            flag = win32con.HWND_TOPMOST if enable else win32con.HWND_NOTOPMOST
            win32gui.SetWindowPos(
                hwnd, flag, 0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW
            )
        except Exception:
            pass

    def load_all_assets(self):
        """加载所有动作分类下的图片"""
        states = [PetState.IDLE, PetState.WALK, PetState.CUTE, PetState.MIDDLE_FINGER, PetState.DRAG]
        for st in states:
            folder = os.path.join(self.assets_dir, st)
            self.frames[st] = []
            if os.path.exists(folder):
                files = sorted([f for f in os.listdir(folder) if f.endswith(".png")])
                for f in files:
                    pix = QPixmap(os.path.join(folder, f))
                    self.frames[st].append(pix)

    def set_scale(self, scale):
        self.scale_factor = scale
        self.cur_width = int(self.base_width * self.scale_factor)
        self.cur_height = int(self.base_height * self.scale_factor)
        self.resize(self.cur_width, self.cur_height)
        self.image_label.setGeometry(0, 0, self.cur_width, self.cur_height)
        self.update_animation_frame()
        self.bubble.update_position(self.geometry())

    def update_animation_frame(self):
        current_state = self.manager.state
        state_frames = self.frames.get(current_state, [])
        if not state_frames:
            state_frames = self.frames.get(PetState.IDLE, [])

        if not state_frames:
            return

        self.frame_index = (self.frame_index + 1) % len(state_frames)
        pix = state_frames[self.frame_index]

        # 始终保持正面朝向用户，不进行镜像翻转
        self.image_label.setPixmap(pix)

    def update_movement(self):
        if self.is_dragging:
            return

        if self.manager.state == PetState.WALK:
            screen = QApplication.primaryScreen().availableGeometry()
            step_speed = 3
            next_x = self.x() + self.manager.direction * step_speed

            # 屏幕边缘碰壁掉头检测
            if next_x <= screen.left():
                next_x = screen.left()
                self.manager.direction = 1
            elif next_x + self.cur_width >= screen.right():
                next_x = screen.right() - self.cur_width
                self.manager.direction = -1

            self.move(next_x, self.y())
            if self.bubble.isVisible():
                self.bubble.update_position(self.geometry())

    def update_ai_decision(self):
        """定期随机做动作决策"""
        if self.is_dragging:
            return

        old_state = self.manager.state
        new_state = self.manager.decide_next_roam()

        # 如果刚刚随机触发了“无缘无故比中指”彩蛋
        if new_state == PetState.MIDDLE_FINGER and old_state != PetState.MIDDLE_FINGER:
            line = random.choice(GRUMPY_LINES)
            self.bubble.show_message(line, self.geometry(), 3000)
        elif new_state == PetState.CUTE and old_state != PetState.CUTE:
            line = random.choice(CUTE_LINES)
            self.bubble.show_message(line, self.geometry(), 2800)

        # 重置决策计时器（随机 3~6 秒浮动，更具生命感）
        self.ai_timer.setInterval(random.randint(3000, 6000))

    # ---- 鼠标事件处理 ----
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.globalPos() - self.frameGeometry().topLeft()
            self.mouse_press_pos = event.globalPos()
            self.is_dragging = False
            event.accept()
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPos())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            # 移动距离超过 6 像素才认定为拖拽，防止单击误判
            dist = (event.globalPos() - self.mouse_press_pos).manhattanLength()
            if dist > 6:
                if not self.is_dragging:
                    self.is_dragging = True
                    drag_line = self.manager.start_drag()
                    self.bubble.show_message(drag_line, self.geometry(), 2000)

                self.move(event.globalPos() - self.drag_start_pos)
                self.bubble.update_position(self.geometry())
                event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.is_dragging:
                # 拖拽结束
                self.is_dragging = False
                self.manager.stop_drag()
                # 确保不被拖出屏幕外
                self.clamp_to_screen()
            else:
                # 单击触发互动（支持狂点暴怒逻辑）
                action_state, line = self.manager.register_click()
                self.bubble.show_message(line, self.geometry(), 3200)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        """双击 Kitty：直接触发专属表白"""
        if event.button() == Qt.LeftButton:
            self.trigger_confession()
            event.accept()

    def clamp_to_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        x = max(screen.left(), min(self.x(), screen.right() - self.cur_width))
        y = max(screen.top(), min(self.y(), screen.bottom() - self.cur_height))
        self.move(x, y)
        self.bubble.update_position(self.geometry())

    # ---- 右键菜单 ----
    def show_context_menu(self, global_pos):
        menu = QMenu(self)
        menu_style = """
            QMenu {
                background-color: #1A1A22;
                border: 1.5px solid #383846;
                border-radius: 14px;
                padding: 8px 6px;
                font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
                font-size: 15px;
                font-weight: 500;
            }
            QMenu::item {
                color: #F0F0F6;
                padding: 10px 24px 10px 18px;
                margin: 3px 4px;
                border-radius: 8px;
                min-width: 190px;
            }
            QMenu::item:selected {
                background-color: #2D2D3A;
                color: #FF5E8A;
                font-weight: 600;
            }
            QMenu::separator {
                height: 1px;
                background-color: #2E2E3A;
                margin: 6px 12px;
            }
            QMenu::right-arrow {
                margin-right: 12px;
            }
        """
        menu.setStyleSheet(menu_style)

        # 0. 依琳专属表白（置顶显式入口）
        confess_act = menu.addAction("💌 依琳专属悄悄话")
        confess_act.triggered.connect(self.trigger_confession)
        menu.addSeparator()

        # 1. 动作强切子菜单
        act_menu = menu.addMenu("🎀 切换动作")
        act_menu.setStyleSheet(menu_style)

        act_walk = act_menu.addAction("🐾 到处溜达 (漫步)")
        act_walk.triggered.connect(lambda: self.manager.set_state(PetState.WALK, lock_duration=6.0))

        act_cute = act_menu.addAction("✨ 甜美卖萌")
        act_cute.triggered.connect(self.trigger_cute)

        act_grumpy = act_menu.addAction("🖕 暴躁中指！")
        act_grumpy.triggered.connect(self.trigger_middle_finger)

        act_idle = act_menu.addAction("😴 原地发呆")
        act_idle.triggered.connect(lambda: self.manager.set_state(PetState.IDLE, lock_duration=4.0))

        menu.addSeparator()

        # 2. 自由漫步开关（显式展示开启/关闭状态）
        roam_text = "🚶 自动漫步  【已开启 ✔】" if self.manager.auto_roam else "🚶 自动漫步  【已关闭 ✖】"
        roam_act = menu.addAction(roam_text)
        roam_act.triggered.connect(self.toggle_auto_roam)

        # 3. 窗口置顶开关（显式展示开启/关闭状态）
        top_text = "📌 窗口置顶  【已开启 ✔】" if self.is_stay_on_top else "📌 窗口置顶  【已关闭 ✖】"
        ontop_act = menu.addAction(top_text)
        ontop_act.triggered.connect(self.toggle_stay_on_top)

        menu.addSeparator()

        # 4. 尺寸调节
        size_menu = menu.addMenu("🔍 调整大小")
        size_menu.setStyleSheet(menu_style)
        for scale, label in [
            (0.6, "60%   (迷你玩偶)"),
            (0.75, "75%   (精致推荐)"),
            (1.0, "100% (标准原图)"),
            (1.25, "125% (稍大显眼)"),
            (1.5, "150% (超大玩偶)")
        ]:
            action = size_menu.addAction(label)
            action.triggered.connect(lambda checked, s=scale: self.set_scale(s))

        menu.addSeparator()

        # 5. 退出
        exit_act = menu.addAction("❌ 退出桌宠")
        exit_act.triggered.connect(self.close_pet)

        menu.exec_(global_pos)

    def trigger_cute(self):
        self.manager.set_state(PetState.CUTE, lock_duration=3.0)
        line = random.choice(CUTE_LINES)
        self.bubble.show_message(line, self.geometry(), 3000)

    def trigger_middle_finger(self):
        self.manager.set_state(PetState.MIDDLE_FINGER, lock_duration=3.5)
        line = random.choice(GRUMPY_LINES)
        self.bubble.show_message(line, self.geometry(), 3500)

    def toggle_auto_roam(self):
        self.manager.auto_roam = not self.manager.auto_roam
        if self.manager.auto_roam:
            self.manager.set_state(PetState.WALK)
            self.bubble.show_message("🐾 自动漫步已开启~ 巡逻出发！", self.geometry(), 2500)
        else:
            self.manager.set_state(PetState.IDLE)
            self.bubble.show_message("⏸️ 自动漫步已暂停，原地歇息~", self.geometry(), 2500)

    def toggle_stay_on_top(self):
        new_val = not self.is_stay_on_top
        self.set_stay_on_top(new_val)
        if new_val:
            self.bubble.show_message("📌 窗口置顶已开启（永不被遮挡）", self.geometry(), 2500)
        else:
            self.bubble.show_message("🔓 窗口置顶已关闭", self.geometry(), 2500)

    def close_pet(self):
        self.bubble.close()
        self.close()
        QApplication.quit()
