#!/usr/bin/python3
"""Tests for the User class"""
from app.models.user import User
def test_user_creation():
    user = User(first_name="John", last_name="Doe", email="john.doe@example.com", password="password123")
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.email == "john.doe@example.com"
    assert user.is_admin is False  # Default value
    print("User creation test passed!")
def test_user_validation():
    try:
        # This should fail due to invalid email
        User(first_name="John", last_name="Doe", email="invalid_email", password="password123")
        print("User validation test failed - invalid email accepted")
    except ValueError:
        print("User validation test passed - invalid email rejected")
if __name__ == "__main__":
    test_user_creation()
    test_user_validation()