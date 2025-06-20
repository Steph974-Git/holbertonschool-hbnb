import unittest
import sys
import os

# Ajout du chemin du projet au sys.path pour permettre l'importation des modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.models.review import Review
from app.models.user import User
from app.models.place import Place
from datetime import datetime

class TestReview(unittest.TestCase):
    """Tests pour la classe Review"""

    def setUp(self):
        """Préparer les objets nécessaires pour les tests"""
        # Créer un utilisateur valide pour les tests
        self.user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        
        # Créer un lieu valide pour les tests
        self.place = Place(
            title="Test Place",
            description="A place for testing",
            price=100.0,
            latitude=40.7128,
            longitude=-74.0060,
            owner=self.user
        )

    def test_review_creation_with_valid_data(self):
        """Test la création d'une review avec des données valides"""
        review = Review(
            text="Great place, would stay again!",
            rating=5,
            user=self.user,
            place=self.place
        )
        
        # Vérifier que l'objet est correctement initialisé
        self.assertEqual(review.text, "Great place, would stay again!")
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.place, self.place)
        
        # Vérifier les attributs hérités de BaseModel
        self.assertIsNotNone(review.id)
        self.assertIsInstance(review.created_at, datetime)
        self.assertIsInstance(review.updated_at, datetime)

    def test_review_creation_with_minimum_rating(self):
        """Test la création d'une review avec la note minimale autorisée"""
        review = Review(
            text="Not so great, but acceptable.",
            rating=1,  # Note minimale
            user=self.user,
            place=self.place
        )
        self.assertEqual(review.rating, 1)

    def test_review_creation_with_maximum_rating(self):
        """Test la création d'une review avec la note maximale autorisée"""
        review = Review(
            text="Absolutely perfect!",
            rating=5,  # Note maximale
            user=self.user,
            place=self.place
        )
        self.assertEqual(review.rating, 5)

    def test_review_creation_empty_text(self):
        """Test la création d'une review avec un texte vide"""
        with self.assertRaises(ValueError):
            Review(
                text="",
                rating=4,
                user=self.user,
                place=self.place
            )

    def test_review_creation_invalid_rating_too_low(self):
        """Test la création d'une review avec une note trop basse"""
        with self.assertRaises(ValueError):
            Review(
                text="Valid text",
                rating=0,  # Trop bas, doit être >= 1
                user=self.user,
                place=self.place
            )

    def test_review_creation_invalid_rating_too_high(self):
        """Test la création d'une review avec une note trop élevée"""
        with self.assertRaises(ValueError):
            Review(
                text="Valid text",
                rating=6,  # Trop élevé, doit être <= 5
                user=self.user,
                place=self.place
            )

    def test_review_creation_invalid_rating_type(self):
        """Test la création d'une review avec un type de note invalide"""
        with self.assertRaises(ValueError):
            Review(
                text="Valid text",
                rating="good",  # Doit être un entier
                user=self.user,
                place=self.place
            )

    def test_review_creation_invalid_user(self):
        """Test la création d'une review avec un utilisateur non valide"""
        with self.assertRaises(ValueError):
            Review(
                text="Valid text",
                rating=4,
                user="not a user object",  # Doit être un objet User
                place=self.place
            )

    def test_review_creation_invalid_user_none(self):
        """Test la création d'une review avec un utilisateur None"""
        with self.assertRaises(ValueError):
            Review(
                text="Valid text",
                rating=4,
                user=None,  # Ne peut pas être None
                place=self.place
            )

    def test_review_creation_invalid_place(self):
        """Test la création d'une review avec un lieu non valide"""
        with self.assertRaises(ValueError):
            Review(
                text="Valid text",
                rating=4,
                user=self.user,
                place="not a place object"  # Doit être un objet Place
            )

    def test_review_creation_invalid_place_none(self):
        """Test la création d'une review avec un lieu None"""
        with self.assertRaises(ValueError):
            Review(
                text="Valid text",
                rating=4,
                user=self.user,
                place=None  # Ne peut pas être None
            )

    def test_save_method(self):
        """Test la méthode save() pour mettre à jour le timestamp"""
        review = Review(
            text="Test review",
            rating=4,
            user=self.user,
            place=self.place
        )
        
        # Enregistrer le timestamp initial
        original_updated_at = review.updated_at
        
        # Attendre un petit moment pour s'assurer que le timestamp change
        import time
        time.sleep(0.001)
        
        # Appeler la méthode save
        review.save()
        
        # Vérifier que le timestamp a été mis à jour
        self.assertNotEqual(review.updated_at, original_updated_at)

    def test_to_dict_method(self):
        """Test la méthode to_dict() pour la sérialisation"""
        review = Review(
            text="Test review for serialization",
            rating=3,
            user=self.user,
            place=self.place
        )
        
        # Obtenir le dictionnaire
        review_dict = review.to_dict()
        
        # Vérifier les clés du dictionnaire
        self.assertIn('id', review_dict)
        self.assertIn('text', review_dict)
        self.assertIn('rating', review_dict)
        self.assertIn('created_at', review_dict)
        self.assertIn('updated_at', review_dict)
        self.assertIn('__class__', review_dict)
        
        # Vérifier que les timestamps sont bien formatés en ISO
        self.assertIsInstance(review_dict['created_at'], str)
        self.assertIsInstance(review_dict['updated_at'], str)
        
        # Vérifier la valeur de __class__
        self.assertEqual(review_dict['__class__'], 'Review')
        
        # Vérifier les valeurs des attributs
        self.assertEqual(review_dict['text'], "Test review for serialization")
        self.assertEqual(review_dict['rating'], 3)

    def test_update_method(self):
        """Test la méthode update() pour mettre à jour les attributs"""
        review = Review(
            text="Initial review text",
            rating=4,
            user=self.user,
            place=self.place
        )
        
        # Mettre à jour le texte et la note
        data = {'text': 'Updated review text', 'rating': 3}
        review.update(data)
        
        # Vérifier que les attributs ont été mis à jour
        self.assertEqual(review.text, 'Updated review text')
        self.assertEqual(review.rating, 3)
        
        # Vérifier que le timestamp a été mis à jour
        self.assertIsInstance(review.updated_at, datetime)

    def test_update_method_with_invalid_attribute(self):
        """Test la méthode update() avec un attribut non existant"""
        review = Review(
            text="Test review",
            rating=4,
            user=self.user,
            place=self.place
        )
        
        # Essayer de mettre à jour un attribut non existant
        data = {'nonexistent_attribute': 'some value'}
        original_dict = review.to_dict()
        
        # L'update ne devrait pas lever d'erreur mais ignorer l'attribut non existant
        review.update(data)
        
        # Vérifier que l'attribut n'a pas été ajouté
        self.assertFalse(hasattr(review, 'nonexistent_attribute'))
        
        # Vérifier que le timestamp updated_at a été mis à jour
        updated_dict = review.to_dict()
        self.assertNotEqual(original_dict['updated_at'], updated_dict['updated_at'])

    def test_update_method_with_invalid_rating(self):
        """Test la méthode update() avec une note invalide"""
        review = Review(
            text="Test review",
            rating=4,
            user=self.user,
            place=self.place
        )
        
        # Essayer de mettre à jour avec une note invalide
        # Note: Ceci suppose que votre méthode update vérifie les contraintes de validation
        data = {'rating': 6}  # Note trop élevée
        
        # Si votre implémentation valide les données dans update(), cela devrait lever une erreur
        # Sinon, vous pourriez avoir besoin d'adapter ce test
        with self.assertRaises(ValueError):
            review.update(data)

if __name__ == '__main__':
    unittest.main()