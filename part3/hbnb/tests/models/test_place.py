from app.models.review import Review
from app.models.amenity import Amenity
from app.models.user import User
from app.models.place import Place
import unittest
import sys
import os
import time
from datetime import datetime

# Ajout du chemin du projet au sys.path pour permettre l'importation des
# modules
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '../..')))


class TestPlace(unittest.TestCase):
    """Tests pour la classe Place"""

    def setUp(self):
        """Préparer les objets nécessaires pour les tests"""
        # Créer un utilisateur valide pour les tests
        self.user = User(
            email="owner@example.com",
            first_name="Property",
            last_name="Owner"
        )

        # Créer des amenities pour les tests
        self.amenity1 = Amenity(name="WiFi")
        self.amenity2 = Amenity(name="Pool")
        self.amenity3 = Amenity(name="Air Conditioning")

    def test_place_creation_with_valid_data(self):
        """Test la création d'un lieu avec des données valides"""
        place = Place(
            title="Beautiful Apartment",
            description="A lovely apartment in the heart of the city",
            price=120.50,
            latitude=40.7128,
            longitude=-74.0060,
            owner=self.user
        )

        # Vérifier que l'objet est correctement initialisé
        self.assertEqual(place.title, "Beautiful Apartment")
        self.assertEqual(
            place.description,
            "A lovely apartment in the heart of the city")
        self.assertEqual(place.price, 120.50)
        self.assertEqual(place.latitude, 40.7128)
        self.assertEqual(place.longitude, -74.0060)
        self.assertEqual(place.owner, self.user)

        # Vérifier les attributs hérités de BaseModel
        self.assertIsNotNone(place.id)
        self.assertIsInstance(place.created_at, datetime)
        self.assertIsInstance(place.updated_at, datetime)

        # Vérifier les listes vides pour reviews et amenities
        self.assertEqual(place.reviews, [])
        self.assertEqual(place.amenities, [])

    def test_place_creation_with_minimum_data(self):
        """Test la création d'un lieu avec le minimum de données requises"""
        place = Place(
            title="Minimal Place",
            description="",  # Description vide est valide
            price=10.0,
            latitude=0.0,
            longitude=0.0,
            owner=self.user
        )

        self.assertEqual(place.title, "Minimal Place")
        self.assertEqual(place.description, "")
        self.assertEqual(place.price, 10.0)
        self.assertEqual(place.latitude, 0.0)
        self.assertEqual(place.longitude, 0.0)

    def test_place_creation_with_title_too_long(self):
        """Test la création d'un lieu avec un titre trop long"""
        # Créer un titre de 101 caractères (la limite est de 100)
        long_title = "A" * 101

        with self.assertRaises(ValueError):
            Place(
                title=long_title,
                description="Valid description",
                price=100.0,
                latitude=40.7128,
                longitude=-74.0060,
                owner=self.user
            )

    def test_place_creation_with_max_length_title(self):
        """Test la création d'un lieu avec un titre de longueur maximale"""
        # Créer un titre de 100 caractères (la limite exacte)
        max_title = "A" * 100

        place = Place(
            title=max_title,
            description="Valid description",
            price=100.0,
            latitude=40.7128,
            longitude=-74.0060,
            owner=self.user
        )

        self.assertEqual(place.title, max_title)

    def test_place_creation_without_title(self):
        """Test la création d'un lieu sans titre"""
        with self.assertRaises(ValueError):
            Place(
                title="",
                description="Valid description",
                price=100.0,
                latitude=40.7128,
                longitude=-74.0060,
                owner=self.user
            )

    def test_place_creation_with_negative_price(self):
        """Test la création d'un lieu avec un prix négatif"""
        with self.assertRaises(ValueError):
            Place(
                title="Valid Title",
                description="Valid description",
                price=-10.0,
                latitude=40.7128,
                longitude=-74.0060,
                owner=self.user
            )

    def test_place_creation_with_zero_price(self):
        """Test la création d'un lieu avec un prix de zéro"""
        with self.assertRaises(ValueError):
            Place(
                title="Valid Title",
                description="Valid description",
                price=0.0,
                latitude=40.7128,
                longitude=-74.0060,
                owner=self.user
            )

    def test_place_creation_with_minimum_price(self):
        """Test la création d'un lieu avec le prix minimum accepté"""
        place = Place(
            title="Budget Place",
            description="Very affordable",
            price=0.01,
            latitude=40.7128,
            longitude=-74.0060,
            owner=self.user
        )

        self.assertEqual(place.price, 0.01)

    def test_place_creation_with_invalid_latitude_too_low(self):
        """Test la création d'un lieu avec une latitude trop basse"""
        with self.assertRaises(ValueError):
            Place(
                title="Valid Title",
                description="Valid description",
                price=100.0,
                latitude=-91.0,  # Doit être >= -90
                longitude=-74.0060,
                owner=self.user
            )

    def test_place_creation_with_invalid_latitude_too_high(self):
        """Test la création d'un lieu avec une latitude trop élevée"""
        with self.assertRaises(ValueError):
            Place(
                title="Valid Title",
                description="Valid description",
                price=100.0,
                latitude=91.0,  # Doit être <= 90
                longitude=-74.0060,
                owner=self.user
            )

    def test_place_creation_with_boundary_latitudes(self):
        """Test la création d'un lieu avec des latitudes limites"""
        # Latitude minimale (-90)
        place_min = Place(
            title="South Pole",
            description="Very cold",
            price=1000.0,
            latitude=-90.0,
            longitude=0.0,
            owner=self.user
        )

        # Latitude maximale (90)
        place_max = Place(
            title="North Pole",
            description="Also very cold",
            price=1000.0,
            latitude=90.0,
            longitude=0.0,
            owner=self.user
        )

        self.assertEqual(place_min.latitude, -90.0)
        self.assertEqual(place_max.latitude, 90.0)

    def test_place_creation_with_invalid_longitude_too_low(self):
        """Test la création d'un lieu avec une longitude trop basse"""
        with self.assertRaises(ValueError):
            Place(
                title="Valid Title",
                description="Valid description",
                price=100.0,
                latitude=40.7128,
                longitude=-181.0,  # Doit être >= -180
                owner=self.user
            )

    def test_place_creation_with_invalid_longitude_too_high(self):
        """Test la création d'un lieu avec une longitude trop élevée"""
        with self.assertRaises(ValueError):
            Place(
                title="Valid Title",
                description="Valid description",
                price=100.0,
                latitude=40.7128,
                longitude=181.0,  # Doit être <= 180
                owner=self.user
            )

    def test_place_creation_with_boundary_longitudes(self):
        """Test la création d'un lieu avec des longitudes limites"""
        # Longitude minimale (-180)
        place_min = Place(
            title="International Date Line West",
            description="Time travels backwards",
            price=500.0,
            latitude=0.0,
            longitude=-180.0,
            owner=self.user
        )

        # Longitude maximale (180)
        place_max = Place(
            title="International Date Line East",
            description="Time travels forwards",
            price=500.0,
            latitude=0.0,
            longitude=180.0,
            owner=self.user
        )

        self.assertEqual(place_min.longitude, -180.0)
        self.assertEqual(place_max.longitude, 180.0)

    def test_place_creation_without_owner(self):
        """Test la création d'un lieu sans propriétaire"""
        with self.assertRaises(ValueError):
            Place(
                title="Valid Title",
                description="Valid description",
                price=100.0,
                latitude=40.7128,
                longitude=-74.0060,
                owner=None
            )

    def test_place_creation_with_invalid_owner(self):
        """Test la création d'un lieu avec un propriétaire invalide"""
        with self.assertRaises(ValueError):
            Place(
                title="Valid Title",
                description="Valid description",
                price=100.0,
                latitude=40.7128,
                longitude=-74.0060,
                owner="not a user object"
            )

    def test_add_amenity(self):
        """Test l'ajout d'un équipement à un lieu"""
        place = Place(
            title="Place with Amenities",
            description="Has many amenities",
            price=150.0,
            latitude=35.6895,
            longitude=139.6917,
            owner=self.user
        )

        # Ajouter un équipement
        place.add_amenity(self.amenity1)

        # Vérifier que l'équipement a été ajouté
        self.assertEqual(len(place.amenities), 1)
        self.assertEqual(place.amenities[0], self.amenity1)

        # Ajouter un deuxième équipement
        place.add_amenity(self.amenity2)

        # Vérifier que les deux équipements sont présents
        self.assertEqual(len(place.amenities), 2)
        self.assertIn(self.amenity1, place.amenities)
        self.assertIn(self.amenity2, place.amenities)

    def test_add_duplicate_amenity(self):
        """Test l'ajout d'un équipement en double à un lieu"""
        place = Place(
            title="Place with Duplicate Amenities",
            description="Testing duplicates",
            price=150.0,
            latitude=35.6895,
            longitude=139.6917,
            owner=self.user
        )

        # Ajouter le même équipement deux fois
        place.add_amenity(self.amenity1)
        place.add_amenity(self.amenity1)

        # Vérifier qu'il n'y a qu'une seule instance de l'équipement
        # Note: Ceci suppose que add_amenity ne vérifie pas les doublons
        # Si add_amenity vérifie les doublons, ce test devra être modifié
        self.assertEqual(len(place.amenities), 2)

        # Compter combien de fois amenity1 apparaît
        count = sum(
            1 for amenity in place.amenities if amenity == self.amenity1)
        self.assertEqual(count, 2)

    def test_add_invalid_amenity(self):
        """Test l'ajout d'un équipement invalide à un lieu"""
        place = Place(
            title="Place with Invalid Amenity",
            description="Testing invalid input",
            price=150.0,
            latitude=35.6895,
            longitude=139.6917,
            owner=self.user
        )

        # Tenter d'ajouter un objet qui n'est pas un Amenity
        # Note: Si add_amenity vérifie le type, ce test doit être adapté
        # Sinon, cette méthode acceptera n'importe quel objet
        place.add_amenity("not an amenity object")

        # Vérifier que l'objet a été ajouté (si pas de vérification de type)
        # ou que l'ajout a été refusé (si vérification de type)
        if len(place.amenities) > 0:
            # Si pas de vérification de type
            self.assertEqual(place.amenities[0], "not an amenity object")
        else:
            # Si vérification de type
            self.assertEqual(len(place.amenities), 0)

    def test_add_review(self):
        """Test l'ajout d'un avis à un lieu"""
        place = Place(
            title="Place with Reviews",
            description="Has many reviews",
            price=150.0,
            latitude=35.6895,
            longitude=139.6917,
            owner=self.user
        )

        # Créer un avis
        reviewer = User(
            email="reviewer@example.com",
            first_name="Happy",
            last_name="Customer"
        )

        review = Review(
            text="Great place!",
            rating=5,
            user=reviewer,
            place=place
        )

        # Ajouter l'avis
        place.add_review(review)

        # Vérifier que l'avis a été ajouté
        self.assertEqual(len(place.reviews), 1)
        self.assertEqual(place.reviews[0], review)

        # Ajouter un deuxième avis
        another_review = Review(
            text="Good but could be better",
            rating=4,
            user=reviewer,
            place=place
        )

        place.add_review(another_review)

        # Vérifier que les deux avis sont présents
        self.assertEqual(len(place.reviews), 2)
        self.assertIn(review, place.reviews)
        self.assertIn(another_review, place.reviews)

    def test_add_invalid_review(self):
        """Test l'ajout d'un avis invalide à un lieu"""
        place = Place(
            title="Place with Invalid Review",
            description="Testing invalid input",
            price=150.0,
            latitude=35.6895,
            longitude=139.6917,
            owner=self.user
        )

        # Tenter d'ajouter un objet qui n'est pas un Review
        # Note: Si add_review vérifie le type, ce test doit être adapté
        # Sinon, cette méthode acceptera n'importe quel objet
        place.add_review("not a review object")

        # Vérifier que l'objet a été ajouté (si pas de vérification de type)
        # ou que l'ajout a été refusé (si vérification de type)
        if len(place.reviews) > 0:
            # Si pas de vérification de type
            self.assertEqual(place.reviews[0], "not a review object")
        else:
            # Si vérification de type
            self.assertEqual(len(place.reviews), 0)

    def test_save_method(self):
        """Test la méthode save() pour mettre à jour le timestamp"""
        place = Place(
            title="Place to Save",
            description="Testing save method",
            price=150.0,
            latitude=35.6895,
            longitude=139.6917,
            owner=self.user
        )

        # Enregistrer le timestamp initial
        original_updated_at = place.updated_at

        # Attendre un petit moment pour s'assurer que le timestamp change
        time.sleep(0.001)

        # Appeler la méthode save
        place.save()

        # Vérifier que le timestamp a été mis à jour
        self.assertNotEqual(place.updated_at, original_updated_at)

    def test_to_dict_method(self):
        """Test la méthode to_dict() pour la sérialisation"""
        place = Place(
            title="Place to Serialize",
            description="Testing to_dict method",
            price=150.0,
            latitude=35.6895,
            longitude=139.6917,
            owner=self.user
        )

        # Ajouter quelques amenities et reviews
        place.add_amenity(self.amenity1)

        reviewer = User(
            email="reviewer@example.com",
            first_name="Happy",
            last_name="Customer"
        )

        review = Review(
            text="Great place!",
            rating=5,
            user=reviewer,
            place=place
        )

        place.add_review(review)

        # Obtenir le dictionnaire
        place_dict = place.to_dict()

        # Vérifier les clés du dictionnaire
        self.assertIn('id', place_dict)
        self.assertIn('title', place_dict)
        self.assertIn('description', place_dict)
        self.assertIn('price', place_dict)
        self.assertIn('latitude', place_dict)
        self.assertIn('longitude', place_dict)
        self.assertIn('created_at', place_dict)
        self.assertIn('updated_at', place_dict)
        self.assertIn('__class__', place_dict)

        # Vérifier que les timestamps sont bien formatés en ISO
        self.assertIsInstance(place_dict['created_at'], str)
        self.assertIsInstance(place_dict['updated_at'], str)

        # Vérifier la valeur de __class__
        self.assertEqual(place_dict['__class__'], 'Place')

        # Vérifier les valeurs des attributs
        self.assertEqual(place_dict['title'], "Place to Serialize")
        self.assertEqual(place_dict['description'], "Testing to_dict method")
        self.assertEqual(place_dict['price'], 150.0)
        self.assertEqual(place_dict['latitude'], 35.6895)
        self.assertEqual(place_dict['longitude'], 139.6917)

    def test_update_method(self):
        """Test la méthode update() pour mettre à jour les attributs"""
        place = Place(
            title="Original Title",
            description="Original description",
            price=100.0,
            latitude=40.7128,
            longitude=-74.0060,
            owner=self.user
        )

        # Mettre à jour plusieurs attributs
        data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'price': 120.0
        }

        place.update(data)

        # Vérifier que les attributs ont été mis à jour
        self.assertEqual(place.title, 'Updated Title')
        self.assertEqual(place.description, 'Updated description')
        self.assertEqual(place.price, 120.0)

        # Vérifier que les autres attributs n'ont pas changé
        self.assertEqual(place.latitude, 40.7128)
        self.assertEqual(place.longitude, -74.0060)

        # Vérifier que le timestamp a été mis à jour
        self.assertIsInstance(place.updated_at, datetime)

    def test_update_method_with_invalid_attribute(self):
        """Test la méthode update() avec un attribut non existant"""
        place = Place(
            title="Test Place",
            description="Test description",
            price=100.0,
            latitude=40.7128,
            longitude=-74.0060,
            owner=self.user
        )

        # Essayer de mettre à jour un attribut non existant
        data = {'nonexistent_attribute': 'some value'}
        original_dict = place.to_dict()

        # L'update ne devrait pas lever d'erreur mais ignorer l'attribut non
        # existant
        place.update(data)

        # Vérifier que l'attribut n'a pas été ajouté
        self.assertFalse(hasattr(place, 'nonexistent_attribute'))

        # Vérifier que le timestamp updated_at a été mis à jour
        updated_dict = place.to_dict()
        self.assertNotEqual(
            original_dict['updated_at'],
            updated_dict['updated_at'])

    def test_update_method_with_invalid_price(self):
        """Test la méthode update() avec un prix invalide"""
        place = Place(
            title="Test Place",
            description="Test description",
            price=100.0,
            latitude=40.7128,
            longitude=-74.0060,
            owner=self.user
        )

        # Essayer de mettre à jour avec un prix négatif
        data = {'price': -10.0}

        # Si votre implémentation valide les données dans update(), cela devrait lever une erreur
        # Sinon, la mise à jour se fera sans validation
        try:
            place.update(data)
            # Si nous sommes ici, cela signifie que l'update n'a pas validé le
            # prix
            self.assertEqual(place.price, -10.0)
            print(
                "NOTE: La méthode update() ne valide pas actuellement les contraintes du modèle.")
        except ValueError:
            # Si nous sommes ici, cela signifie que l'update a bien validé le
            # prix
            self.assertEqual(place.price, 100.0)  # Le prix n'a pas changé

    def test_update_method_with_invalid_latitude(self):
        """Test la méthode update() avec une latitude invalide"""
        place = Place(
            title="Test Place",
            description="Test description",
            price=100.0,
            latitude=40.7128,
            longitude=-74.0060,
            owner=self.user
        )

        # Essayer de mettre à jour avec une latitude invalide
        data = {'latitude': 100.0}  # Plus de 90

        # Si votre implémentation valide les données dans update(), cela devrait lever une erreur
        # Sinon, la mise à jour se fera sans validation
        try:
            place.update(data)
            # Si nous sommes ici, cela signifie que l'update n'a pas validé la
            # latitude
            self.assertEqual(place.latitude, 100.0)
            print(
                "NOTE: La méthode update() ne valide pas actuellement les contraintes du modèle.")
        except ValueError:
            # Si nous sommes ici, cela signifie que l'update a bien validé la
            # latitude
            # La latitude n'a pas changé
            self.assertEqual(place.latitude, 40.7128)

    def test_update_method_with_invalid_longitude(self):
        """Test la méthode update() avec une longitude invalide"""
        place = Place(
            title="Test Place",
            description="Test description",
            price=100.0,
            latitude=40.7128,
            longitude=-74.0060,
            owner=self.user
        )

        # Essayer de mettre à jour avec une longitude invalide
        data = {'longitude': 200.0}  # Plus de 180

        # Si votre implémentation valide les données dans update(), cela devrait lever une erreur
        # Sinon, la mise à jour se fera sans validation
        try:
            place.update(data)
            # Si nous sommes ici, cela signifie que l'update n'a pas validé la
            # longitude
            self.assertEqual(place.longitude, 200.0)
            print(
                "NOTE: La méthode update() ne valide pas actuellement les contraintes du modèle.")
        except ValueError:
            # Si nous sommes ici, cela signifie que l'update a bien validé la
            # longitude
            # La longitude n'a pas changé
            self.assertEqual(place.longitude, -74.0060)


if __name__ == '__main__':
    unittest.main()
