from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('amenities', description='Amenity operations')

# Define the amenity model for input validation and documentation
amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})

@api.route('/')
class AmenityList(Resource):
    @api.expect(amenity_model)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new amenity"""
        # Placeholder for the logic to register a new amenity
        data = api.payload

        if not data.get('name'):
            return {"message": "Name is required"}, 400
        if len(data['name']) > 50:
            return {"message": "Name must be less than 50 characters"}, 400
        
        # Création de l'amenity après validation
        hbnb_facade = facade.HBnBFacade()
        new_amenity = hbnb_facade.create_amenity(data['name'])
        return {'id': new_amenity.id, 'name': new_amenity.name}, 201
        



    @api.response(200, 'List of amenities retrieved successfully')
    def get(self):
        """Retrieve a list of all amenities"""
        # Récupère toutes les amenities
        hbnb_facade = facade.HBnBFacade()
        amenities = hbnb_facade.get_all_amenities()

        #Si aucune amenity n'existe, retourne une liste vide
        if not amenities:
            return [], 200
        
        # Formate la réponse
        result = []
        for amenity in amenities:
            result.append({'id': amenity.id, 'name': amenity.name})
        return result, 200
    

@api.route('/<amenity_id>')
class AmenityResource(Resource):
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """Get amenity details by ID"""
        hbnb_facade = facade.HBnBFacade()
        amenity = hbnb_facade.get_amenity_by_id(amenity_id)

        # Vérifie si l'amenity existe
        if not amenity:
            return {"message": f"Amenity with ID {amenity_id} not found"}, 404
        
        # Retourne les details de l'amenity
        return {'id': amenity.id, 'name': amenity.name}, 200


    @api.expect(amenity_model)
    @api.response(200, 'Amenity updated successfully')
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
    def put(self, amenity_id):
        """Update an amenity's information"""
        # Récupère les données de la requête
        data = api.payload

        # Validation données
        if not data.get('name'):
            return {"message": f"Amenity with ID {amenity_id} not found"}, 404
        if len(data['name']) > 50:
            return {"message": "Name must be less than 50 characters"}, 400
        
        # Vérifie d'abord si l'amenity existe
        hbnb_facade = facade.HBnBFacade()
        existing_amenity = hbnb_facade.get_amenity_by_is(amenity_id)

        if not existing_amenity:
            return {"message": f"Amenity with ID {amenity_id} not found"}, 404
        
        # Met a jour l'amenity
        updated_amenity = hbnb_facade.update_amenity(amenity_id, data['name'])

        # Retourne l'amenity mise à jour
        return {'id': updated_amenity.id, 'name': updated_amenity.name}, 200