from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('places', description='Place operations')

# Define the models for related entities
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

# Define the place model for input validation and documentation
place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'owner_id': fields.String(required=True, description='ID of the owner'),
    'amenities': fields.List(fields.String, required=True, description="List of amenities ID's")
})

@api.route('/')
class PlaceList(Resource):
    @api.expect(place_model)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new place"""
        place_data = api.payload
        latitude = place_data.get('latitude')
        longitude = place_data.get('longitude')

        # Validate latitude and longitude values
        if latitude is None or longitude is None:
            return {'error': 'Latitude and longitude are required'}, 400
        if not -90 <= latitude <= 90:
            return {'error': 'Latitude must be between -90 and 90 degrees'}, 400
        if not -180 <= longitude <= 180:
            return {'error': 'Longitude must be between -180 and 180 degrees'}, 400
        owner = facade.get_user(place_data['owner_id'])
        if not owner:
            return {'error': 'User does not exist'}, 404
        
        new_place = facade.create_place(place_data)
        return {"title": new_place.title, "description": new_place.description, "price": new_place.price,
                "latitude": new_place.latitude, "longitude": new_place.longitude, "owner_id": new_place.owner_id}, 201

    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """Retrieve a list of all places"""
        places = facade.get_all_places()
        return [{"title": place.title, "description": place.description, "price": place.price,
                "latitude": place.latitude, "longitude": place.longitude, "owner_id": place.owner_id} for place in places], 200

@api.route('/<place_id>')
class PlaceResource(Resource):
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        place_owner_id = facade.get_user(place.owner_id)
        return {"title": place.title, "description": place.description, "price": place.price, 
                "latitude": place.latitude, "longitude": place.longitude, "owner_id": place.owner_id}, 200
        

    @api.expect(place_model)
    @api.response(200, 'Place updated successfully')
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    def put(self, place_id):
        """Update a place's information"""
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        place_data = api.payload
        latitude = place_data.get('latitude')
        longitude = place_data.get('longitude')
        if latitude is None or longitude is None:
            return {'error': 'Latitude and longitude are required'}, 400
        if not -90 <= latitude <= 90:
            return {'error': 'Latitude must be between -90 and 90 degrees'}, 400
        if not -180 <= longitude <= 180:
            return {'error': 'Longitude must be between -180 and 180 degrees'}, 400
        if not place_data.get('owner_id'):
            return {'error': 'Owner ID is required'}, 400
        update_place = facade.update_place(place_id, api.payload)
        return {"title": update_place.title, "description": update_place.description, "price": update_place.price, 
                "latitude": update_place.latitude, "longitude": update_place.longitude, "owner_id": update_place.owner_id}, 200
