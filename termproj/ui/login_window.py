# ui/login_window.py
"""
LoginWindow provides the user authentication interface.
On successful login, it notifies the mediator to open the main dashboard.
It now also offers a password recovery option.
"""
from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from patterns.singleton import UserSessionSingleton

class PasswordRecoveryDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Recover Password")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Email input
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)

        # Fixed security questions and answer fields
        self.q1_label = QLabel("Security Question 1: Where were you born?")
        self.a1_input = QLineEdit()
        self.a1_input.setPlaceholderText("Answer")
        layout.addWidget(self.q1_label)
        layout.addWidget(self.a1_input)

        self.q2_label = QLabel("Security Question 2: What is your favorite pet's name?")
        self.a2_input = QLineEdit()
        self.a2_input.setPlaceholderText("Answer")
        layout.addWidget(self.q2_label)
        layout.addWidget(self.a2_input)

        self.q3_label = QLabel("Security Question 3: What is your mother's maiden name?")
        self.a3_input = QLineEdit()
        self.a3_input.setPlaceholderText("Answer")
        layout.addWidget(self.q3_label)
        layout.addWidget(self.a3_input)

        # New Password input
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("Enter new password")
        self.new_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("New Password:"))
        layout.addWidget(self.new_password_input)

        # Recover button
        self.recover_btn = QPushButton("Recover Password")
        self.recover_btn.clicked.connect(self.handle_recover)
        layout.addWidget(self.recover_btn)

    def handle_recover(self):
        email = self.email_input.text().strip()
        a1 = self.a1_input.text().strip()
        a2 = self.a2_input.text().strip()
        a3 = self.a3_input.text().strip()
        new_password = self.new_password_input.text().strip()

        if not email or not a1 or not a2 or not a3 or not new_password:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        user = self.db_manager.get_user_by_email(email)
        if not user:
            QMessageBox.critical(self, "Error", "Email not registered.")
            return

        # Verify answers (case-insensitive)
        if (a1.lower() == user["security_a1"].strip().lower() and
            a2.lower() == user["security_a2"].strip().lower() and
            a3.lower() == user["security_a3"].strip().lower()):
            self.db_manager.update_user_password(user["user_id"], new_password)
            QMessageBox.information(self, "Success", "Password updated successfully.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "One or more answers are incorrect.")

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

        recover_btn = QPushButton("Forgot Password?")
        recover_btn.clicked.connect(self.show_recover_dialog)

        layout.addWidget(self.status_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_btn)
        layout.addWidget(register_btn)
        layout.addWidget(recover_btn)

        self.setCentralWidget(central_widget)
        self.resize(300, 250)

    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        user_data = self.db_manager.get_user_by_email_and_password(email, password)
        if user_data:
            # Set the session via the Singleton (assuming user_data now includes "name")
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

    def show_recover_dialog(self):
        # Open the password recovery dialog
        from PyQt5.QtWidgets import QDialog
        dialog = PasswordRecoveryDialog(self.db_manager, self)
        dialog.exec_()

