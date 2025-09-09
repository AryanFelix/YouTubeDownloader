from __future__ import annotations
import os
import sys
from PySide6.QtGui import QGuiApplication, QFont, QIcon
from PySide6.QtWidgets import QApplication

try:
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        QGuiApplication.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
except Exception:
    pass

from ui import UXWindow
from utils import APP_LOGO_PATH, BG, TEXT_HIGH

def main():
    app = QApplication(sys.argv)
    if APP_LOGO_PATH and isinstance(APP_LOGO_PATH, str):
        try:
            if os.path.exists(APP_LOGO_PATH):
                app.setWindowIcon(QIcon(APP_LOGO_PATH))
        except Exception:
            pass

    app.setStyleSheet(f"""
        QWidget {{ background: {BG}; color: {TEXT_HIGH}; font-family: 'Segoe UI', 'Helvetica', Arial; }}
        QLabel {{ color: {TEXT_HIGH}; }}
        QPushButton {{ font-size: 10pt; }}
    """)
    app.setFont(QFont("Segoe UI" if sys.platform.startswith("win") else "Sans Serif", 10))

    w = UXWindow()
    try:
        if os.path.exists(APP_LOGO_PATH):
            w.setWindowIcon(QIcon(APP_LOGO_PATH))
    except Exception:
        pass

    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
