# user.py

class User:
    def __init__(self, user_id, email, password, balance=0.0):
        self.user_id = user_id
        self.email = email
        self.password = password
        self.balance = balance

    def __repr__(self):
        return f"User(user_id={self.user_id}, email='{self.email}')"

    def get_rental_history_as_renter(self, db_manager):
        """
        Retrieve rental history for this user as a renter.
        Delegates the database call to DBManager.
        """
        return db_manager.get_rental_history_for_renter(self.user_id)

    def get_rental_history_as_owner(self, db_manager):
        """
        Retrieve rental history for this user as a car owner.
        Delegates the database call to DBManager.
        """
        return db_manager.get_rental_history_for_owner(self.user_id)

    def get_reviews(self, db_manager):
        """
        Retrieve all reviews received by this user.
        Delegates the database call to DBManager.
        """
        return db_manager.get_reviews_for_user(self.user_id)

    def submit_review(self, db_manager, booking_id, reviewee_id, rating, feedback):
        """
        Submit a review for a completed rental.
        'self' is the reviewer.
        Delegates the review insertion to DBManager.
        """
        return db_manager.insert_review(booking_id, self.user_id, reviewee_id, rating, feedback)
