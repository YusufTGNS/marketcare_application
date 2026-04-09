from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect


C = {
    "bg": "#0F172A",
    "bg_soft": "#162033",
    "sidebar": "#0B1220",
    "card": "#111C31",
    "card_soft": "#15233D",
    "border": "#233554",
    "border_soft": "#344866",
    "accent": "#38BDF8",
    "accent2": "#2563EB",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "text": "#E5EEF9",
    "text_sub": "#B7C6DD",
    "text_dim": "#7F93B3",
    "row_alt": "#132039",
    "row_sel": "#162744",
    "input_bg": "#0C1628",
}


def card_ss():
    return f"""
        background:{C['card']};
        border:1px solid {C['border_soft']};
        border-radius:20px;
    """


def btn_primary_ss():
    return f"""
        QPushButton{{
            background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {C['accent2']},stop:1 {C['accent']});
            color:#F8FBFF;border:none;border-radius:12px;
            padding:11px 20px;font-size:13px;font-weight:800;
        }}
        QPushButton:hover{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 #2B6EF3,stop:1 #5AC8FA);}}
        QPushButton:pressed{{background:{C['accent2']};}}
        QPushButton:disabled{{background:#334155;color:#94A3B8;}}
    """


def btn_success_ss():
    return f"""
        QPushButton{{
            background:{C['success']};color:#F8FBFF;border:none;
            border-radius:12px;padding:11px 20px;font-size:13px;font-weight:800;
        }}
        QPushButton:hover{{background:#28B863;}}
        QPushButton:disabled{{background:#334155;color:#94A3B8;}}
    """


def btn_danger_ss():
    return f"""
        QPushButton{{
            background:{C['danger']};color:#F8FBFF;border:none;
            border-radius:12px;padding:11px 20px;font-size:13px;font-weight:800;
        }}
        QPushButton:hover{{background:#DC3D3D;}}
        QPushButton:disabled{{background:#334155;color:#94A3B8;}}
    """


def combo_ss():
    return f"""
        QComboBox {{
            background:{C['input_bg']};
            color:{C['text']};
            border:1px solid {C['border_soft']};
            border-radius:14px;
            padding:8px 12px;
            font-size:13px;
            min-height:20px;
        }}
        QComboBox:hover {{
            border:1px solid {C['border']};
            background:{C['bg_soft']};
        }}
        QComboBox::drop-down {{
            background:#21304A;
            width:24px;
            border-top-right-radius:12px;
            border-bottom-right-radius:12px;
        }}
    """


def info_box_ss(accent: str | None = None):
    border_color = accent or C["border_soft"]
    return (
        f"background:rgba(255,255,255,0.035);color:{C['text_sub']};"
        f"border:1px solid {border_color};border-radius:16px;padding:10px 12px;"
    )


def input_ss():
    return f"""
        QLineEdit,QSpinBox,QDoubleSpinBox,QDateEdit{{
            background:{C['input_bg']};color:{C['text']};
            border:1px solid {C['border_soft']};border-radius:14px;
            padding:10px 13px;font-size:13px;
        }}
        QLineEdit:focus,QSpinBox:focus,QDoubleSpinBox:focus,QDateEdit:focus{{
            border:1.5px solid {C['accent']};
            background:{C['bg_soft']};
        }}
        QSpinBox::up-button,QSpinBox::down-button,
        QDoubleSpinBox::up-button,QDoubleSpinBox::down-button{{
            background:#21304A;width:18px;border-radius:4px;
        }}
        QDateEdit::drop-down{{background:#21304A;width:22px;border-radius:4px;}}
    """


TABLE_SS = f"""
    QTableWidget{{
        background:{C['card']};color:{C['text']};border:none;
        gridline-color:{C['border_soft']};font-size:13px;
        selection-background-color:{C['row_sel']};outline:none;
        alternate-background-color:{C['row_alt']};
        border-radius:16px;
    }}
    QTableWidget::item{{padding:10px 13px;border-bottom:1px solid {C['border_soft']};}}
    QTableWidget::item:selected{{background:{C['row_sel']};color:#DFF4FF;}}
    QHeaderView::section{{
        background:{C['sidebar']};color:{C['accent']};
        padding:10px 13px;border:none;
        border-bottom:1px solid {C['border_soft']};
        font-size:11px;font-weight:800;letter-spacing:0.7px;
    }}
    QScrollBar:vertical{{background:{C['bg']};width:8px;border-radius:4px;}}
    QScrollBar::handle:vertical{{background:#405777;border-radius:4px;min-height:20px;}}
    QScrollBar::handle:vertical:hover{{background:{C['accent']};}}
    QScrollBar:horizontal{{background:{C['bg']};height:8px;border-radius:4px;}}
    QScrollBar::handle:horizontal{{background:#405777;border-radius:4px;}}
"""


def shadow(widget, blur=22, dy=6):
    fx = QGraphicsDropShadowEffect(widget)
    fx.setBlurRadius(blur)
    fx.setColor(QColor(2, 6, 23, 140))
    fx.setOffset(0, dy)
    widget.setGraphicsEffect(fx)
