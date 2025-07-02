from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.services import facade
import re

# Création du namespace pour regrouper les routes liées aux utilisateurs
api = Namespace('users', description='User operations')

# Définition du modèle de validation pour les requêtes
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password for the user account')
})

# Modèle pour mise à jour utilisateur (flexible selon le rôle)
user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(required=False, description='First name of the user'),
    'last_name': fields.String(required=False, description='Last name of the user'),
    'email': fields.String(required=False, description='Email of the user (admin only)'),
    'password': fields.String(required=False, description='Password of the user (admin only)')
})


@api.route('/')
class UserList(Resource):
    @api.response(200, 'Users retrieved successfully')
    @api.response(500, 'Internal server error')
    def get(self):
        """Get all users"""
        try:
            users = facade.get_all_users()
            return [{'id': user.id, 'first_name': user.first_name,
                     'last_name': user.last_name, 'email': user.email} for user in users], 200
        except Exception as e:
            print(f"Error retrieving users: {str(e)}")
            return {'error': 'An unexpected error occurred'}, 500


@api.route('/register')
class UserRegistration(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully registered')
    @api.response(400, 'Email already registered')
    @api.response(400, 'Invalid input data')
    @api.response(500, 'Internal server error')
    def post(self):
        """Public user registration (creates regular users only)"""
        try:
            user_data = api.payload
            
            # Pour l'inscription publique, toujours créer un utilisateur normal
            user_data['is_admin'] = False
    
            # Validation de l'email
            email_regex = re.compile(
                r'^(?!.*\.\.)(?!.*@.*@)[a-zA-Z0-9][a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
            if not email_regex.match(user_data.get('email', '')):
                return {'error': 'Invalid email format'}, 400

            # Vérification que l'email n'est pas déjà utilisé
            existing_user = facade.get_user_by_email(user_data['email'])
            if existing_user:
                return {'error': 'Email already registered'}, 400

            # Validation des champs
            if not user_data.get('first_name') or len(user_data['first_name']) > 50:
                return {'error': 'First name is required and must not exceed 50 characters'}, 400

            if not user_data.get('last_name') or len(user_data['last_name']) > 50:
                return {'error': 'Last name is required and must not exceed 50 characters'}, 400
            
            if not user_data.get('password') or len(user_data['password']) < 8:
                return {'error': 'Password is required and must be at least 8 characters long'}, 400

            # Création de l'utilisateur
            new_user = facade.create_user(user_data)
            return {
                'id': new_user.id, 
                'message': 'User successfully registered'
            }, 201
        
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return {'error': 'An unexpected error occurred'}, 500


@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user details by ID"""
        try:
            user = facade.get_user(user_id)
            if not user:
                return {'error': 'User not found'}, 404
            return {'id': user.id, 'first_name': user.first_name,
                    'last_name': user.last_name, 'email': user.email}, 200
        except Exception as e:
            print(f"Error retrieving user: {str(e)}")
            return {'error': 'An unexpected error occurred'}, 500

    @api.expect(user_update_model)
    @api.response(200, 'User successfully updated')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Access forbidden')
    @api.response(404, 'User not found')
    @api.response(500, 'Internal server error')
    @jwt_required()
    def put(self, user_id):
        """Update user details
        
        Regular users can only update their own first_name and last_name.
        Admins can update any user's details including email and password.
        """
        current_user = get_jwt_identity()

        try:
            # Vérifier que l'utilisateur modifie ses propres données (sauf si admin)
            if not current_user.get('is_admin', False) and current_user['id'] != user_id:
                return {'error': 'Access forbidden'}, 403
            
            # Vérifier que l'utilisateur existe
            user = facade.get_user(user_id)
            if not user:
                return {'error': 'User not found'}, 404

            user_data = api.payload

            # Validation des champs autorisés selon le rôle
            if not current_user.get('is_admin', False):
                # Utilisateurs normaux : seulement first_name et last_name
                if 'email' in user_data or 'password' in user_data:
                    return {'error': 'Regular users cannot modify email or password'}, 403
                allowed_fields = {'first_name', 'last_name'}
            else:
                # Admins : tous les champs
                allowed_fields = {'first_name', 'last_name', 'email', 'password'}

            provided_fields = set(user_data.keys())
            invalid_fields = provided_fields - allowed_fields
            
            if invalid_fields:
                return {'error': f'Invalid fields: {", ".join(invalid_fields)}'}, 400
            
            # Vérifier qu'au moins un champ est fourni
            if not provided_fields:
                return {'error': 'At least one field must be provided'}, 400

            # Validations spécifiques
            if 'first_name' in user_data:
                if not user_data['first_name'] or not user_data['first_name'].strip():
                    return {'error': 'First name cannot be empty'}, 400
                if len(user_data['first_name']) > 50:
                    return {'error': 'First name must not exceed 50 characters'}, 400

            if 'last_name' in user_data:
                if not user_data['last_name'] or not user_data['last_name'].strip():
                    return {'error': 'Last name cannot be empty'}, 400
                if len(user_data['last_name']) > 50:
                    return {'error': 'Last name must not exceed 50 characters'}, 400

            # Validations supplémentaires pour les admins
            if current_user.get('is_admin', False):
                if 'email' in user_data:
                    email_regex = re.compile(
                        r'^(?!.*\.\.)(?!.*@.*@)[a-zA-Z0-9][a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
                    if not email_regex.match(user_data['email']):
                        return {'error': 'Invalid email format'}, 400
                    
                    if user_data['email'] != user.email:
                        existing_user = facade.get_user_by_email(user_data['email'])
                        if existing_user and existing_user.id != user_id:
                            return {'error': 'Email already registered to another user'}, 400
                            
                if 'password' in user_data and len(user_data['password']) < 8:
                    return {'error': 'Password must be at least 8 characters long'}, 400

            # Mise à jour de l'utilisateur
            updated_user = facade.update_user(user_id, user_data)
            return {
                'id': updated_user.id, 
                'first_name': updated_user.first_name,
                'last_name': updated_user.last_name, 
                'email': updated_user.email
            }, 200
                    
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            print(f"Error updating user: {str(e)}")
            return {'error': 'An unexpected error occurred'}, 500


