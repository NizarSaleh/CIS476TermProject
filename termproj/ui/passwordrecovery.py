# ui/password_recovery.py
"""
PasswordRecoveryDialog implements a secure password recovery process.
It applies the Chain of Responsibility pattern to verify answers to the three security questions.
"""
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout
from patterns.chain_of_responsibility import SecurityQuestionHandler1, SecurityQuestionHandler2, SecurityQuestionHandler3

class PasswordRecoveryDialog(QDialog):
    def __init__(self, db_manager, user_email, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_email = user_email  # Email for which password recovery is requested
        self.setWindowTitle("Password Recovery")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # For demo purposes, correct answers are hardcoded.
        # In a production system, these would be loaded from the database for user_email.
        self.correct_answer1 = "CityName"    # e.g., where the user was born
        self.correct_answer2 = "PetName"     # e.g., favorite pet's name
        self.correct_answer3 = "MaidenName"  # e.g., mother's maiden name

        self.q1_label = QLabel("Security Question 1: Where were you born?")
        self.a1_input = QLineEdit()
        self.a1_input.setPlaceholderText("Answer")

        self.q2_label = QLabel("Security Question 2: What is your favorite pet's name?")
        self.a2_input = QLineEdit()
        self.a2_input.setPlaceholderText("Answer")

        self.q3_label = QLabel("Security Question 3: What is your mother's maiden name?")
        self.a3_input = QLineEdit()
        self.a3_input.setPlaceholderText("Answer")

        self.status_label = QLabel("")
        self.btn_submit = QPushButton("Recover Password")
        self.btn_submit.clicked.connect(self.handle_recovery)

        layout.addWidget(self.q1_label)
        layout.addWidget(self.a1_input)
        layout.addWidget(self.q2_label)
        layout.addWidget(self.a2_input)
        layout.addWidget(self.q3_label)
        layout.addWidget(self.a3_input)
        layout.addWidget(self.btn_submit)
        layout.addWidget(self.status_label)

    def handle_recovery(self):
        # Setup the chain for security question verification
        chain1 = SecurityQuestionHandler1()
        chain2 = SecurityQuestionHandler2()
        chain3 = SecurityQuestionHandler3()
        chain1.set_next(chain2).set_next(chain3)

        request = {
            "answer1": self.a1_input.text(),
            "correct_answer1": self.correct_answer1,
            "answer2": self.a2_input.text(),
            "correct_answer2": self.correct_answer2,
            "answer3": self.a3_input.text(),
            "correct_answer3": self.correct_answer3,
        }
        result = chain1.handle(request)
        if result:
            self.status_label.setText("Security questions passed. You may now reset your password.")
        else:
            self.status_label.setText("Security questions failed. Please try again.")
