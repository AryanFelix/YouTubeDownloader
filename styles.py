from utils import (PRIMARY_ACCENT, PRIMARY_ACCENT_DARK, PRIMARY_ACCENT_LIGHT,
                   TEXT_HIGH, BG, CARD, BORDER, MUTED)

def textedit_style():
    return f"""
        QTextEdit {{
            background: {CARD};
            color: {TEXT_HIGH};
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 10px;
            font-size: 11pt;
        }}
        QTextEdit:focus {{ border: 1px solid {PRIMARY_ACCENT}; }}
    """

def list_style():
    return f"""
        QListWidget {{
            background: {CARD};
            color: {TEXT_HIGH};
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 6px;
        }}
        QListWidget::item:selected {{ background: rgba(46,135,255,0.12); }}
    """

def log_style():
    return f"""
        QTextEdit {{
            background: #0f1719;
            color: {TEXT_HIGH};
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 10px;
            font-family: monospace;
            font-size: 10pt;
        }}
    """

def primary_button_style(accent: bool = False):
    if accent:
        bg1, bg2 = PRIMARY_ACCENT_DARK, PRIMARY_ACCENT
    else:
        bg1, bg2 = PRIMARY_ACCENT, PRIMARY_ACCENT_DARK
    return f"""
        QPushButton {{ border-radius:8px; padding:10px 14px; color: white; font-weight:700;
                     background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 {bg1}, stop:1 {bg2}); }}
        QPushButton:disabled {{ opacity: 0.6; }}
    """

def secondary_button_style(outline: bool = False):
    if outline:
        return f"""
            QPushButton {{ background: transparent; color: {TEXT_HIGH}; border:1px solid {BORDER}; border-radius:6px; padding:8px 10px; }}
            QPushButton:disabled {{ opacity:0.6; }}
        """
    return f"""
        QPushButton {{ background: #0c1416; color: {TEXT_HIGH}; border:1px solid {BORDER}; border-radius:6px; padding:8px 10px; }}
        QPushButton:disabled {{ opacity:0.6; }}
    """

def progress_style(primary_color: str, chunk_color: str, border: str):
    return f"""
        QProgressBar {{
            border-radius:11px;
            background: rgba(255,255,255,0.02);
            border: 1px solid {border};
            text-align:center;
            color: {TEXT_HIGH};
            padding: 0px;
            min-height: 22px;
        }}
        QProgressBar::chunk {{
            border-radius:11px;
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {chunk_color}, stop:1 {primary_color});
        }}
    """
