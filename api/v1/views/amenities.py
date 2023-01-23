#!/usr/bin/python3
'''Contains the Amenities view for the API.'''
from flask import jsonify, request
from api.v1.views import app_views
from models import storage
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
from models.amenity import Amenity


@app_views.route('/amenities', methods=['GET', 'POST'])
@app_views.route('/amenities/<amenity_id>', methods=['GET', 'DELETE', 'PUT'])
def handle_amenities(amenity_id=None):
    '''Check for allowed methodes'''
    handlers = {
        'GET': get_amenities,
        'DELETE': remove_amenity,
        'POST': add_amenity,
        'PUT': update_amenity,
    }
    if request.method in handlers:
        return handlers[request.method](amenity_id)
    else:
        raise MethodNotAllowed(list(handlers.keys()))


def get_amenities(amenity_id=None):
    '''
    GET method: Gets an amenity with the given id
    otherwise return all amenities
    '''
    all_amenities = storage.all(Amenity).values()
    if amenity_id:
        res = list(filter(lambda x: x.id == amenity_id, all_amenities))
        if res:
            return jsonify(res[0].to_dict())
        raise NotFound()
    all_amenities = list(map(lambda x: x.to_dict(), all_amenities))
    return jsonify(all_amenities)


def add_amenity(amenity_id=None):
    '''
    POST method: Adds a new amenity
    '''
    inputData = request.get_json()
    if type(inputData) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'name' not in inputData:
        raise BadRequest(description='Missing name')
    new_amenity = Amenity(**inputData)
    new_amenity.save()
    return jsonify(new_amenity.to_dict()), 201


def update_amenity(amenity_id=None):
    '''
    PUT method: Updates an amenity with the given id.
    '''
    inputKeys = ('id', 'created_at', 'updated_at')
    all_amenities = storage.all(Amenity).values()
    res = list(filter(lambda x: x.id == amenity_id, all_amenities))
    if res:
        inputData = request.get_json()
        if type(inputData) is not dict:
            raise BadRequest(description='Not a JSON')
        amenityToUpdate = res[0]
        for key, value in inputData.items():
            if key not in inputKeys:
                setattr(amenityToUpdate, key, value)
        amenityToUpdate.save()
        return jsonify(amenityToUpdate.to_dict()), 200
    raise NotFound()


def remove_amenity(amenity_id=None):
    '''
    DELETE method: Removes an amenity with the given id.
    '''
    all_amenities = storage.all(Amenity).values()
    res = list(filter(lambda x: x.id == amenity_id, all_amenities))
    if res:
        storage.delete(res[0])
        storage.save()
        return jsonify({}), 200
    raise NotFound()
