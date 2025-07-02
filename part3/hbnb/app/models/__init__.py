#!/usr/bin/python3
"""Module de centralisation des modèles pour éviter les imports circulaires.

Ce module centralise tous les imports de modèles et fournit une interface
unifiée pour accéder aux classes de modèles dans l'application HBnB.
"""

# Import des extensions Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# Instances partagées des extensions
db = SQLAlchemy()
bcrypt = Bcrypt()

# Import des modèles après la définition de db
def init_models():
    """Initialise et retourne tous les modèles après que l'app soit créée."""
    
    # Import des modèles de base
    from .base_model import BaseModel
    
    # Import des modèles métier
    from .user import User
    from .place import Place
    from .review import Review
    from .amenity import Amenity
    
    # Retourner un dictionnaire avec tous les modèles
    return {
        'BaseModel': BaseModel,
        'User': User,
        'Place': Place,
        'Review': Review,
        'Amenity': Amenity
    }

# Export des instances pour utilisation dans les modèles
__all__ = ['db', 'bcrypt', 'init_models']
