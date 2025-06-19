from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review

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
        owner_id = place_data.pop('owner_id')
        owner = self.get_user(owner_id)
        if not owner:
            raise ValueError("Owner not found")
        
        amenities = place_data.pop('amenities', [])
        
        place = Place(owner=owner, **place_data)

        for amenity_id in amenities:
            amenity = self.amenity_repo.get(amenity_id)
            if amenity:
                place.add_amenity(amenity)

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
    
    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

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
    
    def create_review(self, review_data):
    # Placeholder for logic to create a review, including validation for user_id, place_id, and rating
        review = Review(
            text = review_data['text'],
            rating = review_data['rating'],
            user = review_data['user'],
            place = review_data['place'])
        
        review_data['place'].add_review(review)
        
    # On l'ajoute au repo
        self.review_repo.add(review)
        return review

    def get_review(self, review_id):
        if not review_id:
            return None
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        # On véréfie si le place_id est valide
        if not place_id:
            return []
        # On récupère toutes les reviews
        all_reviews = self.review_repo.get_all()
        # On filtre les reviews et on garde que celles du lieu spécifié
        place_reviews = []
        for review in all_reviews:
            if review.place and review.place.id == place_id:
                place_reviews.append(review)
        return place_reviews

    def updated_review(self, review_id, review_data):
        # On récupère la review existante
        review = self.review_repo.get(review_id)
        # On verifie si elle existe
        if not review:
            return None
        # On met a jour les attribut de la review
        if 'text' in review_data:
            review.text = review_data['text']
        
        if 'rating' in review_data:
            review.rating = review_data['rating']
        review.save()
        return review

    def delete_review(self, review_id):
        # On vérifie si la review existe
        review = self.review_repo.get(review_id)
        if not review:
            return False
        # On supprime la review du repo
        self.review_repo.delete(review_id)
        # Return True pour indiquer que la suppression existe
        return True 