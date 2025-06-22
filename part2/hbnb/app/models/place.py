#!/usr/bin/python3
from app.models.base_model import BaseModel
from app.models.user import User


class Place(BaseModel):
    def __init__(self, title, description, price, latitude, longitude, owner):
        super().__init__()
            # Validation du propriétaire
        if owner is None:
            raise ValueError("Owner cannot be None")
        
        if not isinstance(owner, User):
            raise ValueError("Owner must be a User object")

        # Ici on vérifie si le titre existe et ne dépasse pas 100 charactères.
        if not title or len(title) > 100:
            raise ValueError("100 characters maximum")

        # Validation du prix
        if price <= 0:
            raise ValueError("Price must be positive")

        # Validation des coordonées géographique
        if not (-90 <= latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")

        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner
        self.reviews = []  # Liste pour les reviews
        self.amenities = []  # Liste pour les amenities

    def add_review(self, review):
        """Add a review to the place."""
        self.reviews.append(review)

    def add_amenity(self, amenity):
        """Add an amenity to the place."""
        self.amenities.append(amenity)
