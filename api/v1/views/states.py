#!/usr/bin/python3
'''Contains the states view for the API.'''
from flask import jsonify, request
from api.v1.views import app_views
from models.state import State
from models import storage
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest


ALLOWED_METHODS = ['GET', 'DELETE', 'POST', 'PUT']


@app_views.route('/states', methods=['GET', 'POST'])
@app_views.route('/states/<state_id>', methods=['GET', 'DELETE', 'PUT'])
def handle_states(state_id=None):
    '''Check for allowed methodes'''
    handlers = {
        'GET': get_states,
        'DELETE': remove_state,
        'POST': add_state,
        'PUT': update_state,
    }
    if request.method in handlers:
        return handlers[request.method](state_id)
    else:
        raise MethodNotAllowed(list(handlers.keys()))


def get_states(state_id=None):
    '''
    GET method: Gets a state with the given id
    otherwise return all states
    '''
    all_states = storage.all(State).values()
    if state_id:
        res = list(filter(lambda x: x.id == state_id, all_states))
        if res:
            return jsonify(res[0].to_dict())
        raise NotFound()
    all_states = list(map(lambda x: x.to_dict(), all_states))
    return jsonify(all_states)


def add_state(state_id=None):
    '''
    POST method: Adds a new state
    '''
    inputData = request.get_json()
    if type(inputData) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'name' not in inputData:
        raise BadRequest(description='Missing name')
    new_state = State(**inputData)
    new_state.save()
    return jsonify(new_state.to_dict()), 201


def update_state(state_id=None):
    '''
    PUT method: Updates a state with the given id.
    '''
    inputKeys = ('id', 'created_at', 'updated_at')
    all_states = storage.all(State).values()
    res = list(filter(lambda x: x.id == state_id, all_states))
    if res:
        inputData = request.get_json()
        if type(inputData) is not dict:
            raise BadRequest(description='Not a JSON')
        stateToUpdate = res[0]
        for key, value in inputData.items():
            if key not in inputKeys:
                setattr(stateToUpdate, key, value)
        stateToUpdate.save()
        return jsonify(stateToUpdate.to_dict()), 200
    raise NotFound()


def remove_state(state_id=None):
    '''
    DELETE method: Removes a state with the given id.
    '''
    all_states = storage.all(State).values()
    res = list(filter(lambda x: x.id == state_id, all_states))
    if res:
        storage.delete(res[0])
        storage.save()
        return jsonify({}), 200
    raise NotFound()
