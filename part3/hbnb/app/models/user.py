#!/usr/bin/python3
"""User model module for the HBNB application
"""
from app.models.base_model import BaseModel
from app import bcrypt, db
"""User class for representing users in the application
"""


class User(BaseModel):
    __tablename__ = 'users'

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, email, first_name, last_name, password, is_admin=False):
        """Initialize a new User instance with validation

        Args:
            email (str): User's email address
            first_name (str, optional): User's first name. Defaults to "".
            last_name (str, optional): User's last name. Defaults to "".
            password (str): User's password.
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
        self.hash_password(password)

    def hash_password(self, password):
        """Hashes the password before storing it."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """Verifies if the provided password matches the hashed password."""
        return bcrypt.check_password_hash(self.password, password)
