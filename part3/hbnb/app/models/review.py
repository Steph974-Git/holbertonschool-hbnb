#!/usr/bin/python3
"""Review model module for the HBNB application"""

from app.models.base_model import BaseModel
from app.models import db, bcrypt
from sqlalchemy import ForeignKey


class Review(BaseModel):
    __tablename__ = 'reviews'


    text = db.Column(db.String(), nullable=False)
    rating = db.Column(db.Integer(), nullable=False)
    user_id = db.Column(db.String(36), ForeignKey('users.id'), nullable=False)
    place_id = db.Column(db.String(36), ForeignKey('places.id'), nullable=False)

    def __init__(self, text, rating):
        """Initialize a new Review with validation

        Args:
            text (str): The content of the review
            rating (int): Rating score between 1 and 5
            place (Place): The place being reviewed
            user (User): The user writing the review

        Raises:
            ValueError: If any validation fails
            TypeError: If rating is not convertible to int
        """
        super().__init__()
        if not text:
            raise ValueError("Review text cannot be empty")
        if not isinstance(rating, int) or int(rating) < 1 or int(rating) > 5:
            raise ValueError("Rating must be an integer between 1 and 5")

        self.text = text
        self.rating = rating

