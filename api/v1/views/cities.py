#!/usr/bin/python3
'''Contains the Cities view for the API.'''
from flask import jsonify, request
from api.v1.views import app_views
from models.state import State
from models import storage
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
from models.city import City


@app_views.route('/states/<state_id>/cities', methods=['GET', 'POST'])
@app_views.route('/cities/<city_id>', methods=['GET', 'DELETE', 'PUT'])
def handle_cities(city_id=None, state_id=None):
    '''Check for allowed methodes'''
    handlers = {
        'GET': get_cities,
        'DELETE': remove_city,
        'POST': add_city,
        'PUT': update_city,
    }
    if request.method in handlers:
        return handlers[request.method](city_id, state_id)
    else:
        raise MethodNotAllowed(list(handlers.keys()))


def get_cities(city_id=None, state_id=None):
    '''
    GET method: Gets a city with the given id
    otherwise return all cities in state
    '''
    if state_id:
        state = storage.get(State, state_id)
        if state:
            cities = list(map(lambda x: x.to_dict(), state.cities))
            return jsonify(cities)
    elif city_id:
        city = storage.get(City, city_id)
        if city:
            return jsonify(city.to_dict())
    raise NotFound()


def add_city(city_id=None, state_id=None):
    '''
    POST method: Adds a new city
    '''
    state = storage.get(State, state_id)
    if not state:
        raise NotFound()
    inputData = request.get_json()
    if type(inputData) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'name' not in inputData:
        raise BadRequest(description='Missing name')
    inputData['state_id'] = state_id
    new_city = City(**inputData)
    new_city.save()
    return jsonify(new_city.to_dict()), 201


def update_city(city_id=None, state_id=None):
    '''
    PUT method: Updates a city with the given id.
    '''
    inputKeys = ('id', 'state_id', 'created_at', 'updated_at')
    if city_id:
        cityToUpdate = storage.get(City, city_id)
        if cityToUpdate:
            inputData = request.get_json()
            if type(inputData) is not dict:
                raise BadRequest(description='Not a JSON')
            for key, value in inputData.items():
                if key not in inputKeys:
                    setattr(cityToUpdate, key, value)
            cityToUpdate.save()
            return jsonify(cityToUpdate.to_dict()), 200
    raise NotFound()


def remove_city(city_id=None, state_id=None):
    '''
    DELETE method: Removes a state with the given id.
    '''
    all_cities = storage.all(City).values()
    res = list(filter(lambda x: x.id == city_id, all_cities))
    if res:
        storage.delete(res[0])
        storage.save()
        return jsonify({}), 200
    raise NotFound()
