import sys
from qt_compat import (
    Qt, QTimer, QPoint, QRectF,
    QPainter, QColor, QFont, QPainterPath, QPen,
    QWidget, QLabel, QVBoxLayout
)

class SpeechBubble(QWidget):
    """
    跟随桌宠头顶的漫画风格对话气泡
    """
    def __init__(self, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        if hasattr(Qt, 'WA_MacAlwaysShowToolWindow'):
            self.setAttribute(Qt.WA_MacAlwaysShowToolWindow, True)

        self.label = QLabel(self)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)
        font = QFont("PingFang SC", 10, QFont.Bold)
        font.setStyleHint(QFont.SansSerif)
        self.label.setFont(font)
        self.label.setStyleSheet("color: #1A1A1A; background: transparent; padding: 4px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 18)  # 底部留出空间给气泡小尾巴
        layout.addWidget(self.label)

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)

        self.current_text = ""

    def show_message(self, text, pet_rect, duration_ms=3200):
        self.current_text = text
        self.label.setText(text)
        self.adjustSize()
        self.update_position(pet_rect)
        self.show()
        self.update()
        self.hide_timer.start(duration_ms)

    def update_position(self, pet_rect):
        """保持在桌宠头顶正上方居中，防止出界"""
        bw = self.width()
        bh = self.height()
        bx = pet_rect.x() + (pet_rect.width() - bw) // 2
        by = pet_rect.y() - bh + 12

        # 屏幕边界保护
        from qt_compat import QApplication
        if QApplication.primaryScreen():
            screen = QApplication.primaryScreen().geometry()
            bx = max(screen.left() + 8, min(bx, screen.right() - bw - 8))
            by = max(screen.top() + 8, by)

        self.move(bx, by)

    def paintEvent(self, event):
        if not self.current_text:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        w = self.width()
        h = self.height()
        tail_h = 10
        body_h = h - tail_h

        # 绘制气泡主体路径
        path = QPainterPath()
        path.addRoundedRect(QRectF(2, 2, w - 4, body_h - 4), 12, 12)

        # 气泡下方向下指向的小三角（尾巴）
        mid_x = w / 2
        tail_path = QPainterPath()
        tail_path.moveTo(mid_x - 7, body_h - 3)
        tail_path.lineTo(mid_x, h - 2)
        tail_path.lineTo(mid_x + 7, body_h - 3)
        path = path.united(tail_path)

        # 浅阴影
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 30))
        painter.drawPath(path.translated(2, 2))

        # 白色气泡填充与边框
        painter.setBrush(QColor(255, 255, 255, 245))
        painter.setPen(QPen(QColor(40, 40, 40, 230), 2))
        painter.drawPath(path)
