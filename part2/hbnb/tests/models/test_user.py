import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
import unittest
import json
from app import create_app

class TestUserEndpoints(unittest.TestCase):

    def setUp(self):
        """Configure l'environnement de test avant chaque test"""
        self.app = create_app()
        self.client = self.app.test_client()
        self.headers = {"Content-Type": "application/json"}
        
        # Générer un email unique
        import uuid
        unique_email = f"test.user.{uuid.uuid4()}@example.com"
        self.test_user_email = unique_email  # Stocker l'email pour les tests
        
        user_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": unique_email
        }
        response = self.client.post(
            '/api/v1/users/', 
            headers=self.headers,
            json=user_data
        )
        
        print(f"Test user creation response: {response.status_code}")
        print(f"Response data: {response.data}")
        
        data = json.loads(response.data)
        self.test_user_id = data.get('id')
        print(f"Test user ID: {self.test_user_id}")

    def test_create_user(self):
        """Test la création d'un utilisateur avec des données valides"""
        response = self.client.post(
            '/api/v1/users/', 
            headers=self.headers,
            json={
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@example.com"
            }
        )
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data["first_name"], "Jane")
        self.assertEqual(data["last_name"], "Doe")
        self.assertEqual(data["email"], "jane.doe@example.com")
        self.assertIn("id", data)

    def test_create_user_missing_fields(self):
        """Test la création d'un utilisateur avec des champs manquants"""
        # Test sans first_name
        response = self.client.post(
            '/api/v1/users/', 
            headers=self.headers,
            json={
                "last_name": "Doe",
                "email": "no.first@example.com"
            }
        )
        self.assertEqual(response.status_code, 400)
        
        # Test sans last_name
        response = self.client.post(
            '/api/v1/users/', 
            headers=self.headers,
            json={
                "first_name": "Jane",
                "email": "no.last@example.com"
            }
        )
        self.assertEqual(response.status_code, 400)
        
        # Test sans email
        response = self.client.post(
            '/api/v1/users/', 
            headers=self.headers,
            json={
                "first_name": "Jane",
                "last_name": "Doe"
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_create_user_empty_fields(self):
        """Test la création d'un utilisateur avec des champs vides"""
        response = self.client.post(
            '/api/v1/users/', 
            headers=self.headers,
            json={
                "first_name": "",
                "last_name": "",
                "email": "valid@example.com"
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_create_user_invalid_email(self):
        """Test la création d'un utilisateur avec un email invalide"""
        invalid_emails = [
            "invalid-email",   # Sans @
            "email@",          # Sans domaine
            "@domain.com",     # Sans nom local
            "email@domain.",   # TLD vide
            "email@.com",      # Domaine vide
            "email with spaces@domain.com",  # Espaces dans partie locale
            "email@domain@.com", # Multiple @
            "email..double@domain.com" # Points consécutifs
        ]
        
        for email in invalid_emails:
            with self.subTest(email=email):
                response = self.client.post(
                    '/api/v1/users/', 
                    headers=self.headers,
                    json={
                        "first_name": "Jane",
                        "last_name": "Doe",
                        "email": email
                    }
                )
                self.assertEqual(response.status_code, 400)
                data = json.loads(response.data)
                self.assertIn("error", data)

    def test_create_user_duplicate_email(self):
        """Test la création d'un utilisateur avec un email déjà utilisé"""
        # Premier utilisateur
        self.client.post(
            '/api/v1/users/', 
            headers=self.headers,
            json={
                "first_name": "Original",
                "last_name": "User",
                "email": "duplicate@example.com"
            }
        )
        
        # Tentative avec email dupliqué
        response = self.client.post(
            '/api/v1/users/', 
            headers=self.headers,
            json={
                "first_name": "Duplicate",
                "last_name": "User",
                "email": "duplicate@example.com"
            }
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_get_all_users(self):
        """Test la récupération de tous les utilisateurs"""
        response = self.client.get('/api/v1/users/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)  # Au moins l'utilisateur de test

    def test_get_specific_user(self):
        """Test la récupération d'un utilisateur spécifique"""
        response = self.client.get(f'/api/v1/users/{self.test_user_id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data["id"], self.test_user_id)
        self.assertEqual(data["first_name"], "Test")
        self.assertEqual(data["last_name"], "User")
        self.assertEqual(data["email"], self.test_user_email)  # Utiliser l'email stocké

    def test_get_nonexistent_user(self):
        """Test la récupération d'un utilisateur qui n'existe pas"""
        response = self.client.get('/api/v1/users/nonexistent-id')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_update_user(self):
        """Test la mise à jour d'un utilisateur"""
        response = self.client.put(
            f'/api/v1/users/{self.test_user_id}',
            headers=self.headers,
            json={
                "first_name": "Updated",
                "last_name": "Name",
                "email": "updated@example.com"
            }
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data["first_name"], "Updated")
        self.assertEqual(data["last_name"], "Name")
        self.assertEqual(data["email"], "updated@example.com")

    def test_update_user_partial(self):
        """Test la mise à jour partielle d'un utilisateur"""
        response = self.client.put(
            f'/api/v1/users/{self.test_user_id}',
            headers=self.headers,
            json={
                "first_name": "PartialUpdate"
            }
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data["first_name"], "PartialUpdate")
        self.assertEqual(data["last_name"], "User")  # Inchangé
        self.assertEqual(data["email"], self.test_user_email)  # Utiliser l'email stocké

    def test_update_nonexistent_user(self):
        """Test la mise à jour d'un utilisateur qui n'existe pas"""
        response = self.client.put(
            '/api/v1/users/nonexistent-id',
            headers=self.headers,
            json={
                "first_name": "Update",
                "last_name": "Fail",
                "email": "update.fail@example.com"
            }
        )
        self.assertEqual(response.status_code, 404)

    def test_update_user_invalid_email(self):
        """Test la mise à jour d'un utilisateur avec un email invalide"""
        response = self.client.put(
            f'/api/v1/users/{self.test_user_id}',
            headers=self.headers,
            json={
                "first_name": "Test",  # Ajouté pour éviter les erreurs de validation
                "last_name": "User",   # Ajouté pour éviter les erreurs de validation
                "email": "invalid-email"
            }
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        
        # Accepter différentes structures d'erreur
        self.assertTrue('error' in data or 'errors' in data or 'message' in data)

if __name__ == '__main__':
    unittest.main()