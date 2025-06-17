from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place

# Repositories globaux
_user_repo = InMemoryRepository()
_place_repo = InMemoryRepository()
_review_repo = InMemoryRepository()
_amenity_repo = InMemoryRepository()
_initialized = False  # Variable globale de contrôle d'initialisation

class HBnBFacade:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HBnBFacade, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        global _initialized
        if not _initialized:
            # Utiliser les repositories globaux
            self.user_repo = _user_repo
            self.place_repo = _place_repo
            self.review_repo = _review_repo
            self.amenity_repo = _amenity_repo
            _initialized = True
            print("HBnBFacade initialized with global repositories")

    # Reste de vos méthodes inchangé
    def create_user(self, user_data):
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def create_place(self, place_data):
        place = Place(**place_data)
        self.place_repo.add(place)
        return place

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        place = self.place_repo.get(place_id)
        if not place:
            return None
        
        self.place_repo.update(place_id, place_data)
        return self.place_repo.get(place_id)

    def get_user(self, user_id):
        return self.user_repo.get(user_id)
    
    def get_user_by_email(self, email):
        return self.user_repo.get_by_attribute('email', email)
    
    def create_amenity(self, name):
        try:
            # Cette méthode reçoit un nom, pas un dict
            amenity = Amenity(name=name)
            self.amenity_repo.add(amenity)
            return amenity
        except Exception as e:
            import traceback
            print(f"Error in create_amenity: {str(e)}")
            print(traceback.format_exc())
            raise  # Relève l'exception pour être gérée au niveau supérieur

    def get_amenity_by_id(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, name):
        # Cette méthode reçoit un ID et un nom, pas un dict
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            return None
        
        amenity.name = name
        amenity.save()  # Mettre à jour le timestamp updated_at
        return amenity

    "add task 2"
    def get_all_users(self):
        return self.user_repo.get_all()
    
    "add tack 2" 
    def update_user(self, user_id, user_data):
        user = self.user_repo.get(user_id)
        if not user:
            return None
        
        self.user_repo.update(user_id, user_data)
        return self.user_repo.get(user_id)