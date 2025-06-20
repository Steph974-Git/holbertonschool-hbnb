import unittest
import sys
import os

# Ajout du chemin du projet au sys.path pour permettre l'importation des modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from app.models.amenity import Amenity
from datetime import datetime


class TestAmenityEndpoints(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        
        # Create a test amenity for use in tests
        response = self.client.post('/api/v1/amenities/', json={
            "name": "Test Amenity"
        })
        if response.status_code == 201:
            self.test_amenity_id = response.json.get('id')
        else:
            self.test_amenity_id = None

    def test_create_amenity(self):
        # Test creating a valid amenity
        response = self.client.post('/api/v1/amenities/', json={
            "name": "WiFi"
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json)
        self.assertEqual(response.json.get('name'), "WiFi")

    def test_create_amenity_invalid_data(self):
        # Test with empty name
        response = self.client.post('/api/v1/amenities/', json={
            "name": ""
        })
        self.assertEqual(response.status_code, 400)
        
        # Test with name too long (over 50 characters)
        response = self.client.post('/api/v1/amenities/', json={
            "name": "A" * 51
        })
        self.assertEqual(response.status_code, 400)
        
        # Test with missing name field
        response = self.client.post('/api/v1/amenities/', json={})
        self.assertEqual(response.status_code, 400)

    def test_get_all_amenities(self):
        # Test getting all amenities
        response = self.client.get('/api/v1/amenities/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_amenity_by_id(self):
        # Skip test if no test amenity was created
        if not self.test_amenity_id:
            self.skipTest("No test amenity available")
            
        # Test getting a specific amenity
        response = self.client.get(f'/api/v1/amenities/{self.test_amenity_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get('id'), self.test_amenity_id)
        self.assertEqual(response.json.get('name'), "Test Amenity")
        
        # Test getting a non-existent amenity
        response = self.client.get('/api/v1/amenities/nonexistent-id')
        self.assertEqual(response.status_code, 404)

    def test_update_amenity(self):
        # Skip test if no test amenity was created
        if not self.test_amenity_id:
            self.skipTest("No test amenity available")
            
        # Test updating an amenity
        response = self.client.put(f'/api/v1/amenities/{self.test_amenity_id}', json={
            "name": "Updated Amenity"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get('name'), "Updated Amenity")
        
        # Test updating with invalid data
        response = self.client.put(f'/api/v1/amenities/{self.test_amenity_id}', json={
            "name": ""
        })
        self.assertEqual(response.status_code, 400)
        
        # Test updating a non-existent amenity
        response = self.client.put('/api/v1/amenities/nonexistent-id', json={
            "name": "Valid Name"
        })
        self.assertEqual(response.status_code, 404)

    def test_delete_amenity(self):
        # Create a temporary amenity to delete
        response = self.client.post('/api/v1/amenities/', json={
            "name": "Temporary Amenity"
        })
        if response.status_code != 201:
            self.skipTest("Failed to create temporary amenity for delete test")
        
        temp_id = response.json.get('id')
        
        # Test deleting the amenity
        response = self.client.delete(f'/api/v1/amenities/{temp_id}')
        self.assertEqual(response.status_code, 204)
        
        # Verify it was deleted by trying to get it
        response = self.client.get(f'/api/v1/amenities/{temp_id}')
        self.assertEqual(response.status_code, 404)
        
        # Test deleting a non-existent amenity
        response = self.client.delete('/api/v1/amenities/nonexistent-id')
        self.assertEqual(response.status_code, 404)

class TestAmenity(unittest.TestCase):
    """Tests pour la classe Amenity"""

    def test_amenity_creation_with_valid_name(self):
        """Test la création d'un équipement avec un nom valide"""
        amenity = Amenity(name="WiFi")
        
        # Vérifier que l'objet est correctement initialisé
        self.assertEqual(amenity.name, "WiFi")
        
        # Vérifier les attributs hérités de BaseModel
        self.assertIsNotNone(amenity.id)
        self.assertIsInstance(amenity.created_at, datetime)
        self.assertIsInstance(amenity.updated_at, datetime)

    def test_amenity_creation_with_empty_name(self):
        """Test la création d'un équipement avec un nom vide"""
        with self.assertRaises(ValueError):
            Amenity(name="")

    def test_amenity_creation_with_long_name(self):
        """Test la création d'un équipement avec un nom trop long"""
        # Créer un nom de 51 caractères (la limite est de 50)
        long_name = "A" * 51
        with self.assertRaises(ValueError):
            Amenity(name=long_name)

    def test_amenity_creation_with_max_length_name(self):
        """Test la création d'un équipement avec un nom de longueur maximale"""
        # Créer un nom de 50 caractères (la limite exacte)
        max_name = "A" * 50
        amenity = Amenity(name=max_name)
        self.assertEqual(amenity.name, max_name)

    def test_amenity_creation_with_special_characters(self):
        """Test la création d'un équipement avec des caractères spéciaux"""
        special_name = "WiFi - High Speed (5G)! #Premium"
        amenity = Amenity(name=special_name)
        self.assertEqual(amenity.name, special_name)

    def test_save_method(self):
        """Test la méthode save() pour mettre à jour le timestamp"""
        amenity = Amenity(name="Pool")
        
        # Enregistrer le timestamp initial
        original_updated_at = amenity.updated_at
        
        # Attendre un petit moment pour s'assurer que le timestamp change
        import time
        time.sleep(0.001)
        
        # Appeler la méthode save
        amenity.save()
        
        # Vérifier que le timestamp a été mis à jour
        self.assertNotEqual(amenity.updated_at, original_updated_at)

    def test_to_dict_method(self):
        """Test la méthode to_dict() pour la sérialisation"""
        amenity = Amenity(name="Air Conditioning")
        
        # Obtenir le dictionnaire
        amenity_dict = amenity.to_dict()
        
        # Vérifier les clés du dictionnaire
        self.assertIn('id', amenity_dict)
        self.assertIn('name', amenity_dict)
        self.assertIn('created_at', amenity_dict)
        self.assertIn('updated_at', amenity_dict)
        self.assertIn('__class__', amenity_dict)
        
        # Vérifier que les timestamps sont bien formatés en ISO
        self.assertIsInstance(amenity_dict['created_at'], str)
        self.assertIsInstance(amenity_dict['updated_at'], str)
        
        # Vérifier la valeur de __class__
        self.assertEqual(amenity_dict['__class__'], 'Amenity')
        
        # Vérifier les valeurs des attributs
        self.assertEqual(amenity_dict['name'], "Air Conditioning")

    def test_update_method(self):
        """Test la méthode update() pour mettre à jour les attributs"""
        amenity = Amenity(name="Kitchen")
        
        # Mettre à jour le nom
        data = {'name': 'Full Kitchen'}
        amenity.update(data)
        
        # Vérifier que le nom a été mis à jour
        self.assertEqual(amenity.name, 'Full Kitchen')
        
        # Vérifier que le timestamp a été mis à jour (via la méthode save appelée par update)
        self.assertIsInstance(amenity.updated_at, datetime)

    def test_update_method_with_invalid_attribute(self):
        """Test la méthode update() avec un attribut non existant"""
        amenity = Amenity(name="Gym")
        
        # Essayer de mettre à jour un attribut non existant
        data = {'nonexistent_attribute': 'some value'}
        original_dict = amenity.to_dict()
        
        # L'update ne devrait pas lever d'erreur mais ignorer l'attribut non existant
        amenity.update(data)
        
        # Vérifier que l'attribut n'a pas été ajouté
        self.assertFalse(hasattr(amenity, 'nonexistent_attribute'))
        
        # Vérifier que le timestamp updated_at a été mis à jour
        updated_dict = amenity.to_dict()
        self.assertNotEqual(original_dict['updated_at'], updated_dict['updated_at'])

if __name__ == '__main__':
    unittest.main()