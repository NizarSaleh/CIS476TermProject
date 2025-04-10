# ui/car_list_window.py
"""
CarListWindow allows car owners to view their current listings and add new car listings.
It demonstrates the use of the Builder pattern.
"""
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLineEdit, QLabel, QPushButton, QWidget, QListWidget
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

        self.car_list_widget = QListWidget()

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

        layout.addWidget(QLabel("My Listed Cars:"))
        layout.addWidget(self.car_list_widget)
        layout.addWidget(QLabel("Add New Car Listing:"))
        layout.addWidget(self.model_input)
        layout.addWidget(self.year_input)
        layout.addWidget(self.mileage_input)
        layout.addWidget(self.location_input)
        layout.addWidget(self.price_input)
        layout.addWidget(self.availability_input)
        layout.addWidget(add_car_btn)

        self.setCentralWidget(central_widget)
        self.resize(400, 500)

        self.load_cars()

    def load_cars(self):
        """
        Load car listings for the current owner and append aggregate review info.
        For each car, the average rating and total number of reviews are calculated
        based on reviews available for the car's bookings.
        """
        self.car_list_widget.clear()
        session = UserSessionSingleton.get_instance()
        if not session.is_logged_in():
            self.car_list_widget.addItem("Please log in to view your listings.")
            return
        owner_id = session.user_id
        cars = self.db_manager.get_cars_by_owner(owner_id)
        if cars:
            for car in cars:
                # Fetch all bookings for this car.
                self.db_manager.cursor.execute("SELECT booking_id FROM bookings WHERE car_id = ?", (car['car_id'],))
                booking_rows = self.db_manager.cursor.fetchall()
                booking_ids = [row['booking_id'] for row in booking_rows]

                # Retrieve reviews for each booking.
                reviews = []
                for booking_id in booking_ids:
                    review = self.db_manager.get_review_by_booking(booking_id)
                    if review:
                        reviews.append(review)

                # Calculate aggregate review info.
                num_reviews = len(reviews)
                avg_rating = 0
                if num_reviews > 0:
                    total_rating = sum(review['rating'] for review in reviews)
                    avg_rating = total_rating / num_reviews

                # Build the display text with review info.
                display_text = f"{car['model']} ({car['year']}) - ${car['price_per_day']}/day"
                if num_reviews > 0:
                    display_text += f" | Avg. Rating: {avg_rating:.1f} ({num_reviews} review{'s' if num_reviews > 1 else ''})"
                else:
                    display_text += " | No reviews yet"

                self.car_list_widget.addItem(display_text)
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
            return

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

        # Clear input fields and refresh the listings
        self.model_input.clear()
        self.year_input.clear()
        self.mileage_input.clear()
        self.location_input.clear()
        self.price_input.clear()
        self.availability_input.clear()
        self.load_cars()
