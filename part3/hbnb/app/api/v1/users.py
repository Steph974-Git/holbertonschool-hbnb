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

# CORRECTION: Modèle UNIQUEMENT pour first_name et last_name
user_input_model = api.model('UserInput', {
    'first_name': fields.String(required=False, description='First name of the user'),
    'last_name': fields.String(required=False, description='Last name of the user')
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

    @api.expect(user_input_model)
    @api.response(200, 'User successfully updated')
    @api.response(403, 'Access denied')
    @api.response(404, 'User not found')
    @jwt_required()
    def put(self, user_id):
        """Update user information (TASK REQUIREMENT: no email/password modification)"""
        current_user = get_jwt_identity()

        try:
            # TASK REQUIREMENT: Vérifier que l'utilisateur modifie ses propres données
            if current_user['id'] != user_id:
                return {'error': 'Unauthorized action'}, 403
            
            # Vérifier que l'utilisateur existe
            user = facade.get_user(user_id)
            if not user:
                return {'error': 'User not found'}, 404

            user_data = api.payload

            # TASK REQUIREMENT: Empêcher la modification de email et password
            if 'email' in user_data or 'password' in user_data:
                return {'error': 'You cannot modify email or password'}, 400

            # Seuls first_name et last_name sont autorisés (+ autres champs non email/password)
            allowed_fields = {'first_name', 'last_name'}
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


