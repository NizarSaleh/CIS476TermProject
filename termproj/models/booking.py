# booking.py
"""
Booking model represents a rental booking in DriveShare.
"""
class Booking:
    def __init__(self, booking_id, car_id, renter_id, start_date, end_date, status):
        self.booking_id = booking_id
        self.car_id = car_id
        self.renter_id = renter_id
        self.start_date = start_date
        self.end_date = end_date
        self.status = status

    def __repr__(self):
        return f"Booking(id={self.booking_id}, car_id={self.car_id}, renter_id={self.renter_id}, status={self.status})"
