# termproj/ui/chat_window.py
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QListWidget, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from datetime import datetime

class ChatWindow(QMainWindow):
    def __init__(self, db_manager, current_user, partner_email):
        super().__init__()
        self.db_manager = db_manager
        self.current_user = current_user  
        self.partner_email = partner_email.strip().lower()
        self.partner = self.db_manager.get_user_by_email(self.partner_email)
        if not self.partner:
            QMessageBox.critical(self, "Error", f"No user found with email: {self.partner_email}")
            self.close()
            return

        self.setWindowTitle(f"Chat with {self.partner['email']}")
        self.init_ui()
        self.load_chat()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        self.chat_label = QLabel(f"Chat between You and {self.partner['email']}")
        self.chat_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.chat_label)
        
        self.chat_list = QListWidget()
        layout.addWidget(self.chat_list)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        layout.addWidget(self.message_input)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        layout.addWidget(self.send_btn)

    def load_chat(self):
        self.chat_list.clear()
        query = """
            SELECT * FROM messages 
            WHERE (sender_id = ? AND receiver_id = ?)
               OR (sender_id = ? AND receiver_id = ?)
            ORDER BY timestamp ASC
        """
        params = (self.current_user["user_id"], self.partner["user_id"],
                  self.partner["user_id"], self.current_user["user_id"])
        self.db_manager.cursor.execute(query, params)
        messages = self.db_manager.cursor.fetchall()
        for msg in messages:
            msg_dict = dict(msg)
            sender = "You" if msg_dict["sender_id"] == self.current_user["user_id"] else self.partner["email"]
            self.chat_list.addItem(f"[{msg_dict['timestamp']}] {sender}: {msg_dict['content']}")

    def send_message(self):
        content = self.message_input.text().strip()
        if not content:
            return
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.db_manager.cursor.execute(
                "INSERT INTO messages(sender_id, receiver_id, content, timestamp) VALUES (?, ?, ?, ?)",
                (self.current_user["user_id"], self.partner["user_id"], content, timestamp)
            )
            self.db_manager.conn.commit()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send message: {e}")
            return
        self.message_input.clear()
        self.load_chat()
