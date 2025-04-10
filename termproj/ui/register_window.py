# ui/register_window.py
"""
RegisterWindow provides the user registration interface.
It collects the user's full name, email, password, and answers to three fixed security questions.
"""
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

class RegisterWindow(QMainWindow):
    def __init__(self, db_manager, mediator):
        super().__init__()
        self.db_manager = db_manager
        self.mediator = mediator
        self.setWindowTitle("DriveShare - Register")
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.status_label = QLabel("")
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name")
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        # Fixed security questions (labels) with answer fields.
        self.q1_label = QLabel("Security Question 1: Where were you born?")
        self.a1_input = QLineEdit()
        self.a1_input.setPlaceholderText("Answer")
        
        self.q2_label = QLabel("Security Question 2: What is your favorite pet's name?")
        self.a2_input = QLineEdit()
        self.a2_input.setPlaceholderText("Answer")
        
        self.q3_label = QLabel("Security Question 3: What is your mother's maiden name?")
        self.a3_input = QLineEdit()
        self.a3_input.setPlaceholderText("Answer")

        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.handle_register)

        layout.addWidget(self.status_label)
        layout.addWidget(self.name_input)      
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.q1_label)
        layout.addWidget(self.a1_input)
        layout.addWidget(self.q2_label)
        layout.addWidget(self.a2_input)
        layout.addWidget(self.q3_label)
        layout.addWidget(self.a3_input)
        layout.addWidget(register_btn)

        self.setCentralWidget(central_widget)
        self.resize(400, 400)

    def handle_register(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        # The security questions are fixed; we store the provided answers.
        q1 = "Where were you born?"
        a1 = self.a1_input.text().strip()
        q2 = "What is your favorite pet's name?"
        a2 = self.a2_input.text().strip()
        q3 = "What is your mother's maiden name?"
        a3 = self.a3_input.text().strip()

        if not name or not email or not password or not a1 or not a2 or not a3:
            self.status_label.setText("Please fill all fields!")
            return

        success = self.db_manager.insert_user(name, email, password, q1, a1, q2, a2, q3, a3)
        if success:
            self.status_label.setText("Registration successful!")
            self.mediator.send({"type": "SHOW_LOGIN"}, "register_window")
            self.close()
        else:
            self.status_label.setText("Email already registered!")

    def clear_fields(self):
        self.status_label.setText("")
        self.name_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.a1_input.clear()
        self.a2_input.clear()
        self.a3_input.clear()
