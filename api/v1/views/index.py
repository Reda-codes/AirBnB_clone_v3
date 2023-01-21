#!/usr/bin/python3
'''API Index view'''
from api.v1.views import app_views
from flask import jsonify


@app_views.route('/status')
def get_status():
    '''status route'''
    return jsonify(status='OK')
