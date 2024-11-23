from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QMenu, QVBoxLayout, QWidget
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QSize
import sys


class SnippingTool(QMainWindow):
    """
    Main Snipping Tool Application Window
    """
    def __init__(self):
        super().__init__()
        self.__init_ui()

    def __init_ui(self) -> None:
        """
        Initialize the main window and toolbar.
        """
        self.setWindowTitle("Snipping Tool")
        self.setWindowIcon(QIcon("../assets/icons/logo.jpg"))
        # self.setMinimumSize(600, 200)
        self.setGeometry(200, 200, 540, 200)  # Width x Height
        self.__create_toolbar()

        #set background to dark mode
        self.setStyleSheet("background-color: #2e2e2e; color: #ffffff;")

    def __create_toolbar(self) -> None:
        """
        Create the toolbar with all required buttons and layouts.
        """
        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
         # Style toolbar buttons
        toolbar.setStyleSheet("""
            QToolBar {
                spacing: 10px;  /* Add spacing between buttons */
            }
            QToolButton {
                width: 60px;  /* Set button width */
                margin: 1px;  /* Add margin around buttons */
            }
            QToolButton: hover {
                background-color: #b8b7b4;
                border: 1px solid #7e7e7e
            }
            QToolButton: pressed {
                background-color: #b8b7b4;
            
            }
        """)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        self.addToolBar(toolbar)
        # New Button
        new_action = QAction("+ New", self)
        #new_action.setIcon(QIcon("icons/scissors_1.png"))  # Replace with your icon path
        new_action.triggered.connect(self.__new_snip)
        toolbar.addAction(new_action)
        
        #add Separator
        toolbar.addSeparator()

        # Snip Button
        snip_action = QAction(QIcon("../assets/icons/camera_2.svg"), "Snip", self)
        snip_action.setStatusTip("Capture a screenshot")
        snip_action.triggered.connect(self.__snip_screen)
        toolbar.addAction(snip_action)

        #add Separator
        toolbar.addSeparator()

        # Record Button
        record_action = QAction(QIcon("../assets/icons/camera-video.svg"), "Record", self)
        record_action.setStatusTip("Record the screen")
        record_action.triggered.connect(self.__record_screen)
        toolbar.addAction(record_action)

        #add Separator
        toolbar.addSeparator()

        # Mode Dropdown Button
        mode_menu = QMenu("Mode", self)
        rectangle_action = QAction(QIcon("../assets/icons/rectangle.svg"), "Rectangle", self)
        rectangle_action.triggered.connect(self.__rectangle_mode)

        window_action = QAction(QIcon("../assets/icons/rectangle.png"), "Window", self)
        window_action.triggered.connect(self.__window_mode)

        fullscreen_action = QAction(QIcon("../assets/icons/rectangle.png"), "Full Screen", self)
        fullscreen_action.triggered.connect(self.__fullscreen_mode)

        freeform_action = QAction(QIcon("../assets/icons/rectangle.png"), "Freeform", self)
        freeform_action.triggered.connect(self.__freeform_mode)

        mode_menu.addAction(rectangle_action)
        mode_menu.addAction(window_action)
        mode_menu.addAction(fullscreen_action)
        mode_menu.addAction(freeform_action)


        mode_action = QAction(QIcon("../assets/icons/rectangle.svg"), "Mode", self)
        mode_action.setMenu(mode_menu)
        toolbar.addAction(mode_action)

        #add Separator
        toolbar.addSeparator()

        # Clock Dropdown Button
        clock_menu = QMenu("Clock", self)
        nodelay_action = QAction(QIcon("../assets/icons/clock.svg"), "No delay", self)
        nodelay_action.triggered.connect(self.__nodelay_mode)

        delay3_action = QAction(QIcon("../assets/icons/clock.svg"), "3s delay", self)
        delay3_action.triggered.connect(self.__delay3s_mode)

        delay5_action = QAction(QIcon("../assets/icons/clock.svg"), "5s delay", self)
        delay5_action.triggered.connect(self.__delay5s_mode)

        delay10_action = QAction(QIcon("../assets/icons/clock.svg"), "10s delay", self)
        delay10_action.triggered.connect(self.__delay10s_mode)

        clock_menu.addAction(nodelay_action)
        clock_menu.addAction(delay3_action)
        clock_menu.addAction(delay5_action)
        clock_menu.addAction(delay10_action)


        clock_action = QAction(QIcon("../assets/icons/clock.svg"), "Clock", self)
        clock_action.setMenu(clock_menu)
        toolbar.addAction(clock_action)

        #add Separator
        toolbar.addSeparator()

        # More Dropdown Button
        more_menu = QMenu("More", self)
        # save_action = QAction(QIcon("icons/clock.svg"), "No delay", self)
        # save_action.triggered.connect(self.__nodelay_mode)

        # clound_action = QAction(QIcon("icons/clock.svg"), "3s delay", self)
        # clound_action.triggered.connect(self.__delay3s_mode)

        # clock_menu.addAction(nodelay_action)
        # clock_menu.addAction(delay3_action)
        # clock_menu.addAction(delay5_action)
        # clock_menu.addAction(delay10_action)


        more_action = QAction(QIcon("icons/open-menu.svg"), "More", self)
        more_action.setMenu(more_menu)
        toolbar.addAction(more_action)

    def __new_snip(self) -> None:
        """
        Action for 'New' button.
        """
        print("New snip triggered")

    def __snip_screen(self) -> None:
        """
        Action for 'Snip' button.
        """
        print("Snip screen triggered")

    def __record_screen(self) -> None:
        """
        Action for 'Record' button.
        """
        print("Record screen triggered")

    def __rectangle_mode(self) -> None:
        """
        Action for 'Rectangle Mode' button.
        """
        print("Rectangle mode triggered")

    def __window_mode(self) -> None:
        """
        Action for 'Window Mode' button.
        """
        print("Window mode triggered")
    
    def __fullscreen_mode(self) -> None:
        """
        Action for 'Fullscreen Mode' button.
        """
        print("Fullscreen mode triggered")
    
    def __freeform_mode(self) -> None:
        """
        Action for 'Freeform Mode' button.
        """
        print("Freeform mode triggered")
    
    def __nodelay_mode(self) -> None:
        """
        Action for 'No Delay' button.
        """
        print("No delay mode triggered")
    
    def __delay3s_mode(self) -> None:
        """
        Action for '3s Delay' button.
        """
        print("3s delay mode triggered")
    
    def __delay5s_mode(self) -> None:
        """
        Action for '5s Delay' button.
        """
        print("5s delay mode triggered")

    def __delay10s_mode(self) -> None:
        """
        Action for '10s Delay' button.
        """
        print("10s delay mode triggered")
    
    


def main() -> None:
    """
    Main function to run the Snipping Tool application.
    """
    app = QApplication(sys.argv)
    window = SnippingTool()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
