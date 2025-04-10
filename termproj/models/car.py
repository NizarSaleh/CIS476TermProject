# car.py

class Car:
    def __init__(self, owner_id, model, year, mileage, location, price_per_day, availability, car_id=None):
        self.car_id = car_id
        self.owner_id = owner_id
        self.model = model
        self.year = year
        self.mileage = mileage
        self.location = location
        self.price_per_day = price_per_day
        self.availability = availability


    def __repr__(self):
        return f"Car(car_id={self.car_id}, model='{self.model}', year={self.year})"
