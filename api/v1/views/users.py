#!/usr/bin/python3
'''Contains the Users view for the API.'''
from flask import jsonify, request
from api.v1.views import app_views
from models import storage
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
from models.user import User


@app_views.route('/users', methods=['GET', 'POST'])
@app_views.route('/users/<user_id>', methods=['GET', 'DELETE', 'PUT'])
def handle_users(user_id=None):
    '''Check for allowed methodes'''
    handlers = {
        'GET': get_users,
        'DELETE': remove_user,
        'POST': add_user,
        'PUT': update_user,
    }
    if request.method in handlers:
        return handlers[request.method](user_id)
    else:
        raise MethodNotAllowed(list(handlers.keys()))


def get_users(user_id=None):
    '''
    GET method: Gets a user with the given id
    otherwise return all users
    '''
    all_users = storage.all(User).values()
    if user_id:
        res = list(filter(lambda x: x.id == user_id, all_users))
        if res:
            return jsonify(res[0].to_dict())
        raise NotFound()
    all_users = list(map(lambda x: x.to_dict(), all_users))
    return jsonify(all_users)


def add_user(user_id=None):
    '''
    POST method: Adds a new user
    '''
    inputData = request.get_json()
    if type(inputData) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'email' not in inputData:
        raise BadRequest(description='Missing email')
    if 'password' not in inputData:
        raise BadRequest(description='Missing password')
    new_user = User(**inputData)
    new_user.save()
    return jsonify(new_user.to_dict()), 201


def update_user(user_id=None):
    '''
    PUT method: Updates an user with the given id.
    '''
    inputKeys = ('id', 'email', 'created_at', 'updated_at')
    all_users = storage.all(User).values()
    res = list(filter(lambda x: x.id == user_id, all_users))
    if res:
        inputData = request.get_json()
        if type(inputData) is not dict:
            raise BadRequest(description='Not a JSON')
        userToUpdate = res[0]
        for key, value in inputData.items():
            if key not in inputKeys:
                setattr(userToUpdate, key, value)
        userToUpdate.save()
        return jsonify(userToUpdate.to_dict()), 200
    raise NotFound()


def remove_user(user_id=None):
    '''
    DELETE method: Removes a user with the given id.
    '''
    all_users = storage.all(User).values()
    res = list(filter(lambda x: x.id == user_id, all_users))
    if res:
        storage.delete(res[0])
        storage.save()
        return jsonify({}), 200
    raise NotFound()
