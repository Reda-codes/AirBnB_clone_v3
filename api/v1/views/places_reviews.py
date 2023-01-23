#!/usr/bin/python3
'''Contains the Places view for the API.'''
from flask import jsonify, request
from api.v1.views import app_views
from models.state import State
from models import storage
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
from models.review import Review
from models.place import Place
from models.user import User


@app_views.route('/places/<place_id>/reviews', methods=['GET', 'POST'])
@app_views.route('/reviews/<review_id>', methods=['GET', 'DELETE', 'PUT'])
def handle_reviews(review_id=None, place_id=None):
    '''Check for allowed methodes'''
    handlers = {
        'GET': get_reviews,
        'DELETE': remove_review,
        'POST': add_review,
        'PUT': update_review,
    }
    if request.method in handlers:
        return handlers[request.method](review_id, place_id)
    else:
        raise MethodNotAllowed(list(handlers.keys()))


def get_reviews(review_id=None, place_id=None):
    '''
    GET method: Gets a review with the given id
    otherwise return all review of a place
    '''
    if place_id:
        place = storage.get(Place, place_id)
        if place:
            reviews = list(map(lambda x: x.to_dict(), place.reviews))
            return jsonify(reviews)
    elif review_id:
        review = storage.get(Review, review_id)
        if review:
            return jsonify(review.to_dict())
    raise NotFound()


def add_review(review_id=None, place_id=None):
    '''
    POST method: Adds a new reviewe
    '''
    place = storage.get(Place, place_id)
    if not place:
        raise NotFound("Place do not exist")
    inputData = request.get_json()
    if type(inputData) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'user_id' not in inputData:
        raise BadRequest(description='Missing user_id')
    user = storage.get(User, inputData['user_id'])
    if not user:
        raise NotFound(description='User do not exist')
    if 'text' not in inputData:
        raise BadRequest(description='Missing name')
    inputData['place_id'] = place_id
    new_review = Review(**inputData)
    new_review.save()
    return jsonify(new_Place.to_dict()), 201


def update_review(review_id=None, place_id=None):
    '''
    PUT method: Updates a review with the given id.
    '''
    inputKeys = ('id', 'user_id', 'place_id', 'created_at', 'updated_at')
    if review_id:
        reviewToUpdate = storage.get(Review, review_id)
        if reviewToUpdate:
            inputData = request.get_json()
            if type(inputData) is not dict:
                raise BadRequest(description='Not a JSON')
            for key, value in inputData.items():
                if key not in inputKeys:
                    setattr(reviewToUpdate, key, value)
            reviewToUpdate.save()
            return jsonify(reviewToUpdate.to_dict()), 200
    raise NotFound()


def remove_review(review_id=None):
    '''
    DELETE method: Removes a review with the given id.
    '''
    review = storage.get(Review, review_id)
    if review:
        storage.delete(review)
        storage.save()
        return jsonify({}), 200
    raise NotFound()
