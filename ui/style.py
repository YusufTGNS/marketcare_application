from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect


C = {
    "bg": "#11161C",
    "sidebar": "#182127",
    "card": "#1A242C",
    "border": "#2B3943",
    "accent": "#F4B942",
    "accent2": "#4FA36C",
    "success": "#63B77C",
    "warning": "#F0A93E",
    "danger": "#D95C54",
    "text": "#F2F0EA",
    "text_sub": "#C9C1B3",
    "text_dim": "#8E9AA3",
    "row_alt": "#202B34",
    "row_sel": "#23362B",
    "input_bg": "#131C22",
}


def card_ss():
    return f"""
        background:{C['card']};
        border:1px solid {C['border']};
        border-radius:14px;
    """


def btn_primary_ss():
    return f"""
        QPushButton{{
            background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {C['accent2']},stop:1 {C['accent']});
            color:#fff;border:none;border-radius:10px;
            padding:10px 20px;font-size:13px;font-weight:700;
        }}
        QPushButton:hover{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 {C['accent2']},stop:1 #F7B955);}}
        QPushButton:pressed{{background:{C['accent2']};}}
    """


def btn_success_ss():
    return f"""
        QPushButton{{background:{C['success']};color:#fff;border:none;
            border-radius:10px;padding:10px 20px;font-size:13px;font-weight:700;}}
        QPushButton:hover{{background:#62AD72;}}
    """


def btn_danger_ss():
    return f"""
        QPushButton{{background:{C['danger']};color:#fff;border:none;
            border-radius:10px;padding:10px 20px;font-size:13px;font-weight:700;}}
        QPushButton:hover{{background:#D85A4C;}}
    """


def input_ss():
    return f"""
        QLineEdit,QSpinBox,QDoubleSpinBox,QDateEdit{{
            background:{C['input_bg']};color:{C['text']};
            border:1px solid {C['border']};border-radius:10px;
            padding:8px 10px;font-size:13px;
        }}
        QLineEdit:focus,QSpinBox:focus,QDoubleSpinBox:focus,QDateEdit:focus{{
            border:1.5px solid {C['accent']};
        }}
        QSpinBox::up-button,QSpinBox::down-button,
        QDoubleSpinBox::up-button,QDoubleSpinBox::down-button{{
            background:#24313A;width:18px;border-radius:4px;
        }}
        QDateEdit::drop-down{{background:#24313A;width:22px;border-radius:4px;}}
    """


TABLE_SS = f"""
    QTableWidget{{
        background:{C['card']};color:{C['text']};border:none;
        gridline-color:{C['border']};font-size:13px;
        selection-background-color:{C['row_sel']};outline:none;
        alternate-background-color:{C['row_alt']};
    }}
    QTableWidget::item{{padding:9px 13px;border-bottom:1px solid {C['border']};}}
    QTableWidget::item:selected{{background:{C['row_sel']};color:{C['accent2']};}}
    QHeaderView::section{{
        background:{C['sidebar']};color:{C['accent']};
        padding:9px 13px;border:none;
        border-bottom:2px solid {C['accent']};
        font-size:11px;font-weight:700;letter-spacing:0.8px;
    }}
    QScrollBar:vertical{{background:{C['bg']};width:8px;border-radius:4px;}}
    QScrollBar::handle:vertical{{background:#3A4A55;border-radius:4px;min-height:20px;}}
    QScrollBar::handle:vertical:hover{{background:{C['accent']};}}
    QScrollBar::horizontal{{background:{C['bg']};height:8px;border-radius:4px;}}
    QScrollBar::handle:horizontal{{background:#3A4A55;border-radius:4px;}}
"""


def shadow(widget, blur=18, dy=4):
    fx = QGraphicsDropShadowEffect(widget)
    fx.setBlurRadius(blur)
    fx.setColor(QColor(0, 0, 0, 90))
    fx.setOffset(0, dy)
    widget.setGraphicsEffect(fx)
