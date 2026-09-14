"""
PyQt5 / PyQt6 跨平台双向兼容垫片
保证在 Windows、Intel Mac、Apple Silicon (M1/M2/M3/M4) Mac 上均可无缝运行
"""

try:
    from PyQt5.QtCore import Qt, QTimer, QPoint, QRect, QRectF, QCoreApplication
    from PyQt5.QtGui import QPixmap, QTransform, QCursor, QIcon, QPainter, QColor, QFont, QPainterPath, QPen
    from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMenu, QAction, QVBoxLayout, QSystemTrayIcon
    IS_QT6 = False
except ImportError:
    from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, QRectF, QCoreApplication
    from PyQt6.QtGui import QPixmap, QTransform, QCursor, QIcon, QPainter, QColor, QFont, QPainterPath, QPen, QAction
    from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QMenu, QVBoxLayout, QSystemTrayIcon
    IS_QT6 = True

    # 兼容 PyQt6 枚举规范
    Qt.FramelessWindowHint = Qt.WindowType.FramelessWindowHint
    Qt.WindowStaysOnTopHint = Qt.WindowType.WindowStaysOnTopHint
    Qt.Tool = Qt.WindowType.Tool
    Qt.WA_TranslucentBackground = Qt.WidgetAttribute.WA_TranslucentBackground
    Qt.WA_DeleteOnClose = Qt.WidgetAttribute.WA_DeleteOnClose
    Qt.WA_ShowWithoutActivating = Qt.WidgetAttribute.WA_ShowWithoutActivating
    Qt.LeftButton = Qt.MouseButton.LeftButton
    Qt.RightButton = Qt.MouseButton.RightButton
    Qt.AlignCenter = Qt.AlignmentFlag.AlignCenter
    Qt.NoPen = Qt.PenStyle.NoPen
    
    # 兼容 exec_ 方法
    if not hasattr(QMenu, "exec_"):
        QMenu.exec_ = QMenu.exec
    if not hasattr(QApplication, "exec_"):
        QApplication.exec_ = QApplication.exec
