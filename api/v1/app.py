#!/usr/bin/python3
'''Flask web api setup'''
from flask import Flask
from models import storage
from api.v1.views import app_views
import os
from flask import jsonify
from flask_cors import CORS

app = Flask(__name__)
app_host = os.getenv('HBNB_API_HOST', '0.0.0.0')
app_port = int(os.getenv('HBNB_API_PORT', '5000'))
app.url_map.strict_slashes = False
app.register_blueprint(app_views)
CORS(app, resources={'/*': {'origins': app_host}})


@app.teardown_appcontext
def teardown_flask(exception):
    '''storage.close() method to handle'''
    storage.close()


@app.errorhandler(404)
def error_404(error):
    '''Handles 404 HTTP error'''
    return jsonify(error='Not found'), 404


if __name__ == '__main__':
    app_host = os.getenv('HBNB_API_HOST', '0.0.0.0')
    app_port = int(os.getenv('HBNB_API_PORT', '5000'))
    app.run(
        host=app_host,
        port=app_port,
        threaded=True
    )
