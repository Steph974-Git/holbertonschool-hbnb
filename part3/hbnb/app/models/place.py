#!/usr/bin/python3
from app.models.base_model import BaseModel
from app.models import db, bcrypt
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.types import CHAR
from sqlalchemy.orm import relationship

place_amenity = db.Table('place_amenity',
    Column('place_id', CHAR(36), ForeignKey('places.id'), primary_key=True),
    Column('amenity_id', CHAR(36), ForeignKey('amenities.id'), primary_key=True)
)

class Place(BaseModel):
    __tablename__ = 'places'

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    price = db.Column(db.Float(), nullable=False)
    latitude = db.Column(db.Float(), nullable=False)
    longitude = db.Column(db.Float(), nullable=False)
    amenities = relationship('Amenity', secondary=place_amenity, lazy='subquery',
                           backref=db.backref('places', lazy=True))
    owner_id = db.Column(db.String(36), ForeignKey('users.id'), nullable=False)
    reviews = relationship('Review', backref='place', lazy=True)

    def __init__(self, title, description, price, latitude, longitude):
        super().__init__()

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
