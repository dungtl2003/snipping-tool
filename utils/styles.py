qframe_style: str = """
    QFrame {
        background-color: #3f3f3f;
    }
"""

qpushbutton_style: str = """
    QPushButton {
        border-radius: 5px;
        background-color: rgb(60, 90, 255);
        padding: 10px;
        color: white;
        font-weight: bold;
        font-family: Arial;
        font-size: 12px;
    }
    QPushButton::hover {
        background-color: rgb(60, 20, 255)
    }
"""

styles: str = "".join((qframe_style, qpushbutton_style))
