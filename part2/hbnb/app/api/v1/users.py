from flask_restx import Namespace, Resource, fields
from app.services import facade
import re

api = Namespace('users', description='User operations')

# Define the user model for input validation and documentation
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user')
})

@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered')
    @api.response(400, 'Invalid input data')
    @api.response(500, 'Internal server error')
    def post(self):
        """Register a new user"""
        try:
            user_data = api.payload

            email_regex = re.compile(r'^(?!.*\.\.)(?!.*@.*@)[a-zA-Z0-9][a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
            if not email_regex.match(user_data.get('email', '')):
                return {'error': 'Invalid email format'}, 400
        
            existing_user = facade.get_user_by_email(user_data['email'])
            if existing_user:
                return {'error': 'Email already registered'}, 400

            if not user_data.get('first_name') or len(user_data['first_name']) > 50:
                return {'error': 'First name is required and must not exceed 50 characters'}, 400

            if not user_data.get('last_name') or len(user_data['last_name']) > 50:
                return {'error': 'Last name is required and must not exceed 50 characters'}, 400

            new_user = facade.create_user(user_data)
            return {'id': new_user.id, 'first_name': new_user.first_name, 'last_name': new_user.last_name, 'email': new_user.email}, 201
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return {'error': 'An unexpected error occurred'}, 500
        
    @api.response(200, 'Users retrieved successfully')
    @api.response(500, 'Internal server error')
    def get(self):
        """Get all users"""
        try:
            users = facade.get_all_users()
            return [{'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email} for user in users], 200
        except Exception as e:
            print(f"Error retrieving users: {str(e)}")
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
            return {'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email}, 200
        except Exception as e:
            print(f"Error retrieving user: {str(e)}")
            return {'error': 'An unexpected error occurred'}, 500
    
    @api.response(200, 'User successfully updated')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'User not found')
    @api.response(500, 'Internal server error')
    @api.expect(user_model)  # Supprimer validate=True
    def put(self, user_id):
        try:
            user = facade.get_user(user_id)
            if not user:
                return {'error': 'user not found'}, 404
            
            user_data = api.payload
            
            # Validation manuelle des champs présents
            if 'email' in user_data:
                email_regex = re.compile(r'^(?!.*\.\.)(?!.*@.*@)[a-zA-Z0-9][a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
                if not email_regex.match(user_data['email']):
                    return {'error': 'Invalid email format'}, 400
                    
                # Vérifier que l'email n'est pas déjà pris
                if user_data['email'] != user.email:
                    existing_user = facade.get_user_by_email(user_data['email'])
                    if existing_user and existing_user.id != user_id:
                        return {'error': 'Email already registered to another user'}, 400
            
            # Reste des validations
            if 'first_name' in user_data and (not user_data['first_name'] or len(user_data['first_name']) > 50):
                return {'error': 'First name is required and must not exceed 50 characters'}, 400

            if 'last_name' in user_data and (not user_data['last_name'] or len(user_data['last_name']) > 50):
                return {'error': 'Last name must not exceed 50 characters'}, 400

            # Mise à jour
            updated_user = facade.update_user(user_id, user_data)
            return {'id': updated_user.id, 'first_name': updated_user.first_name, 'last_name': updated_user.last_name, 'email': updated_user.email}, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            print(f"Error updating user: {str(e)}")
            return {'error': 'An unexpected error occurred'}, 500
