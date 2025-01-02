qframe_style: str = """
    QFrame {
        background-color: transparent;
    }
"""

qpushbutton_style: str = """
    QPushButton {
        background-color: #3E3E50; /* Button background for QAction */
        border: none;
        border-radius: 4px; /* Rounded corners */
        padding: 8px; /* Button padding */
        color: #E0E0E0; /* Text color */
        font-size: 16px; /* Text size */
        icon-size: 20px; /* Icon size */
    }
    QPushButton:hover {
        background-color: #ff78b7af; /* Button hover color */
    }
    QPushButton:pressed {
        background-color: #ff78b7af; /* Active/pressed state color */
    }
    QPushButton:checked {
        background-color: #ff78b7af; /* Checked state for toggled actions */
    }   
"""

qtoolbar_style: str = """
    QToolBar {
        background-color: #2C2C3A; /* Toolbar background */
        padding: 8px; /* Toolbar padding */
        border: none; /* Remove default border */
    }
    QToolButton {
        background-color: #3E3E50; /* Button background for QAction */
        border: none;
        border-radius: 4px; /* Rounded corners */
        padding: 8px; /* Button padding */
        color: #E0E0E0; /* Text color */
    }
    QToolButton:hover {
        background-color: #ff78b7af; /* Button hover color */
    }
    QToolButton:pressed {
        background-color: #ff78b7af; /* Active/pressed state color */
    }
    QToolButton:checked {
        background-color: #ff78b7af; /* Checked state for toggled actions */
    }
    QToolButton:disabled {
        background-color: #2C2C3A; /* Disabled actions blend with toolbar */
        color: #707070; /* Dim text for disabled actions */
    }
"""


styles: str = "".join((qframe_style, qpushbutton_style))
