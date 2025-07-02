from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager

# Import des extensions depuis models
from app.models import db, bcrypt

jwt = JWTManager()

def create_app(config_class="config.DevelopmentConfig"):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    api = Api(app, version='1.0', title='HBnB API',
              description='HBnB Application API')
    
    jwt.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)

    # Initialiser les modèles APRÈS les extensions
    with app.app_context():
        from app.models import init_models
        models = init_models()
        db.create_all()

    from app.api.v1.users import api as users_ns
    # Importation du namespace des amenities
    from app.api.v1.amenities import api as amenities_ns
    from app.api.v1.places import api as places_ns
    from app.api.v1.reviews import api as reviews_ns
    from app.api.v1.auth import api as auth_ns
    

    # Register the users namespace
    api.add_namespace(users_ns, path='/api/v1/users')
    # Register the amenities namespace
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    api.add_namespace(auth_ns, path='/api/v1/auth')
    return app
