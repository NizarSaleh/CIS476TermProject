# patterns/observer.py
"""
Observer pattern used for booking notifications.
The BookingSubject notifies observers about changes in booking status.
"""
class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self, data):
        for observer in self._observers:
            observer.update(data)

class Observer:
    def update(self, data):
        raise NotImplementedError

class BookingSubject(Subject):
    def change_booking_status(self, booking_id, new_status):
        data = {"booking_id": booking_id, "new_status": new_status}
        self.notify(data)

class BookingObserver(Observer):
    def __init__(self, user_id):
        self.user_id = user_id

    def update(self, data):
        print(f"[Observer] User {self.user_id} notified: Booking {data['booking_id']} is now {data['new_status']}.")
