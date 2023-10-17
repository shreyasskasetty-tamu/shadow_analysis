from flask import Blueprint, request, jsonify
from datetime import datetime
import shadow_analysis.api.shadowingfunction_wallheight_13 as shadow_func
from shadow_analysis.db import insert_shadow_result, get_sh_data
import matplotlib.pyplot as plt
import boto3
from io import BytesIO
import numpy as np
import pandas as pd
import uuid
import os 
import sys

shadow_analysis_api_v1 = Blueprint(
    'shadow_analysis_api_v1', 'shadow_analysis_api_v1', url_prefix='/api/v1/shadow_analysis')

@shadow_analysis_api_v1.route('/test', methods=['GET'])
def test():
    return "Shadow Analysis Service Test API Success"

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
    
@shadow_analysis_api_v1.route('/get-shadow-data',methods=['POST'])
def get_shadow_data():
    print("Received request to calculate shadow")
    print("Headers:", request.headers)

    data_json = request.json

    # Ensure that data_json contains the document_id
    if 'document_id' not in data_json:
        return jsonify({'error': 'Missing document_id in request'}), 400

    # Retrieve the document based on the provided document_id
    document_id = data_json['document_id']
    shadow_data = get_sh_data(document_id)
    if shadow_data is None:
        return jsonify({'error': 'Document not found'}), 404

    # Return the shadow data as a JSON response
    return jsonify({'shadow_data': shadow_data})

# Function to create and save the heatmap image to S3
def create_and_save_heatmap(data, cmap_name):
    try:
        timestamp_str = data.get("timestamp")
        sh = data.get("sh")
        timestamps = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%f")
        hour = timestamps.hour
        minute = timestamps.minute
        f, ax = plt.subplots(dpi=500)
        # Create a heatmap using the specified colormap
        plt.imshow(sh, cmap=cmap_name)

        plt.title("%2s" % str(hour).zfill(2) + ":%2s"% str(minute).zfill(2), pad =10, fontsize=15, color="black", weight='bold' )

        # Save the plot to a BytesIO buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Upload the image to S3
        s3 = boto3.client('s3', aws_access_key_id='access-key', aws_secret_access_key='secret-access-key')
        bucket_name = 'visualization-bucket'

        file = f'heatmap_{cmap_name}.png'
        s3.upload_fileobj(buffer, bucket_name, file,ExtraArgs={'ACL': 'public-read'} )
        
        # Return the S3 URL of the uploaded image
        return f'https://{bucket_name}.s3.amazonaws.com/{file}'
    except Exception as e:
        # Handle any exceptions that may occur during image creation or upload
        print(f"Error occurred: {e}")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return None

@shadow_analysis_api_v1.route('/visualize-shadow-data', methods=['POST'])
def get_visualisation_url():
    try:
        print("Received request to visualize shadow")
        print("Headers:", request.headers)

        data_json = request.json
        
        # Ensure that data_json contains the document_id
        if 'document_id' not in data_json:
            return jsonify({'error': 'Missing document_id in request'}), 400

        # Retrieve the document based on the provided document_id
        document_id = data_json['document_id']
        sh = get_sh_data(document_id)
        if sh is None:
            return jsonify({'error': 'Document not found'}), 404

        # List of colormaps to use
        cmap_name = 'viridis' if 'colormap' not in data_json else data_json['colormap']
        print(cmap_name)
        # Dictionary to store S3 URLs for each colormap
        colormap_url = None

        # Create and save the heatmap image to S3
        s3_url = create_and_save_heatmap(sh, cmap_name)
        
        if s3_url is not None:
            # Store the S3 URL in the dictionary
            colormap_url = s3_url

        if colormap_url:
            # Return the dictionary of S3 URLs in the response
            return jsonify(colormap_url)
        else:
            # Handle the case when no images were created or uploaded
            return jsonify({'error': 'Failed to create or upload images'}), 500
    except Exception as e:
        # Handle any unexpected exceptions that may occur
        return jsonify({'error': str(e)}), 500