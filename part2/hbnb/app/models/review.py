#!/usr/bin/python3
"""Review model module for the HBNB application"""

from app.models.base_model import BaseModel
from app.models.user import User
from app.models.place import Place

class Review(BaseModel):

    def __init__(self, text, rating, place, user):
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
        if not rating or int(rating) < 1 or int(rating) > 5:
            raise ValueError("Rating is from 1 to 5")
        if not isinstance(place, Place):
            raise ValueError("The place must be valid")
        if not isinstance(user, User):
            raise ValueError("The user must be valid")
        
        self.text = text
        self.rating = rating
        self.place = place
        self.user = user
        