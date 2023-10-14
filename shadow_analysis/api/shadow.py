from flask import Blueprint, request, jsonify
# from mflix.db import get_movie, get_movies, get_movies_by_country, \
#     get_movies_faceted, add_comment, update_comment, delete_comment

# from mflix.api.utils import expect
from datetime import datetime
import shadow_analysis.api.shadowingfunction_wallheight_13 as shadow_func
from shadow_analysis.db import insert_shadow_result

import numpy as np
import pandas as pd
import uuid
import os 
import sys

shadow_analysis_api_v1 = Blueprint(
    'shadow_analysis_api_v1', 'shadow_analysis_api_v1', url_prefix='/api/v1/shadow_analysis')

@shadow_analysis_api_v1.route('/test', methods=['GET'])
def test():
    x = {
        "Name":"shreyas"
    }
    return jsonify(x)

@shadow_analysis_api_v1.route('/calculate-shadow', methods=['POST'])
def calculate_shadow():
    try:
        print("Received request to calculate shadow")
        print("Headers:", request.headers)

        data_json = request.json
        # Validate data
        if not all(key in data_json for key in ['azimuth', 'altitude', 'dsm', 'scale']):
            print("Missing required data")
            return jsonify({"error": "Missing required data"}), 400

        # Extract shadow calculation parameters from the request data
        azimuth = data_json['azimuth']
        altitude = data_json['altitude']
        dsm = np.array(data_json['dsm'])  # Ensure this is converted to a numpy array
        scale = data_json['scale']
        walls = np.zeros((dsm.shape[0], dsm.shape[1]))
        dirwalls = np.zeros((dsm.shape[0], dsm.shape[1])) * np.pi / 180.

        # Perform shadow calculation
        sh, wallsh, wallsun, facesh, facesun = shadow_func.shadowingfunction_wallheight_13(
            dsm, azimuth, altitude, scale, walls, dirwalls
        )
        print("Shadow Analysis Done")

        # Store the results in MongoDB
        result = {
            '_id': str(uuid.uuid4()),
            "sh": sh.tolist(),
            "timestamp": pd.Timestamp.now().isoformat()
        }
        insert_shadow_result(result)
        return jsonify({"message": "Shadow analysis completed and stored in MongoDB", "id": result['_id']})

    except Exception as e:
        print(f"Error occurred: {e}")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return jsonify({"error": str(e)}), 500