#!/usr/bin/python3
"""Module d'API pour les opérations liées aux amenities (équipements)

Ce module fournit les endpoints REST pour la création, la récupération et
la mise à jour des amenities dans l'application HBnB.
"""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.services import facade  # Import unifié comme dans users.py

# Création du namespace pour les opérations sur les amenities
api = Namespace('amenities', description='Amenity operations')

# Définition du modèle amenity pour la validation des entrées et documentation
amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})


@api.route('/')
class AmenityList(Resource):
    @api.expect(amenity_model)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')  # Ajout
    @api.response(500, 'Server error')
    @jwt_required()  # Ajout - ADMIN UNIQUEMENT
    def post(self):
        """Create new amenity (ADMIN ONLY)"""
        current_user = get_jwt_identity()

        # Vérification des privilèges admin
        if not current_user.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403
        
        try:
            # Récupération et validation des données
            amenity_data = api.payload

            # Vérifier que le nom est présent
            if not amenity_data.get('name'):
                return {"error": "Name is required"}, 400

            # Vérifier que le nom ne dépasse pas 50 caractères
            if len(amenity_data['name']) > 50:
                return {"error": "Name must be less than 50 characters"}, 400

            # Création de l'amenity après validation
            new_amenity = facade.create_amenity(amenity_data['name'])

            # Vérification que l'objet a bien été créé
            if not new_amenity:
                return {"error": "Failed to create amenity"}, 500

            # Construction de la réponse avec les attributs nécessaires
            response = {
                'id': new_amenity.id,
                'name': new_amenity.name
            }
            return response, 201

        except ValueError as e:
            # Gestion des erreurs de validation
            return {"error": str(e)}, 400
        except Exception as e:
            # Gestion des erreurs inattendues avec trace pour débogage
            print(f"Error creating amenity: {str(e)}")
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    @api.response(200, 'List of amenities retrieved successfully')
    @api.response(500, 'Server error')
    def get(self):
        """Get all amenities (PUBLIC)"""
        try:
            # Récupère toutes les amenities via la façade
            amenities = facade.get_all_amenities()

            # Si aucune amenity n'existe, retourne une liste vide
            if not amenities:
                return [], 200

            # Formate la réponse pour inclure uniquement les champs nécessaires
            result = []
            for amenity in amenities:
                result.append({'id': amenity.id, 'name': amenity.name})
            return result, 200
        except Exception as e:
            print(f"Error retrieving amenities: {str(e)}")
            return {"error": "Failed to retrieve amenities"}, 500


@api.route('/<amenity_id>')
class AmenityResource(Resource):
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(404, 'Amenity not found')
    @api.response(500, 'Server error')
    def get(self, amenity_id):
        """Get amenity by ID (PUBLIC)"""
        try:
            # Récupération de l'amenity par son ID
            amenity = facade.get_amenity_by_id(amenity_id)

            # Vérifie si l'amenity existe
            if not amenity:
                return {
                    "error": f"Amenity with ID {amenity_id} not found"}, 404

            # Retourne les détails de l'amenity
            return {'id': amenity.id, 'name': amenity.name}, 200
        except Exception as e:
            print(f"Error retrieving amenity: {str(e)}")
            return {"error": "Failed to retrieve amenity"}, 500

    @api.expect(amenity_model)
    @api.response(200, 'Amenity updated successfully')
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')  # Ajout
    @api.response(500, 'Server error')
    @jwt_required()  # Ajout - ADMIN UNIQUEMENT
    def put(self, amenity_id):
        """Update amenity (ADMIN ONLY)"""
        current_user = get_jwt_identity()

        # Vérification des privilèges admin
        if not current_user.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403
        
        try:
            # Récupère les données de la requête
            amenity_data = api.payload

            # Validation des données d'entrée
            if not amenity_data.get('name'):
                return {"error": "Name is required"}, 400

            if len(amenity_data['name']) > 50:
                return {"error": "Name must be less than 50 characters"}, 400

            # Vérifie d'abord si l'amenity existe
            existing_amenity = facade.get_amenity_by_id(amenity_id)

            if not existing_amenity:
                return {
                    "error": f"Amenity with ID {amenity_id} not found"}, 404

            # Met à jour l'amenity avec le nouveau nom
            updated_amenity = facade.update_amenity(
                amenity_id, amenity_data['name'])

            # Retourne l'amenity mise à jour
            return {'id': updated_amenity.id,
                    'name': updated_amenity.name}, 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            print(f"Error updating amenity: {str(e)}")
            return {"error": "Failed to update amenity"}, 500
