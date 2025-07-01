"""Module de façade pour l'application HBnB.

Ce module implémente le pattern Façade pour centraliser l'accès aux fonctionnalités
de l'application. Il gère l'interaction avec les repositories et fournit une interface
unifiée pour toutes les opérations sur les modèles.
"""
from app.persistence.repository import InMemoryRepository, SQLAlchemyRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review

# Repositories globaux pour le partage de données entre les instances
_user_repo = InMemoryRepository()
_place_repo = InMemoryRepository()
_review_repo = InMemoryRepository()
_amenity_repo = InMemoryRepository()
_initialized = False  # Variable globale de contrôle d'initialisation


class HBnBFacade:
    """Façade pour accéder aux fonctionnalités de l'application.

    Cette classe implémente le pattern Singleton pour assurer qu'une seule
    instance de la façade existe dans l'application, permettant ainsi un
    accès unifié aux données.
    """
    _instance = None

    def __new__(cls):
        """Implémentation du pattern Singleton.

        Returns:
            HBnBFacade: L'instance unique de la façade.
        """
        if cls._instance is None:
            cls._instance = super(HBnBFacade, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialise la façade avec les repositories.

        Utilise les repositories globaux pour assurer que toutes les instances
        partagent les mêmes données.
        """
        self.user_repo = SQLAlchemyRepository(User)  # Switched to SQLAlchemyRepository
        self.place_repo = SQLAlchemyRepository(Place)
        self.review_repo = SQLAlchemyRepository(Review)
        self.amenity_repo = SQLAlchemyRepository(Amenity)

        global _initialized
        if not _initialized:
            # Utiliser les repositories globaux
            self.user_repo = _user_repo
            self.place_repo = _place_repo
            self.review_repo = _review_repo
            self.amenity_repo = _amenity_repo
            _initialized = True
            print("HBnBFacade initialized with global repositories")

    def create_user(self, user_data):
        """Crée un nouvel utilisateur.

        Args:
            user_data (dict): Données de l'utilisateur à créer.

        Returns:
            User: L'objet utilisateur créé.
        """
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def create_place(self, place_data):
        """Crée un nouvel hébergement.

        Args:
            place_data (dict): Données de l'hébergement, incluant owner_id et
                               optionnellement une liste d'amenities.

        Returns:
            Place: L'objet hébergement créé.

        Raises:
            ValueError: Si le propriétaire spécifié n'existe pas.
        """
        # Récupère et retire l'ID du propriétaire du dictionnaire
        owner_id = place_data.pop('owner_id')
        owner = self.get_user(owner_id)
        if not owner:
            raise ValueError("Owner not found")

        # Extrait les amenities du dictionnaire si présentes
        amenities = place_data.pop('amenities', [])

        # Crée l'objet Place avec le propriétaire et les attributs restants
        place = Place(owner=owner, **place_data)

        # Ajoute les amenities à la place si elles existent
        for amenity_id in amenities:
            amenity = self.amenity_repo.get(amenity_id)
            if amenity:
                place.add_amenity(amenity)

        self.place_repo.add(place)
        return place

    def get_place(self, place_id):
        """Récupère un hébergement par son ID.

        Args:
            place_id (str): ID de l'hébergement à récupérer.

        Returns:
            Place: L'objet hébergement ou None s'il n'existe pas.
        """
        return self.place_repo.get(place_id)

    def get_all_places(self):
        """Récupère tous les hébergements.

        Returns:
            list: Liste de tous les objets Place.
        """
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        """Met à jour un hébergement existant.

        Args:
            place_id (str): ID de l'hébergement à mettre à jour.
            place_data (dict): Données à mettre à jour, peut inclure une liste d'amenities.

        Returns:
            Place: L'objet hébergement mis à jour ou None s'il n'existe pas.
        """
        # Vérifie que l'hébergement existe
        place = self.place_repo.get(place_id)
        if not place:
            return None

        # Extrait et traite séparément les amenities
        amenity_ids = place_data.pop('amenities', [])
        self.place_repo.update(place_id, place_data)
        updated_place = self.place_repo.get(place_id)
        updated_place.amenities = []

        # Ajoute les nouvelles amenities à l'hébergement
        for amenity_id in amenity_ids:
            amenity = self.amenity_repo.get(amenity_id)
            if amenity:
                updated_place.add_amenity(amenity)

        return updated_place

    def get_user(self, user_id):
        """Récupère un utilisateur par son ID.

        Args:
            user_id (str): ID de l'utilisateur à récupérer.

        Returns:
            User: L'objet utilisateur ou None s'il n'existe pas.
        """
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        """Récupère un utilisateur par son email.

        Args:
            email (str): Email de l'utilisateur à récupérer.

        Returns:
            User: L'objet utilisateur ou None s'il n'existe pas.
        """
        return self.user_repo.get_by_attribute('email', email)

    def create_amenity(self, name):
        """Crée un nouvel équipement.

        Args:
            name (str): Nom de l'équipement à créer.

        Returns:
            Amenity: L'objet équipement créé.

        Raises:
            Exception: Si une erreur survient lors de la création.
        """
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
        """Récupère un équipement par son ID.

        Args:
            amenity_id (str): ID de l'équipement à récupérer.

        Returns:
            Amenity: L'objet équipement ou None s'il n'existe pas.
        """
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        """Récupère tous les équipements.

        Returns:
            list: Liste de tous les objets Amenity.
        """
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, name):
        """Met à jour un équipement existant.

        Args:
            amenity_id (str): ID de l'équipement à mettre à jour.
            name (str): Nouveau nom pour l'équipement.

        Returns:
            Amenity: L'objet équipement mis à jour ou None s'il n'existe pas.
        """
        # Récupère l'équipement à mettre à jour
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            return None

        # Met à jour le nom et sauvegarde
        amenity.name = name
        amenity.save()  # Mettre à jour le timestamp updated_at
        return amenity

    def get_amenity(self, amenity_id):
        """Récupère un équipement par son ID (alias pour get_amenity_by_id).

        Args:
            amenity_id (str): ID de l'équipement à récupérer.

        Returns:
            Amenity: L'objet équipement ou None s'il n'existe pas.
        """
        return self.amenity_repo.get(amenity_id)

    def get_all_users(self):
        """Récupère tous les utilisateurs.

        Returns:
            list: Liste de tous les objets User.
        """
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        """Met à jour un utilisateur existant.

        Args:
            user_id (str): ID de l'utilisateur à mettre à jour.
            user_data (dict): Données à mettre à jour.

        Returns:
            User: L'objet utilisateur mis à jour ou None s'il n'existe pas.
        """
        # Vérifie que l'utilisateur existe
        user = self.user_repo.get(user_id)
        if not user:
            return None

        # Met à jour l'utilisateur et retourne l'objet mis à jour
        self.user_repo.update(user_id, user_data)
        return self.user_repo.get(user_id)

    def create_review(self, review_data):
        """Crée un nouvel avis.

        Args:
            review_data (dict): Données de l'avis incluant texte, note,
                               utilisateur et hébergement.

        Returns:
            Review: L'objet avis créé.
        """
        # Crée l'objet Review avec les données fournies
        review = Review(
            text=review_data['text'],
            rating=review_data['rating'],
            user=review_data['user'],
            place=review_data['place'])

        # Ajoute la review à l'hébergement concerné
        review_data['place'].add_review(review)

        # Ajoute la review au repository
        self.review_repo.add(review)
        return review

    def get_review(self, review_id):
        """Récupère un avis par son ID.

        Args:
            review_id (str): ID de l'avis à récupérer.

        Returns:
            Review: L'objet avis ou None s'il n'existe pas.
        """
        if not review_id:
            return None
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        """Récupère tous les avis.

        Returns:
            list: Liste de tous les objets Review.
        """
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        """Récupère tous les avis pour un hébergement spécifique.

        Args:
            place_id (str): ID de l'hébergement dont on veut récupérer les avis.

        Returns:
            list: Liste des avis pour l'hébergement spécifié.
        """
        # On vérifie si le place_id est valide
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
        """Met à jour un avis existant.

        Args:
            review_id (str): ID de l'avis à mettre à jour.
            review_data (dict): Données à mettre à jour (texte et/ou note).

        Returns:
            Review: L'objet avis mis à jour ou None s'il n'existe pas.
        """
        # On récupère la review existante
        review = self.review_repo.get(review_id)

        # On vérifie si elle existe
        if not review:
            return None

        # Validation de la note si présente
        if 'rating' in review_data:
            try:
                rating = int(review_data['rating'])
                if rating < 1 or rating > 5:
                    raise ValueError("Rating must be between 1 and 5")
                review_data['rating'] = rating
            except (ValueError, TypeError):
                raise ValueError(
                    "Rating must be a valid integer between 1 and 5")

        # On met à jour les attributs de la review
        if 'text' in review_data:
            # Validation du texte
            if not review_data['text']:
                raise ValueError("Review text cannot be empty")
            review.text = review_data['text']

        if 'rating' in review_data:
            review.rating = review_data['rating']

        # Sauvegarde des modifications
        review.save()
        return review

    def delete_review(self, review_id):
        """Supprime un avis existant.

        Args:
            review_id (str): ID de l'avis à supprimer.

        Returns:
            bool: True si l'avis a été supprimé, False sinon.
        """
        # On vérifie si la review existe
        review = self.review_repo.get(review_id)
        if not review:
            return False

        # On supprime la review du repository
        self.review_repo.delete(review_id)

        # Return True pour indiquer que la suppression a réussi
        return True

    def create_user(self, user_data):
        user = User(**user_data)
        self.user_repository.add(user)
        return user

    def get_user_by_id(self, user_id):
        return self.user_repository.get(user_id)

    def get_all_users(self):
        return self.user_repository.get_all()
    
    def create_place(self, place_data):
        place = Place(**place_data)
        self.user_repository.add(place)
        return place

    def get_place_by_id(self, place_id):
        return self.place_repository.get(place_id)

    def get_all_places(self):
        return self.place_repository.get_all()
    
    def create_ameneties(self, amenity_data):
        amenity = Amenity(**amenity_data)
        self.user_repository.add(amenity)
        return amenity

    def get_amenity_by_id(self, amennity_id):
        return self.amenity_repository.get(amennity_id)

    def get_all_amenities(self):
        return self.amenity_repository.get_all()
    
    def create_reviews(self, review_data):
        review = Review(**review_data)
        self.review_repository.add(review)
        return review

    def get_review_by_id(self, review_id):
        return self.review_repository.get(review_id)

    def get_all_reviews(self):
        return self.review_repository.get_all()