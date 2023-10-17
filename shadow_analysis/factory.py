import os
import configparser

from flask import Flask, render_template
from json import JSONEncoder
from flask_cors import CORS  # Import Flask-CORS
##from flask_bcrypt import Bcrypt
##from flask_jwt_extended import JWTManager
from shadow_analysis.api.shadow import shadow_analysis_api_v1

from bson import json_util, ObjectId
from datetime import datetime, timedelta



class MongoJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, ObjectId):
            return str(obj)
        return json_util.default(obj, json_util.CANONICAL_JSON_OPTIONS)

def create_app():
    config = configparser.ConfigParser()
    config.read(os.path.abspath(os.path.join(".ini")))
    app = Flask(__name__)
    app.config['MONGO_DBNAME'] = 'shadow_db'
    app.config['SECRET_KEY'] = "secret-key"
    app.config['MONGO_URI'] = config['PROD']['DB_URI']
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.json_encoder = MongoJsonEncoder
    app.register_blueprint(shadow_analysis_api_v1)
    return app
