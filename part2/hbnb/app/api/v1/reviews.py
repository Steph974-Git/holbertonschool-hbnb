from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade

api = Namespace('reviews', description='Review operations')

# Define the review model for input validation and documentation
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'user_id': fields.String(required=True, description='ID of the user'),
    'place_id': fields.String(required=True, description='ID of the place')
})

@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new review"""
        # Premier bloc try pour la validation des données de base
        try:
            reviews_data = api.payload

            if not reviews_data.get('text'):
                return {'message': 'Reviews text is required'}, 400
            if not reviews_data.get('rating'):
                return {'message': 'Rating is required'}, 400
            if not reviews_data.get('user_id'):
                return {'message': 'User ID is required'}, 400
            if not reviews_data.get('place_id'):
                return {'message': 'Place ID is required'}, 400
            
            # Deuxième bloc try pour la validation du rating
            try:
                rating = int(reviews_data['rating'])
                if rating < 1 or rating > 5:
                    return {'message': 'Rating must be between 1 and 5'}, 400
            except (ValueError, TypeError):
                return {'message': 'Rating must be a number between 1 and 5'}, 400
            
            # S'en suit la création de la review et la récupération de l'utilisateur et du lieu
            hbnb_facade = HBnBFacade()
            user = hbnb_facade.get_user(reviews_data['user_id'])
            place = hbnb_facade.get_place(reviews_data['place_id'])

            if not user:
                return {'message': f'User with ID {reviews_data['user_id']} not found'}, 404
            if not place:
                return {'message': f'Place with ID  {reviews_data['place_id']} not found'}, 404
            
            # Création de la review
            review = hbnb_facade.create_review({
                'text': reviews_data['text'],
                'rating': rating,
                'user': user,
                'place': place
            })

            # On retourne les détails de la review créée
            return {'id': review.id, 'text': review.text, 'rating': review.rating, 'user_id': user.id,
                    'place_id': review.place.id, 'created_at': review.created_at.isoformat()}, 201
        
        except Exception as e:
            # Gestion des erreurs générales pour tout le bloc
            return {'message': f'An error occurred: {str(e)}'}, 500

            

    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """Retrieve a list of all reviews"""
        try:
            # Récupérer les reviews via la façade
            hbnb_facade = HBnBFacade()
            reviews = hbnb_facade.get_all_reviews()
            # Vérifier si des reviews existent
            if not reviews:
                return [], 200
            # Formater les données pour la réponse
            result = []
            for review in reviews:
            # Créer un dictionnaire pour chaques review
                review_data = {'id': review.id, 'text': review.text, 'rating': review.rating,
                            'user_id': review.user.id, 'place_id': review.place.id,
                            'created_at': review.created_at.isoformat(),
                            'updated_at': review.updated_at.isoformat()}
                result.append(review_data)
            # Ensuite on return la liste des reviews
            return result, 200
        except Exception as e:
            return {'message': f"An error occurred: {str(e)}"}, 500

@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Get review details by ID"""
        try:
            hbnb_facade = HBnBFacade()
            review = hbnb_facade.get_review(review_id)

            if not review:
                return {'message': f"Review with ID {review_id} not found"}, 404
            
            review_data = {'id': review.id, 'text': review.text, 'rating': review.rating,
                        'user_id': review.user.id, 'place_id': review.place.id,
                        'created_at': review.created_at.isoformat(),
                        'updated_at': review.updated_at.isoformat()}
            return review_data
        except Exception as e:
            return {'message': f'An error occurred: {str(e)}'}, 500
            

    @api.expect(review_model)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    def put(self, review_id):
        """Update a review's information"""
        try:
            # Récupérer les données de la requete
            review_data = api.payload
            # Valider les données d'entrée
            if not review_data:
                return {'message': 'No data provided'}, 400
            # Vérification spécifiques pour chaque champ
            if 'rating' in review_data:
                try:
                    rating = int(review_data['rating'])
                    if rating < 1 or rating > 5:
                        return {'message': 'Rating must be between 1 and 5'}, 400  # Ajout du code HTTP 400
                except (ValueError, TypeError):
                    return {'message': 'Rating must be a number between 1 and 5'}, 400

            if 'text' in review_data and not review_data['text']:
                return {'message': 'Review text cannot be empty'}, 400
            # Verifier si la review existe
            hbnb_facade = HBnBFacade()
            existing_review = hbnb_facade.get_review(review_id)

            if not existing_review:
                return {'message': f'Review with ID {review_id} not found'}, 404
            # Préparer les données pour la mise a jour
            updated_data = {}
            if 'text' in review_data:
                updated_data['text'] = review_data['text']
            if 'rating' in review_data:
                updated_data['rating'] = rating
            # Mettre a jour la review
            update_review = hbnb_facade.updated_review(review_id, updated_data)
            # Retourner la réponse
            return {
                'id': update_review.id, 
                'text': update_review.text, 
                'rating': update_review.rating,
                'user_id': update_review.user.id,  # Assurez-vous que c'est bien user.id
                'place_id': update_review.place.id,  # Assurez-vous que c'est bien place.id
                'created_at': update_review.created_at.isoformat(),
                'updated_at': update_review.updated_at.isoformat()
            }, 200
        except Exception as e:
            # Gerer les erreurs potentielles
            import traceback
            print(f"Error updating review: {str(e)}")
            print(traceback.format_exc())
            return {'message': f'An error occurred: {str(e)}'}, 500

    @api.response(200, 'Review deleted successfully')
    @api.response(404, 'Review not found')
    def delete(self, review_id):
        """Delete a review"""
        try:
            hbnb_facade = HBnBFacade()
            existing_review = hbnb_facade.get_review(review_id)

            if not existing_review:
                return {'message': f'Review with ID {review_id} not found'}, 404
            success = hbnb_facade.delete_review(review_id)

            if success:
                return {'message': f'Review with ID { review_id} deleted successfully'}, 200
            else:
                return {'message': f'Failed to delete review with ID {review_id}'}, 500
        except Exception as e:
            return {'message': f'An errir occurred: {str(e)}'}, 500


@api.route('/places/<place_id>/reviews')
class PlaceReviewList(Resource):
    @api.response(200, 'List of reviews for the place retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get all reviews for a specific place"""
        try:
            hbnb_facade = HBnBFacade()
            place = hbnb_facade.get_place(place_id)

            if not place:
                return {'message': f'Place with ID {place_id} not found'}, 404
            reviews = hbnb_facade.get_reviews_by_place(place_id)

            if not reviews:
                return [], 200
            
            result = []
            for review in reviews:
                review_data = {
                    'id': review.id, 'text': review.text, 'rating': review.rating,
                    'user_id': review.user.id, 'place_id': review.place.id,
                    'created_at': review.created_at.isoformat(),
                    'updated_at': review.updated_at.isoformat()
                }
                result.append(review_data)
            return result, 200
        except Exception as e:
            return {'message':f'An error occurred: {str(e)}'}, 500