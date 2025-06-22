#!/usr/bin/python3
"""Module d'API pour les opérations liées aux reviews (avis)

Ce module fournit les endpoints REST pour la création, la consultation,
la mise à jour et la suppression des avis dans l'application HBnB.
Il permet également de récupérer les avis associés à un hébergement spécifique.
"""
from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade

# Création du namespace pour regrouper les routes liées aux reviews
api = Namespace('reviews', description='Review operations')

# Définition du modèle review pour la validation des entrées et documentation
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True,
                             description='Rating of the place (1-5)'),
    'user_id': fields.String(required=True, description='ID of the user'),
    'place_id': fields.String(required=True, description='ID of the place')
})

# Modèle pour la mise à jour d'un avis
review_update_model = api.model('ReviewUpdate', {
    'text': fields.String(required=False, description='Text of the review'),
    'rating': fields.String(required=False, description='Rating of the place (1-5), must be an integer')
})


@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'User or place not found')
    @api.response(500, 'Server error')
    def post(self):
        """Enregistre un nouvel avis.

        Crée un nouvel avis avec les données fournies après validation.
        Vérifie que l'utilisateur et le lieu existent avant la création.

        Returns:
            dict: Les détails de l'avis créé et code HTTP 201 en cas de succès
            dict: Message d'erreur et code HTTP approprié en cas d'échec
        """
        try:
            # Récupération des données de la requête
            reviews_data = api.payload

            # Validation des champs obligatoires
            if not reviews_data.get('text'):
                return {'message': 'Reviews text is required'}, 400
            if not reviews_data.get('rating'):
                return {'message': 'Rating is required'}, 400
            if not reviews_data.get('user_id'):
                return {'message': 'User ID is required'}, 400
            if not reviews_data.get('place_id'):
                return {'message': 'Place ID is required'}, 400

            # Validation du format et de la plage de la note
            try:
                rating = int(reviews_data['rating'])
                if rating < 1 or rating > 5:
                    return {'message': 'Rating must be between 1 and 5'}, 400
            except (ValueError, TypeError):
                return {
                    'message': 'Rating must be a number between 1 and 5'}, 400

            # Récupération des entités associées (utilisateur et lieu)
            hbnb_facade = HBnBFacade()
            user = hbnb_facade.get_user(reviews_data['user_id'])
            place = hbnb_facade.get_place(reviews_data['place_id'])

            # Vérification de l'existence des entités associées
            if not user:
                return {
                    'message': f'User with ID {
                        reviews_data["user_id"]} not found'}, 404
            if not place:
                return {
                    'message': f'Place with ID {
                        reviews_data["place_id"]} not found'}, 404

            # Création de l'avis une fois toutes les validations passées
            review = hbnb_facade.create_review({
                'text': reviews_data['text'],
                'rating': rating,
                'user': user,
                'place': place
            })

            # Construction de la réponse avec les données de l'avis créé
            return {
                'id': review.id,
                'text': review.text,
                'rating': review.rating,
                'user_id': user.id,
                'place_id': review.place.id,
                'created_at': review.created_at.isoformat()
            }, 201

        except Exception as e:
            # Journalisation et gestion des erreurs imprévues
            print(f"Error creating review: {str(e)}")
            return {'message': f'An error occurred: {str(e)}'}, 500

    @api.response(200, 'List of reviews retrieved successfully')
    @api.response(500, 'Server error')
    def get(self):
        """Récupère la liste de tous les avis.

        Returns:
            list: Liste des avis disponibles et code HTTP 200
            list: Liste vide si aucun avis n'existe
            dict: Message d'erreur et code HTTP 500 en cas d'échec
        """
        try:
            # Récupération de tous les avis via la façade
            hbnb_facade = HBnBFacade()
            reviews = hbnb_facade.get_all_reviews()

            # Si aucun avis n'existe, retourner une liste vide
            if not reviews:
                return [], 200

            # Formatage des données pour la réponse
            result = []
            for review in reviews:
                # Création d'un dictionnaire pour chaque avis avec tous les
                # attributs nécessaires
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

            # Retour de la liste complète des avis
            return result, 200

        except Exception as e:
            # Journalisation et gestion des erreurs imprévues
            print(f"Error retrieving reviews: {str(e)}")
            return {'message': f'An error occurred: {str(e)}'}, 500


@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    @api.response(500, 'Server error')
    def get(self, review_id):
        """Récupère les détails d'un avis spécifique.

        Args:
            review_id (str): L'identifiant unique de l'avis à récupérer

        Returns:
            dict: Les détails de l'avis et code HTTP 200 en cas de succès
            dict: Message d'erreur et code HTTP approprié en cas d'échec
        """
        try:
            # Récupération de l'avis par son ID
            hbnb_facade = HBnBFacade()
            review = hbnb_facade.get_review(review_id)

            # Vérification que l'avis existe
            if not review:
                return {'message': f'Review with ID {review_id} not found'}, 404

            # Construction de la réponse avec toutes les données de l'avis
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
            # Journalisation et gestion des erreurs imprévues
            print(f"Error retrieving review: {str(e)}")
            return {'message': f'An error occurred: {str(e)}'}, 500

    @api.expect(review_update_model)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    @api.response(500, 'Server error')
    def put(self, review_id):
        """Met à jour les informations d'un avis existant.

        Seuls le texte et la note peuvent être modifiés.
        Les relations avec l'utilisateur
        et le lieu ne peuvent pas être changées.

        Args:
            review_id (str): L'identifiant unique de l'avis à mettre à jour

        Returns:
            dict: Les détails de l'avis mis à
            jour et code HTTP 200 en cas de succès
            dict: Message d'erreur et code HTTP approprié en cas d'échec
        """
        try:
            # Récupération des données de la requête
            review_data = api.payload

            # Validation de base des données
            if not review_data:
                return {'message': 'No data provided'}, 400

            # Validation spécifique pour chaque champ modifiable
            if 'rating' in review_data:
                try:
                    rating = int(review_data['rating'])
                    if rating < 1 or rating > 5:
                        return {
                            'message': 'Rating must be between 1 and 5'}, 400
                except (ValueError, TypeError):
                    return {
                        'message': 'Rating must be a '
                        'number between 1 and 5'}, 400

            if 'text' in review_data and not review_data['text']:
                return {'message': 'Review text cannot be empty'}, 400

            # Interdiction de modifier les relations
            if 'user_id' in review_data or 'place_id' in review_data:
                return {
                    'message': 'Cannot change '
                    'user_id or place_id of a review'}, 400

            # Vérification que l'avis existe
            hbnb_facade = HBnBFacade()
            existing_review = hbnb_facade.get_review(review_id)

            if not existing_review:
                return {'message': f'Review with ID {review_id} not found'}, 404

            # Préparation des données à mettre à jour
            updated_data = {}
            if 'text' in review_data:
                updated_data['text'] = review_data['text']
            if 'rating' in review_data:
                try:
                    rating_value = int(review_data['rating'])
                    if rating_value < 1 or rating_value > 5:
                        return {'message': 'Rating must be between 1 and 5'}, 400
                    updated_data['rating'] = rating_value
                except (ValueError, TypeError):
                    return {'message': 'Rating must be a number between 1 and 5'}, 400

            # Mise à jour de l'avis via la façade
            update_review = hbnb_facade.updated_review(review_id, updated_data)

            # Construction de la réponse avec les données mises à jour
            return {
                'id': update_review.id,
                'text': update_review.text,
                'rating': update_review.rating,
                'user_id': update_review.user.id,
                'place_id': update_review.place.id,
                'created_at': update_review.created_at.isoformat(),
                'updated_at': update_review.updated_at.isoformat()
            }, 200

        except Exception as e:
            # Journalisation détaillée des erreurs pour le débogage
            import traceback
            print(f"Error updating review: {str(e)}")
            print(traceback.format_exc())
            return {'message': f'An error occurred: {str(e)}'}, 500

    @api.response(200, 'Review deleted successfully')
    @api.response(404, 'Review not found')
    @api.response(500, 'Server error')
    def delete(self, review_id):
        """Supprime un avis existant.

        Args:
            review_id (str): L'identifiant unique de l'avis à supprimer

        Returns:
            dict: Message de confirmation et code HTTP 200 en cas de succès
            dict: Message d'erreur et code HTTP approprié en cas d'échec
        """
        try:
            # Vérification que l'avis existe avant de tenter de le supprimer
            hbnb_facade = HBnBFacade()
            existing_review = hbnb_facade.get_review(review_id)

            if not existing_review:
                return {'message': f'Review with ID {review_id} not found'}, 404

            # Suppression de l'avis via la façade
            success = hbnb_facade.delete_review(review_id)

            # Vérification du succès de l'opération
            if success:
                return {
                    'message': f'Review with ID {review_id} deleted successfully'}, 200
            else:
                return {
                    'message': f'Failed to delete review with ID {review_id}'}, 500

        except Exception as e:
            # Journalisation et gestion des erreurs imprévues
            print(f"Error deleting review: {str(e)}")
            return {'message': f'An error occurred: {str(e)}'}, 500


@api.route('/places/<place_id>/reviews')
class PlaceReviewList(Resource):
    @api.response(200, 'List of reviews for the place retrieved successfully')
    @api.response(404, 'Place not found')
    @api.response(500, 'Server error')
    def get(self, place_id):
        """Récupère tous les avis pour un hébergement spécifique.

        Args:
            place_id (str): L'identifiant unique
            de l'hébergement dont on veut les avis

        Returns:
            list: Liste des avis pour l'hébergement
            et code HTTP 200 en cas de succès
            list: Liste vide si aucun avis n'existe pour cet hébergement
            dict: Message d'erreur et code HTTP approprié en cas d'échec
        """
        try:
            # Vérification que l'hébergement existe
            hbnb_facade = HBnBFacade()
            place = hbnb_facade.get_place(place_id)

            if not place:
                return {'message': f'Place with ID {place_id} not found'}, 404

            # Récupération des avis pour cet hébergement
            reviews = hbnb_facade.get_reviews_by_place(place_id)

            # Si aucun avis n'existe, retourner une liste vide
            if not reviews:
                return [], 200

            # Formatage des données pour la réponse
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
            # Journalisation et gestion des erreurs imprévues
            print(f"Error retrieving reviews for place: {str(e)}")
            return {'message': f'An error occurred: {str(e)}'}, 500
