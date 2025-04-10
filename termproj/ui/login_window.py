# ui/login_window.py
"""
LoginWindow provides the user authentication interface.
On successful login, it notifies the mediator to open the main dashboard.
"""
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
from patterns.singleton import UserSessionSingleton

class LoginWindow(QMainWindow):
    def __init__(self, db_manager, mediator):
        super().__init__()
        self.db_manager = db_manager
        self.mediator = mediator
        self.setWindowTitle("DriveShare - Login")
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.status_label = QLabel("")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.handle_login)

        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.show_register_window)

        layout.addWidget(self.status_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_btn)
        layout.addWidget(register_btn)

        self.setCentralWidget(central_widget)
        self.resize(300, 200)

    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        user_data = self.db_manager.get_user_by_email_and_password(email, password)
        if user_data:
            session = UserSessionSingleton.get_instance()
            session.login(user_data["user_id"], user_data["email"], user_data["name"])
            self.status_label.setText("Login successful!")
            self.mediator.send({"type": "LOGIN_SUCCESS", "user_id": user_data["user_id"]}, "login_window")
            self.close()
        else:
            self.status_label.setText("Invalid credentials!")

    def show_register_window(self):
        self.mediator.send({"type": "SHOW_REGISTER"}, "login_window")
        self.close()
