from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLineEdit, QListWidget, QListWidgetItem, QTextEdit,
    QToolBar, QAction, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt
from patterns.singleton import UserSessionSingleton
from patterns.proxy import PaymentProxy
from database.db_manager import DBManager
from datetime import datetime

class MainWindow(QMainWindow):
    def __init__(self, db_manager, mediator):
        super().__init__()
        self.db_manager = db_manager
        self.mediator = mediator
        self.setWindowTitle("DriveShare - Dashboard")
        self.init_ui()

    def init_ui(self):
        self.tabs = QTabWidget()

        self.dashboard_tab = QWidget()
        dash_layout = QVBoxLayout(self.dashboard_tab)
        self.welcome_label = QLabel("Welcome to DriveShare Dashboard!")
        dash_layout.addWidget(self.welcome_label)
        # Add Balance Section
        balance_layout = QHBoxLayout()
        self.balance_label = QLabel("Current Balance: $0.00")
        self.balance_input = QLineEdit()
        self.balance_input.setPlaceholderText("Enter amount to add")
        self.add_balance_btn = QPushButton("Add Balance")
        self.add_balance_btn.clicked.connect(self.handle_add_balance)
        balance_layout.addWidget(self.balance_label)
        balance_layout.addWidget(self.balance_input)
        balance_layout.addWidget(self.add_balance_btn)
        dash_layout.addLayout(balance_layout)
        self.tabs.addTab(self.dashboard_tab, "Dashboard")

        # Car Listings Tab
        from ui.car_list_window import CarListWindow
        self.car_list_tab = CarListWindow(self.db_manager)
        self.tabs.addTab(self.car_list_tab, "Car Listings")

        # Search & Rent Tab
        self.search_tab = QWidget()
        search_layout = QVBoxLayout(self.search_tab)
        self.search_label = QLabel("Search Cars by Location:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("e.g., San Francisco")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.handle_search)
        self.search_results_list = QListWidget()
        self.rent_car_btn = QPushButton("Rent Selected Car")
        self.rent_car_btn.clicked.connect(self.handle_rent_car)
        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.search_results_list)
        search_layout.addWidget(self.rent_car_btn)
        self.tabs.addTab(self.search_tab, "Search & Rent")

        # Messaging Tab with Inbox/Chat Split View
        self.msg_tab = QWidget()
        msg_layout = QHBoxLayout(self.msg_tab)
        # Left Panel: New Chat entry and Chat Partners list
        left_panel = QVBoxLayout()
        # New Chat entry
        new_chat_layout = QHBoxLayout()
        self.new_partner_input = QLineEdit()
        self.new_partner_input.setPlaceholderText("Enter partner's email")
        self.new_chat_btn = QPushButton("Start Chat")
        self.new_chat_btn.clicked.connect(self.start_new_chat)
        new_chat_layout.addWidget(self.new_partner_input)
        new_chat_layout.addWidget(self.new_chat_btn)
        left_panel.addLayout(new_chat_layout)
        # Existing Chat Partners List
        left_label = QLabel("Your Chats:")
        left_panel.addWidget(left_label)
        self.chat_partner_list = QListWidget()
        self.chat_partner_list.itemDoubleClicked.connect(self.open_chat_from_item)
        left_panel.addWidget(self.chat_partner_list)
        
        # Right Panel: Conversation View and Input
        right_panel = QVBoxLayout()
        self.chat_header = QLabel("Select a chat partner")
        self.chat_header.setAlignment(Qt.AlignCenter)
        right_panel.addWidget(self.chat_header)
        self.chat_view_list = QListWidget()
        right_panel.addWidget(self.chat_view_list)
        chat_input_layout = QHBoxLayout()
        self.chat_message_input = QLineEdit()
        self.chat_message_input.setPlaceholderText("Type your message here...")
        self.chat_send_btn = QPushButton("Send")
        self.chat_send_btn.clicked.connect(self.send_chat_message)
        chat_input_layout.addWidget(self.chat_message_input)
        chat_input_layout.addWidget(self.chat_send_btn)
        right_panel.addLayout(chat_input_layout)

        msg_layout.addLayout(left_panel, 1)
        msg_layout.addLayout(right_panel, 2)
        self.tabs.addTab(self.msg_tab, "Messages")

        # Reviews & Rental History Tab
        self.reviews_tab = QWidget()
        reviews_layout = QVBoxLayout(self.reviews_tab)
        rental_title = QLabel("Your Rental History")
        rental_title.setAlignment(Qt.AlignCenter)
        reviews_layout.addWidget(rental_title)
        self.rental_history_list = QListWidget()
        reviews_layout.addWidget(self.rental_history_list)
        refresh_history_btn = QPushButton("Refresh History")
        refresh_history_btn.clicked.connect(self.loadRentalHistory)
        reviews_layout.addWidget(refresh_history_btn)
        reviews_layout.addWidget(QLabel("-------------------------------------------------"))
        review_title = QLabel("Submit a Review")
        review_title.setAlignment(Qt.AlignCenter)
        reviews_layout.addWidget(review_title)
        booking_layout = QHBoxLayout()
        booking_label = QLabel("Booking ID:")
        self.booking_input = QLineEdit()
        booking_layout.addWidget(booking_label)
        booking_layout.addWidget(self.booking_input)
        reviews_layout.addLayout(booking_layout)
        reviewee_layout = QHBoxLayout()
        reviewee_label = QLabel("Reviewee User ID:")
        self.reviewee_input = QLineEdit()
        reviewee_layout.addWidget(reviewee_label)
        reviewee_layout.addWidget(self.reviewee_input)
        reviews_layout.addLayout(reviewee_layout)
        rating_layout = QHBoxLayout()
        rating_label = QLabel("Rating:")
        self.rating_combo = QComboBox()
        self.rating_combo.addItems([str(i) for i in range(1, 6)])
        rating_layout.addWidget(rating_label)
        rating_layout.addWidget(self.rating_combo)
        reviews_layout.addLayout(rating_layout)
        feedback_label = QLabel("Feedback:")
        self.feedback_text = QTextEdit()
        reviews_layout.addWidget(feedback_label)
        reviews_layout.addWidget(self.feedback_text)
        submit_review_btn = QPushButton("Submit Review")
        submit_review_btn.clicked.connect(self.submitReview)
        reviews_layout.addWidget(submit_review_btn)
        self.tabs.addTab(self.reviews_tab, "Reviews")
        # --- End of Tabs ---

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.tabs)
        self.setCentralWidget(central_widget)
        self.resize(800, 600)
        self.create_toolbar()

    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar", self)
        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.handle_logout)
        toolbar.addAction(logout_action)
        self.addToolBar(toolbar)

    def handle_logout(self):
        session = UserSessionSingleton.get_instance()
        session.logout()
        self.mediator.send({"type": "SHOW_LOGIN"}, "main_window")
        self.close()

    def on_user_logged_in(self, user_id):
        session = UserSessionSingleton.get_instance()
        self.welcome_label.setText(f"Welcome, {session.name}!")
        self.mediator.register("main_window", self)
        self.loadChatPartners()  # Refresh chat partner list
        self.car_list_tab.load_cars()
        current_balance = self.db_manager.get_balance(session.user_id)
        self.balance_label.setText(f"Current Balance: ${current_balance:.2f}")
        self.loadRentalHistory()
        self.show()

    def handle_search(self):
        location = self.search_input.text().strip()
        self.search_results_list.clear()
        if not location:
            self.search_results_list.addItem("Please enter a location.")
            return
        results = self.db_manager.search_cars(location, "", "")
        if results:
            for car in results:
                item_text = f"{car['model']} ({car['year']}) - ${car['price_per_day']}/day | Location: {car['location']}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, car['car_id'])
                self.search_results_list.addItem(item)
        else:
            self.search_results_list.addItem("No cars found for that location.")

    def handle_rent_car(self):
        session = UserSessionSingleton.get_instance()
        if not session.is_logged_in():
            return
        selected_item = self.search_results_list.currentItem()
        if not selected_item:
            return
        car_id = selected_item.data(Qt.UserRole)
        success, message = self.db_manager.rent_car(car_id, session.user_id)
        current_balance = self.db_manager.get_balance(session.user_id)
        self.balance_label.setText(f"Current Balance: ${current_balance:.2f}")
        self.search_results_list.addItem(message)

    def handle_add_balance(self):
        session = UserSessionSingleton.get_instance()
        if not session.is_logged_in():
            return
        try:
            amount = float(self.balance_input.text().strip())
        except ValueError:
            self.balance_label.setText("Please enter a valid amount.")
            return
        self.db_manager.add_balance(session.user_id, amount)
        current_balance = self.db_manager.get_balance(session.user_id)
        self.balance_label.setText(f"Current Balance: ${current_balance:.2f}")
        self.balance_input.clear()

    # --- Methods for Reviews & Rental History ---
    def loadRentalHistory(self):
        self.rental_history_list.clear()
        session = UserSessionSingleton.get_instance()
        if not session.is_logged_in():
            self.rental_history_list.addItem("Please log in to view rental history.")
            return
        history = self.db_manager.get_rental_history_for_renter(session.user_id)
        if not history:
            self.rental_history_list.addItem("No rental history found.")
        else:
            for booking in history:
                item_text = (f"Booking ID: {booking['booking_id']} | Car ID: {booking['car_id']} | "
                             f"Dates: {booking['start_date']} to {booking['end_date']} | Status: {booking['status']}")
                self.rental_history_list.addItem(item_text)

    def submitReview(self):
        session = UserSessionSingleton.get_instance()
        if not session.is_logged_in():
            return
        booking_id_text = self.booking_input.text().strip()
        reviewee_id_text = self.reviewee_input.text().strip()
        rating = int(self.rating_combo.currentText())
        feedback = self.feedback_text.toPlainText().strip()

        if not booking_id_text or not reviewee_id_text:
            QMessageBox.warning(self, "Input Error", "Please fill out both Booking ID and Reviewee User ID.")
            return

        try:
            booking_id = int(booking_id_text)
            reviewee_id = int(reviewee_id_text)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Booking ID and Reviewee User ID must be valid integers.")
            return

        success = session.user.submit_review(
            self.db_manager, booking_id, reviewee_id, rating, feedback
        )
        if success:
            QMessageBox.information(self, "Success", "Review submitted successfully.")
            self.booking_input.clear()
            self.reviewee_input.clear()
            self.feedback_text.clear()
            self.loadRentalHistory()
        else:
            QMessageBox.critical(self, "Error", "Failed to submit review. Please try again.")

    # --- Methods for One-to-One Chat (Messaging Tab) ---
    def loadChatPartners(self):
        """Load a list of distinct chat partners from previous messages."""
        self.chat_partner_list.clear()
        session = UserSessionSingleton.get_instance()
        if not session.is_logged_in():
            return
        user_id = session.user_id
        query = """
            SELECT DISTINCT
                CASE
                    WHEN sender_id = ? THEN receiver_id
                    ELSE sender_id
                END AS partner_id
            FROM messages
            WHERE sender_id = ? OR receiver_id = ?
        """
        params = (user_id, user_id, user_id)
        self.db_manager.cursor.execute(query, params)
        rows = self.db_manager.cursor.fetchall()
        partner_ids = [r["partner_id"] for r in rows]
        for pid in partner_ids:
            self.db_manager.cursor.execute("SELECT * FROM users WHERE user_id = ?", (pid,))
            partner_row = self.db_manager.cursor.fetchone()
            if partner_row:
                partner = dict(partner_row)
                item = QListWidgetItem(partner["email"])
                item.setData(Qt.UserRole, partner)
                self.chat_partner_list.addItem(item)

    def open_chat_from_item(self, item):
        """Open chat when a partner is double-clicked from the chat partner list."""
        partner = item.data(Qt.UserRole)
        self.load_chat_conversation(partner)

    def load_chat_conversation(self, partner):
        """Load messages between current user and the given partner into the conversation view."""
        session = UserSessionSingleton.get_instance()
        current_user_id = session.user_id
        self.chat_header.setText(f"Chat with {partner['email']}")
        self.chat_view_list.clear()
        query = """
            SELECT * FROM messages 
            WHERE (sender_id = ? AND receiver_id = ?)
               OR (sender_id = ? AND receiver_id = ?)
            ORDER BY timestamp ASC
        """
        params = (current_user_id, partner["user_id"],
                  partner["user_id"], current_user_id)
        self.db_manager.cursor.execute(query, params)
        messages = self.db_manager.cursor.fetchall()
        for msg in messages:
            msg_dict = dict(msg)
            if msg_dict["sender_id"] == current_user_id:
                sender = session.email
            else:
                sender = partner["email"]
            self.chat_view_list.addItem(f"[{msg_dict['timestamp']}] {sender}: {msg_dict['content']}")
        self.chat_view_list.scrollToBottom()
        # Store current conversation partner for sending messages
        self.current_chat_partner = partner

    def send_chat_message(self):
        """Send the message typed in the chat input to the current chat partner."""
        session = UserSessionSingleton.get_instance()
        if not session.is_logged_in() or not hasattr(self, "current_chat_partner"):
            QMessageBox.warning(self, "No Chat Selected", "Please select a chat partner first.")
            return
        content = self.chat_message_input.text().strip()
        if not content:
            return
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.db_manager.cursor.execute(
                "INSERT INTO messages(sender_id, receiver_id, content, timestamp) VALUES (?, ?, ?, ?)",
                (session.user_id, self.current_chat_partner["user_id"], content, timestamp)
            )
            self.db_manager.conn.commit()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send message: {e}")
            return
        self.chat_message_input.clear()
        self.load_chat_conversation(self.current_chat_partner)

    def start_new_chat(self):
        """Start a new chat using the email entered in the new partner input."""
        partner_email = self.new_partner_input.text().strip().lower()
        if not partner_email:
            QMessageBox.warning(self, "Input Error", "Please enter the partner's email.")
            return
        # Look up the partner from the DB using the email
        partner = self.db_manager.get_user_by_email(partner_email)
        if not partner:
            QMessageBox.critical(self, "Error", f"No user found with email: {partner_email}")
            return
        # Load the conversation into the built-in chat pane
        self.load_chat_conversation(partner)
        self.new_partner_input.clear()
        self.loadChatPartners()

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    db_manager = DBManager("driveshare.db")
    mediator = None 

    window = MainWindow(db_manager, mediator)
    window.show()

    sys.exit(app.exec_())
