# patterns/builder.py
"""
Builder pattern for constructing Car objects.
Allows flexible creation of car listings with various attributes.
"""
from models.car import Car

class CarBuilder:
    def __init__(self):
        self._owner_id = None
        self._model = None
        self._year = None
        self._mileage = None
        self._location = None
        self._price_per_day = None
        self._availability = None

    def set_owner_id(self, owner_id):
        self._owner_id = owner_id
        return self

    def set_model(self, model):
        self._model = model
        return self

    def set_year(self, year):
        self._year = year
        return self

    def set_mileage(self, mileage):
        self._mileage = mileage
        return self

    def set_location(self, location):
        self._location = location
        return self

    def set_price_per_day(self, price):
        self._price_per_day = price
        return self

    def set_availability(self, availability):
        self._availability = availability
        return self

    def build(self):
        return Car(
            owner_id=self._owner_id,
            model=self._model,
            year=self._year,
            mileage=self._mileage,
            location=self._location,
            price_per_day=self._price_per_day,
            availability=self._availability
        )
