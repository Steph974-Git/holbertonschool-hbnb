#!/usr/bin/python3
from app.models.base_model import BaseModel


class Amenity(BaseModel):
    def __init__(self, name):
        super().__init__()
        if not name:
            raise ValueError("Name is required")
        if len(name) > 50:
            raise ValueError("Name must be 50 characters maximum")

        self.name = name
