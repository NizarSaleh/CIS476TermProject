import sqlite3
from datetime import datetime

class DBManager:
    def __init__(self, db_name='driveshare.db'):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row  # Enable dict-like row access
        self.cursor = self.conn.cursor()
        self.setup_tables()

    def setup_tables(self):
        # USERS TABLE: Stores registration and authentication details, the user's name, and balance.
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                security_q1 TEXT NOT NULL,
                security_a1 TEXT NOT NULL,
                security_q2 TEXT NOT NULL,
                security_a2 TEXT NOT NULL,
                security_q3 TEXT NOT NULL,
                security_a3 TEXT NOT NULL,
                balance REAL NOT NULL DEFAULT 0.0
            );
        """)
        # CARS TABLE: Stores car listing details.
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cars (
                car_id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                model TEXT NOT NULL,
                year INTEGER NOT NULL,
                mileage INTEGER NOT NULL,
                location TEXT NOT NULL,
                price_per_day REAL NOT NULL,
                availability TEXT,
                FOREIGN KEY (owner_id) REFERENCES users(user_id)
            );
        """)
        # BOOKINGS TABLE: Stores booking details for rentals.
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                car_id INTEGER NOT NULL,
                renter_id INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (car_id) REFERENCES cars(car_id),
                FOREIGN KEY (renter_id) REFERENCES users(user_id)
            );
        """)
        # MESSAGES TABLE: For communication between users.
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (sender_id) REFERENCES users(user_id),
                FOREIGN KEY (receiver_id) REFERENCES users(user_id)
            );
        """)
        # REVIEWS TABLE: Stores reviews and ratings for completed rentals.
        # The UNIQUE constraint on booking_id ensures only one review per booking.
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id INTEGER NOT NULL UNIQUE,
                reviewer_id INTEGER NOT NULL,
                reviewee_id INTEGER NOT NULL,
                rating INTEGER NOT NULL,
                feedback TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (booking_id) REFERENCES bookings(booking_id),
                FOREIGN KEY (reviewer_id) REFERENCES users(user_id),
                FOREIGN KEY (reviewee_id) REFERENCES users(user_id)
            );
        """)
        self.conn.commit()

    # --- Existing Methods ---

    def get_messages(self, receiver_id):
        """Retrieve all messages sent to the given receiver."""
        self.cursor.execute("SELECT * FROM messages WHERE receiver_id=?", (receiver_id,))
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    def get_cars_by_owner(self, owner_id):
        """Returns a list of car listings (as dictionaries) for the given owner_id."""
        self.cursor.execute("SELECT * FROM cars WHERE owner_id=?", (owner_id,))
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    def insert_user(self, name, email, password, q1, a1, q2, a2, q3, a3):
        """Insert a new user into the users table including the name.
           Returns True on success."""
        try:
            self.cursor.execute("""
                INSERT INTO users(name, email, password, security_q1, security_a1,
                                  security_q2, security_a2, security_q3, security_a3)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, email, password, q1, a1, q2, a2, q3, a3))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print("Insert user error:", e)
            return False

    def get_user_by_email_and_password(self, email, password):
        """Retrieve a user's info based on email and password."""
        self.cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_user_by_email(self, email):
        """Retrieve a user's info by email."""
        self.cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def update_user_password(self, user_id, new_password):
        """Update a user's password."""
        self.cursor.execute("UPDATE users SET password=? WHERE user_id=?", (new_password, user_id))
        self.conn.commit()

    def insert_car(self, owner_id, model, year, mileage, location, price, availability):
        """Insert a new car listing."""
        self.cursor.execute("""
            INSERT INTO cars(owner_id, model, year, mileage, location, price_per_day, availability)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (owner_id, model, year, mileage, location, price, availability))
        self.conn.commit()

    def search_cars(self, location, max_mileage, rental_date):
        """
        Searches for cars by location, and filters by mileage and rental availability.
        - location: string to match in the location field.
        - max_mileage: maximum allowed mileage (as an integer).
        - rental_date: desired rental date as a string (format "YYYY-MM-DD").

        The availability column is assumed to be a string in the format "YYYY-MM-DD to YYYY-MM-DD".
        Returns a list of car listings (as dictionaries) that match the criteria.
        """
        self.cursor.execute(
            "SELECT * FROM cars WHERE location LIKE ? AND mileage <= ?",
            ('%' + location + '%', max_mileage)
        )
        rows = self.cursor.fetchall()
        results = []
        for row in rows:
            car = dict(row)
            avail_str = car.get("availability", "")
            try:
                start_avail, end_avail = avail_str.split(" to ")
                if rental_date >= start_avail and rental_date <= end_avail:
                    results.append(car)
            except Exception as e:
                # If availability cannot be parsed, include the car (or choose to exclude it)
                results.append(car)
        return results

    # --- Methods for Balance and Renting Functionality ---

    def add_balance(self, user_id, amount):
        """Add funds to the user's balance."""
        self.cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
        self.conn.commit()

    def get_balance(self, user_id):
        """Get the user's current balance."""
        self.cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
        row = self.cursor.fetchone()
        return row["balance"] if row else 0.0

    def rent_car(self, car_id, renter_id, start_date, end_date):
        """
        Attempts to rent a car by reserving it for the specified period.
        Prevents double-booking by checking for overlapping bookings.
        Deducts the total rental cost from the user's balance and creates a booking record.

        Parameters:
            car_id (int): The car to book.
            renter_id (int): The ID of the user renting the car.
            start_date (str): The start date in "YYYY-MM-DD" format.
            end_date (str): The end date in "YYYY-MM-DD" format.

        Returns:
            (bool, str): A tuple where True means success, with the message including the booking ID,
                         reviewee ID, and total cost; False means an error with an explanation.
        """
        # Retrieve car details
        self.cursor.execute("SELECT * FROM cars WHERE car_id=?", (car_id,))
        car = self.cursor.fetchone()
        if not car:
            return False, "Car not found."

        # Check for overlapping bookings
        self.cursor.execute("""
            SELECT * FROM bookings
            WHERE car_id = ?
              AND status = 'Booked'
              AND NOT (? > end_date OR ? < start_date)
        """, (car_id, start_date, end_date))
        conflict = self.cursor.fetchone()
        if conflict:
            return False, "Car is already booked for the selected period."

        from datetime import datetime
        d1 = datetime.strptime(start_date, "%Y-%m-%d")
        d2 = datetime.strptime(end_date, "%Y-%m-%d")
        rental_days = (d2 - d1).days + 1
        total_price = rental_days * car["price_per_day"]

        balance = self.get_balance(renter_id)
        if balance < total_price:
            return False, "Insufficient balance. Please add funds."

        # Deduct rental cost and create a booking
        self.cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id=?", (total_price, renter_id))
        self.cursor.execute("""
            INSERT INTO bookings(car_id, renter_id, start_date, end_date, status)
            VALUES (?, ?, ?, ?, ?)
        """, (car["car_id"], renter_id, start_date, end_date, "Booked"))
        self.conn.commit()
        booking_id = self.cursor.lastrowid
        reviewee_id = car["owner_id"]
        return True, f"Rental successful!\nBooking ID: {booking_id}\nReviewee ID: {reviewee_id}\nTotal Cost: ${total_price:.2f}"

    # --- Methods for Rental History ---

    def get_rental_history_for_renter(self, renter_id):
        """
        Retrieve the rental history for a renter.
        Returns a list of booking records (as dictionaries) where this user is the renter.
        """
        self.cursor.execute("SELECT * FROM bookings WHERE renter_id=?", (renter_id,))
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    def get_rental_history_for_owner(self, owner_id):
        """
        Retrieve the rental history for a car owner.
        Returns a list of booking records (as dictionaries) for which the user owns the car.
        """
        self.cursor.execute("""
            SELECT b.*
            FROM bookings b
            JOIN cars c ON b.car_id = c.car_id
            WHERE c.owner_id = ?
        """, (owner_id,))
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    # --- Methods for Reviews ---

    def insert_review(self, booking_id, reviewer_id, reviewee_id, rating, feedback):
        """
        Insert a review for a completed rental.
        - booking_id: ID of the booking associated with the review.
        - reviewer_id: The user who is writing the review.
        - reviewee_id: The user being reviewed.
        - rating: An integer rating (e.g., 1 to 5).
        - feedback: Textual feedback message.
        Returns True on success, False otherwise.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.cursor.execute("""
                INSERT INTO reviews (booking_id, reviewer_id, reviewee_id, rating, feedback, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (booking_id, reviewer_id, reviewee_id, rating, feedback, timestamp))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print("Insert review error:", e)
            return False

    def get_reviews_for_user(self, user_id):
        """
        Retrieve all reviews received by a specific user.
        Returns a list of review records (as dictionaries).
        """
        self.cursor.execute("SELECT * FROM reviews WHERE reviewee_id=?", (user_id,))
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    def get_review_by_booking(self, booking_id):
        """
        Retrieve the review associated with a specific booking.
        Returns a review record (as a dictionary) if found.
        """
        self.cursor.execute("SELECT * FROM reviews WHERE booking_id=?", (booking_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def update_car_availability(self, car_id, availability):
        """
        Update the availability field for a given car.
        :param car_id: The ID of the car to update.
        :param availability: The new availability string (e.g., a date range).
        """
        self.cursor.execute("UPDATE cars SET availability = ? WHERE car_id = ?", (availability, car_id))
        self.conn.commit()
    def update_car_price(self, car_id, price):
        """
        Update the price_per_day field for a given car.
        :param car_id: The ID of the car to update.
        :param price: The new price per day (float).
        """
        self.cursor.execute("UPDATE cars SET price_per_day = ? WHERE car_id = ?", (price, car_id))
        self.conn.commit()