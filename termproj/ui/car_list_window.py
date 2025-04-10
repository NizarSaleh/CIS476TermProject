"""
CarListWindow allows car owners to view their current listings, add new car listings,
and see aggregate review data (average rating and review count) for each listing.
It demonstrates the use of the Builder pattern.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QLineEdit, QLabel, QPushButton, QWidget,
    QListWidget, QListWidgetItem, QHBoxLayout, QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from patterns.singleton import UserSessionSingleton
from patterns.builder import CarBuilder

class CarListWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("My Car Listings")
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        # Label and Refresh Button at top
        top_layout = QHBoxLayout()
        title_label = QLabel("My Listed Cars:")
        self.refresh_btn = QPushButton("Refresh Listings")
        self.refresh_btn.clicked.connect(self.load_cars)
        top_layout.addWidget(title_label)
        top_layout.addWidget(self.refresh_btn)
        layout.addLayout(top_layout)
        
        # Listings List – Double-click to edit car details (availability & price)
        self.car_list_widget = QListWidget()
        self.car_list_widget.itemDoubleClicked.connect(self.edit_car_details)
        layout.addWidget(self.car_list_widget)
        
        # Section to add a new car listing
        layout.addWidget(QLabel("Add New Car Listing:"))
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Car Model (e.g., Toyota Camry)")
        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("Year (e.g., 2020)")
        self.mileage_input = QLineEdit()
        self.mileage_input.setPlaceholderText("Mileage (e.g., 30000)")
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Location (e.g., San Francisco, CA)")
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Price Per Day (e.g., 49.99)")
        self.availability_input = QLineEdit()
        self.availability_input.setPlaceholderText("Availability (e.g., 2025-04-01 to 2025-04-10)")

        add_car_btn = QPushButton("Add Car Listing")
        add_car_btn.clicked.connect(self.add_car)

        layout.addWidget(self.model_input)
        layout.addWidget(self.year_input)
        layout.addWidget(self.mileage_input)
        layout.addWidget(self.location_input)
        layout.addWidget(self.price_input)
        layout.addWidget(self.availability_input)
        layout.addWidget(add_car_btn)

        self.setCentralWidget(central_widget)
        self.resize(400, 500)

        # Initially load cars
        self.load_cars()

    def load_cars(self):
        """Reload the list of car listings, including review and availability information."""
        self.car_list_widget.clear()
        session = UserSessionSingleton.get_instance()
        if not session.is_logged_in():
            self.car_list_widget.addItem("Please log in to view your listings.")
            return
        owner_id = session.user_id
        cars = self.db_manager.get_cars_by_owner(owner_id)
        if cars:
            for car in cars:
                # Fetch bookings and reviews to calculate aggregate review info.
                self.db_manager.cursor.execute("SELECT booking_id FROM bookings WHERE car_id = ?", (car['car_id'],))
                booking_rows = self.db_manager.cursor.fetchall()
                booking_ids = [row['booking_id'] for row in booking_rows]

                reviews = []
                for booking_id in booking_ids:
                    review = self.db_manager.get_review_by_booking(booking_id)
                    if review:
                        reviews.append(review)

                num_reviews = len(reviews)
                avg_rating = 0
                if num_reviews > 0:
                    total_rating = sum(review['rating'] for review in reviews)
                    avg_rating = total_rating / num_reviews

                display_text = (
                    f"{car['model']} ({car['year']}) - ${car['price_per_day']}/day | Location: {car['location']} "
                    f"| Availability: {car['availability']}"
                )
                if num_reviews > 0:
                    display_text += f" | Avg. Rating: {avg_rating:.1f} ({num_reviews} review{'s' if num_reviews > 1 else ''})"
                else:
                    display_text += " | No reviews yet"
                
                list_item = QListWidgetItem(display_text)
                # Attach full car information to the item
                list_item.setData(Qt.UserRole, car)
                self.car_list_widget.addItem(list_item)
        else:
            self.car_list_widget.addItem("No car listings found.")

    def add_car(self):
        session = UserSessionSingleton.get_instance()
        if not session.is_logged_in():
            return
        owner_id = session.user_id
        try:
            model = self.model_input.text().strip()
            year = int(self.year_input.text().strip())
            mileage = int(self.mileage_input.text().strip())
            location = self.location_input.text().strip()
            price = float(self.price_input.text().strip())
            availability = self.availability_input.text().strip()
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid information for all fields.")
            return

        from patterns.builder import CarBuilder
        car = (CarBuilder()
               .set_owner_id(owner_id)
               .set_model(model)
               .set_year(year)
               .set_mileage(mileage)
               .set_location(location)
               .set_price_per_day(price)
               .set_availability(availability)
               .build())
        self.db_manager.insert_car(car.owner_id, car.model, car.year, car.mileage,
                                     car.location, car.price_per_day, car.availability)
        self.model_input.clear()
        self.year_input.clear()
        self.mileage_input.clear()
        self.location_input.clear()
        self.price_input.clear()
        self.availability_input.clear()
        self.load_cars()

    def edit_car_details(self, item):
        """
        When a car listing is double-clicked, prompt the owner to update:
          - Availability (via text dialog)
          - Price (via double dialog)
        Then update the corresponding fields in the database.
        """
        car = item.data(Qt.UserRole)
       
        new_availability, ok1 = QInputDialog.getText(
            self, "Edit Availability", f"Current availability: {car['availability']}\nEnter new availability:"
        )
        if not ok1:
            return
        
        new_price, ok2 = QInputDialog.getDouble(
            self, "Edit Price", f"Current price: ${car['price_per_day']}\nEnter new price per day:", 
            decimals=2, min=0
        )
        if not ok2:
            return

        # Update the fields in the DB 
        self.db_manager.update_car_availability(car['car_id'], new_availability)
        self.db_manager.update_car_price(car['car_id'], new_price)

        QMessageBox.information(self, "Updated", "Car listing has been updated.")
        self.load_cars()

