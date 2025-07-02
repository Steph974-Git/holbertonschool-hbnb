#!/usr/bin/python3
from app.models.base_model import BaseModel
from app.models import db



class Amenity(BaseModel):
    __tablename__ = 'amenities'

    name = db.Column(db.String(50), nullable=False)
    
    def __init__(self, name):
        super().__init__()
        if not name:
            raise ValueError("Name is required")
        if len(name) > 50:
            raise ValueError("Name must be 50 characters maximum")

        self.name = name
