from flask_restx import Namespace, Resource, fields
from app.services import facade

# Création du namespace pour les opérations sur les places
api = Namespace('places', description='Place operations')

# Définition des modèles pour les entités liées aux places
amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})

user_model = api.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name': fields.String(description='Last name of the owner'),
    'email': fields.String(description='Email of the owner')
})

review_model = api.model('PlaceReview', {
    'id': fields.String(description='Review ID'),
    'text': fields.String(description='Text of the review'),
    'rating': fields.Integer(description='Rating of the place (1-5)'),
    'user_id': fields.String(description='ID of the user')
})

# Définition du modèle place pour la validation des entrées et la documentation
place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'owner_id': fields.String(required=True, description='ID of the owner'),
    'owner': fields.Nested(user_model, description='Owner of the place'),
    'amenities': fields.List(fields.String, required=True, description="List of amenities ID's"),
})


@api.route('/')
class PlaceList(Resource):
    @api.expect(place_model)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'Owner not found')
    @api.response(500, 'Internal server error')
    def post(self):
        """Enregistre un nouvel hébergement.

        Crée un nouvel hébergement avec les données fournies après validation.

        Returns:
            dict: Les détails de l'hébergement
            créé et code HTTP 201 en cas de succès
            dict: Message d'erreur et code HTTP approprié
            (400, 404, 500) en cas d'échec
        """
        try:
            place_data = api.payload

            # Validation du titre: ne doit pas être vide
            if not place_data.get('title'):
                return {'error': 'Title is required'}, 400

            # Validation du prix: doit être un nombre positif
            if not place_data.get('price') or place_data['price'] <= 0:
                return {'error': 'Price must be a positive number'}, 400

            latitude = place_data.get('latitude')
            longitude = place_data.get('longitude')

            # Validation des coordonnées géographiques
            if latitude is None or longitude is None:
                return {'error': 'Latitude and longitude are required'}, 400
            if not -90 <= latitude <= 90:
                return {
                    'error': 'Latitude must be between '
                    '-90 and 90 degrees'}, 400
            if not -180 <= longitude <= 180:
                return {
                    'error': 'Longitude must be between '
                    '-180 and 180 degrees'}, 400

            # Vérification que le propriétaire existe
            owner = facade.get_user(place_data['owner_id'])
            if not owner:
                return {'error': 'User does not exist'}, 404

            # Création de l'hébergement après validation
            new_place = facade.create_place(place_data)

            # Préparation de la réponse avec ou sans aménités
            if new_place.amenities:
                amenities_list = [{"id": amenity.id, "name": amenity.name}
                                  for amenity in new_place.amenities]
                return {"id": new_place.id, "title": new_place.title,
                        "description": new_place.description,
                        "price": new_place.price,
                        "latitude": new_place.latitude,
                        "longitude": new_place.longitude,
                        "owner_id": new_place.owner.id,
                        "amenities": amenities_list}, 201

            return {"id": new_place.id, "title": new_place.title,
                    "description": new_place.description,
                    "price": new_place.price,
                    "latitude": new_place.latitude,
                    "longitude": new_place.longitude,
                    "owner_id": new_place.owner.id}, 201

        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            print(f"Error creating place: {str(e)}")
            return {'error': 'An unexpected error occurred'}, 500

    @api.response(200, 'List of places retrieved successfully')
    @api.response(500, 'Internal server error')
    def get(self):
        """Récupère la liste de tous les hébergements.

        Returns:
            list: Liste des hébergements disponibles et
            code HTTP 200 en cas de succès
            dict: Message d'erreur et code HTTP 500 en cas d'échec
        """
        try:
            places = facade.get_all_places()
            result = []

            # Formatage de chaque hébergement pour la réponse
            for place in places:
                if place.amenities:
                    amenities_list = [{"id": amenity.id, "name": amenity.name}
                                      for amenity in place.amenities]
                    result.append({"id": place.id,
                                   "title": place.title,
                                   "description": place.description,
                                   "price": place.price,
                                   "latitude": place.latitude,
                                   "longitude": place.longitude,
                                   "owner_id": place.owner.id,
                                   "amenities": amenities_list})
                else:
                    result.append({"id": place.id,
                                   "title": place.title,
                                   "description": place.description,
                                   "price": place.price,
                                   "latitude": place.latitude,
                                   "longitude": place.longitude,
                                   "owner_id": place.owner.id})
            return result, 200
        except Exception as e:
            print(f"Error retrieving places: {str(e)}")
            return {'error': 'An unexpected error occurred'}, 500


@api.route('/<place_id>')
class PlaceResource(Resource):
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    @api.response(500, 'Internal server error')
    def get(self, place_id):
        """Récupère les détails d'un hébergement spécifique.

        Args:
            place_id (str): L'identifiant unique de l'hébergement à récupérer

        Returns:
            dict: Les détails de l'hébergement et
            code HTTP 200 en cas de succès
            dict: Message d'erreur et code HTTP
            approprié (404, 500) en cas d'échec
        """
        try:
            place = facade.get_place(place_id)
            if not place:
                return {"error": "Place not found"}, 404

            # Préparation des informations du propriétaire
            owner_details = {
                "id": place.owner.id,
                "first_name": place.owner.first_name,
                "last_name": place.owner.last_name,
                "email": place.owner.email
            }

            # Préparation de la réponse avec ou sans aménités
            if place.amenities:
                amenities_list = [{"id": amenity.id, "name": amenity.name}
                                  for amenity in place.amenities]
                return {"id": place.id, "title": place.title,
                        "description": place.description,
                        "price": place.price,
                        "latitude": place.latitude,
                        "longitude": place.longitude,
                        "owner": owner_details,
                        "amenities": amenities_list}, 200

            return {"id": place.id, "title": place.title,
                    "description": place.description, "price": place.price,
                    "latitude": place.latitude, "longitude": place.longitude,
                    "owner": owner_details}, 200
        except Exception as e:
            print(f"Error retrieving place: {str(e)}")
            return {'error': 'An unexpected error occurred'}, 500

    @api.expect(place_model)
    @api.response(200, 'Place updated successfully')
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    def put(self, place_id):
        """Met à jour les informations d'un hébergement.

        Args:
            place_id (str): L'identifiant unique
            de l'hébergement à mettre à jour

        Returns:
            dict: Message de succès et code HTTP 200 en cas de succès
            dict: Message d'erreur et code HTTP approprié
            (400, 404, 500) en cas d'échec
        """
        try:
            # Vérification que l'hébergement existe
            place = facade.get_place(place_id)
            if not place:
                return {'error': 'Place not found'}, 404

            place_data = api.payload
            latitude = place_data.get('latitude')
            longitude = place_data.get('longitude')

            # Validation des coordonnées géographiques si présentes
            if 'latitude' in place_data:
                if not -90 <= latitude <= 90:
                    return {
                        'error': 'Latitude must be between'
                        '-90 and 90 degrees'}, 400

            if 'longitude' in place_data:
                if not -180 <= longitude <= 180:
                    return {
                        'error': 'Longitude must be between'
                        '-180 and 180 degrees'}, 400

            # Validation du prix si présent
            if 'price' in place_data and place_data['price'] <= 0:
                return {'error': 'Price must be a positive number'}, 400

            # Vérification du nouveau propriétaire s'il est modifié
            new_owner = None
            if 'owner_id' in place_data and place_data['owner_id'] != place.owner.id:
                new_owner = facade.get_user(place_data['owner_id'])
                if not new_owner:
                    return {'error': 'New owner does not exist'}, 404

            # Mise à jour de l'hébergement après validation
            update_place = facade.update_place(place_id, api.payload)
            return {"message": "Place updated successfully"}, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            print(f"Error updating place: {str(e)}")
            return {'error': 'An unexpected error occurred'}, 500
