from flask import Blueprint, request, jsonify
# from mflix.db import get_movie, get_movies, get_movies_by_country, \
#     get_movies_faceted, add_comment, update_comment, delete_comment

# from mflix.api.utils import expect
from datetime import datetime
from shadow_analysis.api.solarposition import get_solarposition
import shadow_analysis.api.shadowingfunction_wallheight_13 as shadow_func
from shadow_analysis.db import insert_shadow_result

import numpy as np
import pandas as pd
import uuid
import gzip 
import json
import base64

shadow_analysis_api_v1 = Blueprint(
    'shadow_analysis_api_v1', 'shadow_analysis_api_v1', url_prefix='/api/v1/shadow_analysis')

@shadow_analysis_api_v1.route('/hello', methods=['GET'])
def hello():
    x = {
        "Name":"shreyas"
    }
    return jsonify(x)

@shadow_analysis_api_v1.route('/solar-position', methods=['POST'])
def solar_position():
    data = request.json
    utc_offset = -6
    timestamps = pd.to_datetime(data['timestamp'])
    lat = float(data['latitude'])
    lon = float(data['longitude'])

    # Calculate the solar position
    df_solar = get_solarposition(timestamps, lat, lon)
    timestamps = pd.DatetimeIndex(df_solar.index) + pd.DateOffset(hours=utc_offset)
    formatted_timestamp = timestamps.strftime("%Y-%m-%d %H:%M:%S")
    # Extract and return the solar data
    solar_data = {
        "timestamp": formatted_timestamp.tolist(),
        "elevation": df_solar['elevation'].tolist(),
        "zenith": df_solar['zenith'].tolist(),
        "apparent_elevation": df_solar['apparent_elevation'].tolist(),
        "apparent_zenith": df_solar['apparent_zenith'].tolist(),
        "equation_of_time": df_solar['equation_of_time'].tolist(),
        "azimuth": df_solar['azimuth'].tolist()
    }
    return jsonify(solar_data)

@shadow_analysis_api_v1.route('/calculate-shadow', methods=['POST'])
def calculate_shadow():
    data = request.json
    decompressed_data_json = gzip.decompress(data).decode()

    # Extract shadow calculation parameters from the request data
    azimuth = data['azimuth']
    altitude = data['altitude']
    dsm = decompressed_data_json['dsm']
    scale = data['scale']
    walls = np.zeros((dsm.shape[0], dsm.shape[1]))
    dirwalls = np.zeros((dsm.shape[0], dsm.shape[1]))* np.pi / 180.

    # Perform shadow calculation
    sh, wallsh, wallsun, facesh, facesun = shadow_func.shadowingfunction_wallheight_13(
        dsm, azimuth, altitude, scale, walls, dirwalls
    )

    # Store the results in MongoDB
    result = {
        '_id': str(uuid.uuid4()),
        "sh": sh.tolist(),
        "wallsh": wallsh.tolist(),
        "wallsun": wallsun.tolist(),
        "facesh": facesh.tolist(),
        "facesun": facesun.tolist(),
        "timestamp": pd.Timestamp.now().isoformat()
    }
    insert_shadow_result(result)
    return jsonify({"message": "Shadow analysis completed and stored in MongoDB", "id": result['_id']})