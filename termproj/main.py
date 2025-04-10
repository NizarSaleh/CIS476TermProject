# main.py
"""
Entry point for the DriveShare application.
Sets up the QApplication, applies a black & yellow QSS style,
initializes the database, creates the mediator, instantiates
the various UI windows, and shows the login window.
"""
import sys
from PyQt5.QtWidgets import QApplication
from database.db_manager import DBManager
from patterns.mediator import UIMediator
from ui.login_window import LoginWindow
from ui.register_window import RegisterWindow
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    app.setStyleSheet("""
    /* Overall widget styling */
    QWidget {
        background-color: #F7F8FA;  /* Light background */
        color: #333333;             /* Dark text for readability */
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 11pt;
    }

    /* Modern button design */
    QPushButton {
        background-color: #007ACC;  /* Accent blue */
        color: #ffffff;
        border: none;
        border-radius: 4px;
        padding: 10px 15px;
        font-weight: 500;
    }
    QPushButton:hover {
        background-color: #005FA3;
    }
    QPushButton:pressed {
        background-color: #004A82;
    }

    /* Line edit and text edit styling */
    QLineEdit, QTextEdit {
        background-color: #FFFFFF;  /* White inputs */
        border: 1px solid #CCCCCC;
        border-radius: 4px;
        padding: 6px;
    }
    QLineEdit:focus, QTextEdit:focus {
        border: 1px solid #007ACC;  /* Focus color matching buttons */
    }

    /* Label styling */
    QLabel {
        color: #333333;
        font-weight: 400;
    }

    /* Tab widget styling */
    QTabWidget::pane {
        border: 1px solid #CCCCCC;
        background: #FFFFFF;
    }
    QTabBar::tab {
        background: #E9E9E9;
        color: #333333;
        padding: 8px 15px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background: #FFFFFF;
        color: #007ACC;
        border-bottom: 2px solid #007ACC;
    }

    /* List widget styling */
    QListWidget {
        background: #FFFFFF;
        border: 1px solid #CCCCCC;
        border-radius: 4px;
        padding: 4px;
    }
""")


    # Initialize the database and mediator
    db_manager = DBManager("driveshare.db")
    mediator = UIMediator()

    # Create and register the login, register, and main windows
    login_window = LoginWindow(db_manager, mediator)
    register_window = RegisterWindow(db_manager, mediator)
    main_window = MainWindow(db_manager, mediator)

    mediator.register("login_window", login_window)
    mediator.register("register_window", register_window)
    mediator.register("main_window", main_window)

    login_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
