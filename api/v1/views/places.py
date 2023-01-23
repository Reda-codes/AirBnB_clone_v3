#!/usr/bin/python3
'''Contains the Places view for the API.'''
from flask import jsonify, request
from api.v1.views import app_views
from models.state import State
from models import storage
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
from models.city import City
from models.place import Place
from models.user import User


@app_views.route('/places/<place_id>', methods=['GET', 'DELETE', 'PUT'])
@app_views.route('/cities/<city_id>/places', methods=['GET', 'POST'])
def handle_places(city_id=None, place_id=None):
    '''Check for allowed methodes'''
    handlers = {
        'GET': get_places,
        'DELETE': remove_place,
        'POST': add_place,
        'PUT': update_place,
    }
    if request.method in handlers:
        return handlers[request.method](city_id, place_id)
    else:
        raise MethodNotAllowed(list(handlers.keys()))


def get_places(city_id=None, place_id=None):
    '''
    GET method: Gets a place with the given id
    otherwise return all places in city
    '''
    if city_id:
        city = storage.get(City, city_id)
        if city:
            places = list(map(lambda x: x.to_dict(), city.places))
            return jsonify(places)
    elif place_id:
        place = storage.get(Place, place_id)
        if place:
            return jsonify(place.to_dict())
    raise NotFound()


def add_place(city_id=None, place_id=None):
    '''
    POST method: Adds a new place
    '''
    city = storage.get(City, city_id)
    if not city:
        raise NotFound("City do not exist")
    inputData = request.get_json()
    if type(inputData) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'user_id' not in inputData:
        raise BadRequest(description='Missing user_id')
    user = storage.get(User, inputData['user_id'])
    if not user:
        raise NotFound(description='User do not exist')
    if 'name' not in inputData:
        raise BadRequest(description='Missing name')
    inputData['city_id'] = city_id
    new_Place = Place(**inputData)
    new_Place.save()
    return jsonify(new_Place.to_dict()), 201


def update_place(city_id=None, place_id=None):
    '''
    PUT method: Updates a place with the given id.
    '''
    inputKeys = ('id', 'user_id', 'city_id', 'created_at', 'updated_at')
    if place_id:
        placeToUpdate = storage.get(Place, place_id)
        if placeToUpdate:
            inputData = request.get_json()
            if type(inputData) is not dict:
                raise BadRequest(description='Not a JSON')
            for key, value in inputData.items():
                if key not in inputKeys:
                    setattr(placeToUpdate, key, value)
            placeToUpdate.save()
            return jsonify(placeToUpdate.to_dict()), 200
    raise NotFound()


def remove_place(city_id=None, place_id=None):
    '''
    DELETE method: Removes a state with the given id.
    '''
    all_places = storage.all(Place).values()
    res = list(filter(lambda x: x.id == place_id, all_places))
    if res:
        storage.delete(res[0])
        storage.save()
        return jsonify({}), 200
    raise NotFound()
