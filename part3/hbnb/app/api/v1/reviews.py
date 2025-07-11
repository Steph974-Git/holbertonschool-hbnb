#!/usr/bin/python3
"""Module d'API pour les opérations liées aux reviews (avis)

Ce module fournit les endpoints REST pour la création, la consultation,
la mise à jour et la suppression des avis dans l'application HBnB.
Il permet également de récupérer les avis associés à un hébergement spécifique.
"""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.services import facade

# Création du namespace pour regrouper les routes liées aux reviews
api = Namespace('reviews', description='Review operations')

# Définition du modèle review pour la validation des entrées et documentation
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'place_id': fields.String(required=True, description='ID of the place')  # <-- toujours demandé
})


@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(401, 'Authentication required')
    @api.response(404, 'Place not found')
    @api.response(500, 'Server error')
    @jwt_required()
    def post(self):
        """Create new review (Authenticated users only)"""
        try:
            current_user = get_jwt_identity()
            reviews_data = api.payload

            # Forcer l'utilisateur connecté comme auteur de la review
            reviews_data['user_id'] = current_user['id']

            # Validation des champs obligatoires
            if not reviews_data.get('text'):
                return {'error': 'Review text is required'}, 400
            if not reviews_data.get('rating'):
                return {'error': 'Rating is required'}, 400
            if not reviews_data.get('place_id'):
                return {'error': 'Place ID is required'}, 400

            # Validation du format et de la plage de la note
            try:
                rating = int(reviews_data['rating'])
                if rating < 1 or rating > 5:
                    return {'error': 'Rating must be between 1 and 5'}, 400
            except (ValueError, TypeError):
                return {'error': 'Rating must be a number between 1 and 5'}, 400

            # Récupération des entités associées (utilisateur et lieu)
            user = facade.get_user(reviews_data['user_id'])
            place = facade.get_place(reviews_data['place_id'])

            # Vérification de l'existence des entités associées
            if not user:
                return {'error': f'User with ID {reviews_data["user_id"]} not found'}, 404
            if not place:
                return {'error': f'Place with ID {reviews_data["place_id"]} not found'}, 404

            # VALIDATION: Empêcher l'auto-review
            if place.owner.id == current_user['id']:
                return {'error': 'You cannot review your own place'}, 400

            # VALIDATION: Empêcher les reviews dupliquées
            existing_reviews = facade.get_reviews_by_place(reviews_data['place_id'])
            for review in existing_reviews:
                if review.user.id == current_user['id']:
                    return {'error': 'You have already reviewed this place'}, 400

            # Création de l'avis une fois toutes les validations passées
            review = facade.create_review({
                'text': reviews_data['text'],
                'rating': rating,
                'user_id': reviews_data['user_id'],
                'place_id': reviews_data['place_id']
            })

            # Construction de la réponse avec les données de l'avis créé
            return {
                'id': review.id,
                'text': review.text,
                'rating': review.rating,
                'user_id': user.id,
                'place_id': reviews_data['place_id'],
                'created_at': review.created_at.isoformat()
            }, 201

        except Exception as e:
            print(f"Error creating review: {str(e)}")
            return {'error': 'An unexpected error occurred'}, 500

    @api.response(200, 'List of reviews retrieved successfully')
    @api.response(500, 'Server error')
    def get(self):
        """Get all reviews (PUBLIC)"""
        try:
            reviews = facade.get_all_reviews()

            if not reviews:
                return [], 200

            result = []
            for review in reviews:
                review_data = {
                    'id': review.id,
                    'text': review.text,
                    'rating': review.rating,
                    'user_id': review.user.id,
                    'place_id': review.place.id,
                    'created_at': review.created_at.isoformat(),
                    'updated_at': review.updated_at.isoformat()
                }
                result.append(review_data)

            return result, 200

        except Exception as e:
            print(f"Error retrieving reviews: {str(e)}")
            return {'error': 'Failed to retrieve reviews'}, 500


@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    @api.response(500, 'Server error')
    def get(self, review_id):
        """Get review details by ID (PUBLIC)"""
        try:
            review = facade.get_review(review_id)

            if not review:
                return {'error': f'Review with ID {review_id} not found'}, 404

            review_data = {
                'id': review.id,
                'text': review.text,
                'rating': review.rating,
                'user_id': review.user.id,
                'place_id': review.place.id,
                'created_at': review.created_at.isoformat(),
                'updated_at': review.updated_at.isoformat()
            }
            return review_data, 200

        except Exception as e:
            print(f"Error retrieving review: {str(e)}")
            return {'error': 'Failed to retrieve review'}, 500

    @api.expect(review_model)
    @api.response(200, 'Review updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(401, 'Authentication required')
    @api.response(403, 'Access forbidden')
    @api.response(404, 'Review not found')
    @api.response(500, 'Server error')
    @jwt_required()
    def put(self, review_id):
        """Update review (Owner or Admin only)"""
        try:
            current_user = get_jwt_identity()
            review_data = api.payload

            # Vérification que l'avis existe
            existing_review = facade.get_review(review_id)
            if not existing_review:
                return {'error': f'Review with ID {review_id} not found'}, 404

            is_admin = current_user.get('is_admin', False)
            user_id = current_user.get('id')

            if not is_admin and existing_review.user.id != user_id:
                return {'error': 'Unauthorized action'}, 403

            # Vérifier que le place_id fourni correspond à la review (sécurité)
            if 'place_id' in review_data and review_data['place_id'] != existing_review.place.id:
                return {'error': 'Cannot change place_id of a review'}, 400

            # Traiter les champs modifiables
            updated_data = {}
            if 'text' in review_data:
                updated_data['text'] = review_data['text']
            if 'rating' in review_data:
                try:
                    rating = int(review_data['rating'])
                    if rating < 1 or rating > 5:
                        return {'error': 'Rating must be between 1 and 5'}, 400
                    updated_data['rating'] = rating
                except (ValueError, TypeError):
                    return {'error': 'Rating must be a number between 1 and 5'}, 400

            # Mise à jour de l'avis via la façade
            updated_review = facade.update_review(review_id, updated_data)

            return {
                'id': updated_review.id,
                'text': updated_review.text,
                'rating': updated_review.rating,
                'user_id': updated_review.user.id,
                'place_id': updated_review.place.id,
                'created_at': updated_review.created_at.isoformat(),
                'updated_at': updated_review.updated_at.isoformat()
            }, 200

        except Exception as e:
            print(f"Error updating review: {str(e)}")
            return {'error': 'An unexpected error occurred'}, 500

    @api.response(200, 'Review deleted successfully')
    @api.response(401, 'Authentication required')
    @api.response(403, 'Access forbidden')
    @api.response(404, 'Review not found')
    @api.response(500, 'Server error')
    @jwt_required()
    def delete(self, review_id):
        """Delete review (Owner or Admin only)"""
        try:
            current_user = get_jwt_identity()
            
            # Vérification que l'avis existe
            existing_review = facade.get_review(review_id)
            if not existing_review:
                return {'error': f'Review with ID {review_id} not found'}, 404

            # TASK 5: Admin bypass OU propriétaire uniquement
            is_admin = current_user.get('is_admin', False)
            user_id = current_user.get('id')
            
            if not is_admin and existing_review.user.id != user_id:
                return {'error': 'Unauthorized action'}, 403

            # Suppression de l'avis via la façade
            success = facade.delete_review(review_id)

            if success:
                return {'message': f'Review with ID {review_id} deleted successfully'}, 200
            else:
                return {'error': f'Failed to delete review with ID {review_id}'}, 500

        except Exception as e:
            print(f"Error deleting review: {str(e)}")
            return {'error': 'An unexpected error occurred'}, 500


@api.route('/places/<place_id>/reviews')
class PlaceReviewList(Resource):
    @api.response(200, 'List of reviews for the place retrieved successfully')
    @api.response(404, 'Place not found')
    @api.response(500, 'Server error')
    def get(self, place_id):
        """Get all reviews for a specific place (PUBLIC)"""
        try:
            # Vérification que l'hébergement existe
            place = facade.get_place(place_id)
            if not place:
                return {'error': f'Place with ID {place_id} not found'}, 404

            # Récupération des avis pour cet hébergement
            reviews = facade.get_reviews_by_place(place_id)

            if not reviews:
                return [], 200

            result = []
            for review in reviews:
                review_data = {
                    'id': review.id,
                    'text': review.text,
                    'rating': review.rating,
                    'user_id': review.user.id,
                    'place_id': review.place.id,
                    'created_at': review.created_at.isoformat(),
                    'updated_at': review.updated_at.isoformat()
                }
                result.append(review_data)

            return result, 200

        except Exception as e:
            print(f"Error retrieving reviews for place: {str(e)}")
            return {'error': 'Failed to retrieve reviews for place'}, 500
