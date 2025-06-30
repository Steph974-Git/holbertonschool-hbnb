from flask_restx import Namespace, Resource, fields
from app.services import facade
import re

# Création du namespace pour regrouper les routes liées aux utilisateurs
api = Namespace('users', description='User operations')

# Définition du modèle de validation pour les requêtes
user_model = api.model('User', {
    'first_name': fields.String(required=True,
                                description='First name of the user'),
    'last_name': fields.String(required=True,
                               description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password for the user account')
})


@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered')
    @api.response(400, 'Invalid input data')
    @api.response(500, 'Internal server error')
    def post(self):
        """Register a new user.

        Creates a new user with the provided data after validation.
        Returns the created user with HTTP 201 or an error with HTTP 400/500.
        """
        try:
            user_data = api.payload
    
            # Validation de l'email avec regex pour s'assurer
            # qu'il respecte le format standard
            # et ne contient pas de points consécutifs ou multiples @
            email_regex = re.compile(
                r'^(?!.*\.\.)(?!.*@.*@)[a-zA-Z0-9][a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
            if not email_regex.match(user_data.get('email', '')):
                return {'error': 'Invalid email format'}, 400

            # Vérification que l'email n'est pas déjà utilisé
            existing_user = facade.get_user_by_email(user_data['email'])
            if existing_user:
                return {'error': 'Email already registered'}, 400

            # Validation du prénom
            if not user_data.get('first_name') or len(
                    user_data['first_name']) > 50:
                return {
                    'error': 'First name is required and must not'
                    'exceed 50 characters'}, 400

            # Validation du nom
            if not user_data.get('last_name') or len(
                    user_data['last_name']) > 50:
                return {
                    'error': 'Last name is required and must not'
                    'exceed 50 characters'}, 400
            
            # Validation du mot de passe
            if not user_data.get('password') or len(user_data['password']) < 8:
                return {'error': 'Password is required and must be at least 8 characters long'}, 400

            # Création de l'utilisateur après validation
            new_user = facade.create_user(user_data)
            return {'id': new_user.id, 'message': 'User successfully '
                    'registered'}, 201
        
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return {'error': 'An unexpected error occurred'}, 500

    @api.response(200, 'Users retrieved successfully')
    @api.response(500, 'Internal server error')
    def get(self):
        """Get all users.

        Retrieves a list of all users in the system.
        Returns an array of users with HTTP 200 or an error with HTTP 500.
        """
        try:
            users = facade.get_all_users()
            return [{'id': user.id, 'first_name': user.first_name,
                     'last_name': user.last_name, 'email': user.email} for user in users], 200
        except Exception as e:
            print(f"Error retrieving users: {str(e)}")
            return {'error': 'An unexpected error occurred'}, 500


@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user details by ID.

        Args:
            user_id: The unique identifier of the user to retrieve

        Returns:
            User details with HTTP 200 or an error with HTTP 404/500.
        """
        try:
            user = facade.get_user(user_id)
            if not user:
                return {'error': 'User not found'}, 404
            return {'id': user.id, 'first_name': user.first_name,
                    'last_name': user.last_name, 'email': user.email}, 200
        except Exception as e:
            print(f"Error retrieving user: {str(e)}")
            return {'error': 'An unexpected error occurred'}, 500

    @api.response(200, 'User successfully updated')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'User not found')
    @api.response(500, 'Internal server error')
    # Sans validate=True pour permettre les mises à jour partielles
    @api.expect(user_model)
    def put(self, user_id):
        """Update user details.

        Args:
            user_id: The unique identifier of the user to update

        Returns:
            Updated user details with HTTP 200 or an error with HTTP 400/404/500.
        """
        try:
            # Vérifier que l'utilisateur existe
            user = facade.get_user(user_id)
            if not user:
                return {'error': 'user not found'}, 404

            user_data = api.payload

            # Validation manuelle des champs présents pour permettre les mises
            # à jour partielles
            if 'email' in user_data:
                # Même validation regex que pour la création
                email_regex = re.compile(
                    r'^(?!.*\.\.)(?!.*@.*@)[a-zA-Z0-9][a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
                if not email_regex.match(user_data['email']):
                    return {'error': 'Invalid email format'}, 400

                # Vérifier que l'email n'est pas déjà pris par un autre
                # utilisateur
                if user_data['email'] != user.email:
                    existing_user = facade.get_user_by_email(
                        user_data['email'])
                    if existing_user and existing_user.id != user_id:
                        return {
                            'error': 'Email already registered to another user'}, 400

            # Validation du prénom si présent
            if 'first_name' in user_data and (
                not user_data['first_name'] or len(
                    user_data['first_name']) > 50):
                return {
                    'error': 'First name is required and must not exceed 50 characters'}, 400

            # Validation du nom si présent
            if 'last_name' in user_data and (
                not user_data['last_name'] or len(
                    user_data['last_name']) > 50):
                return {'error': 'Last name must not exceed 50 characters'}, 400

            # Mise à jour de l'utilisateur après validation
            updated_user = facade.update_user(user_id, user_data)
            return {'id': updated_user.id, 'first_name': updated_user.first_name,
                    'last_name': updated_user.last_name, 'email': updated_user.email}, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            print(f"Error updating user: {str(e)}")
            return {'error': 'An unexpected error occurred'}, 500
