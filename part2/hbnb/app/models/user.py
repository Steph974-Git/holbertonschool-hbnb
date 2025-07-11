#!/usr/bin/python3
"""User model module for the HBNB application
"""
from app.models.base_model import BaseModel
"""User class for representing users in the application
"""


class User(BaseModel):

    def __init__(self, email, first_name, last_name, is_admin=False):
        """Initialize a new User instance with validation

        Args:
            email (str): User's email address
            first_name (str, optional): User's first name. Defaults to "".
            last_name (str, optional): User's last name. Defaults to "".
            is_admin (bool, optional): Admin status. Defaults to False.

        Raises:
            ValueError: If any validation fails
        """
        super().__init__()

        if not email or '@' not in email:
            raise ValueError("Invalid email format")
        if not first_name or len(first_name) > 50:
            raise ValueError(
                "First name exceeds maximum length of 50 characters")
        if not last_name or len(last_name) > 50:
            raise ValueError(
                "Last name exceeds maximum length of 50 characters")

        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.is_admin = is_admin
