import requests
import json
import base64
import gzip 
import pandas as pd
import numpy as np
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import gridfs
import bson

def solar_position_api_call_test(df_solar_data):
    # API endpoint for solar position
    lon = -95.30052
    lat = 29.73463
   
    url = 'http://127.0.0.1:5001/api/v1/shadow_analysis/solar-position'
    timestamps = df_solar_data.index.strftime("%Y-%m-%d %H:%M:%S").tolist()
    # Replace with actual values for timestamp, latitude, and longitude
    data = {
        'timestamp': timestamps,
        'latitude': lat,
        'longitude': lon
    }

    # Make a POST request to the API
    response = requests.post(url, json=data)

    # Print the status code and the response JSON
    print('Status code:', response.status_code)
    if response.status_code == 200:
        print('Response JSON:', json.dumps(response.json(), indent=4))
        data = response.json()
    else:
        print('Failed to retrieve data')
    return response.json()

def calculate_shadow_api_call_test(df_solar_data,data):
    i = 0
    scale = 1

    altitude = data['elevation'][i]
    azimuth = data['azimuth'][i]
    dt = pd.to_datetime(data['timestamp'])
    hour = dt[i].hour
    minute = dt[i].minute
    print(altitude)
    print(azimuth)

    # API endpoint for solar position
    url = 'http://127.0.0.1:5001/api/v1/shadow_analysis/calculate-shadow'
    # timestamps = df_solar_data.index.strftime("%Y-%m-%d %H:%M:%S").tolist()
    # Replace with actual values for timestamp, latitude, and longitude

    dsm = np.load('./dsm_local_array.npy')
    dsm = np.nan_to_num(dsm, nan=0)

    print(dsm.shape)
    data = {
        'azimuth': azimuth,
        'altitude': altitude,
        'scale':scale,
        'dsm': dsm.tolist()
    }

    data_headers = {'Content-type': 'application/json'}

    print('Headers:', data_headers)

    # Make a POST request to the API
    response = requests.post(url, json=data, headers=data_headers, timeout=200)

    # Print the status code and the response JSON
    print('Status code:', response.status_code)

    if response.status_code == 200:
        print('Response JSON:', json.dumps(response.json(), indent=4))
        return response.json()['id']
    else:
        print('Failed to retrieve data')
    
def visualise_data(db):
    fs = gridfs.GridFS(db)

    # Replace with the actual file id of the stored file

    file_metadata = db.fs.files.find_one({"filename": "91d5b96d-8a37-4ebb-bcd6-b8ae605c25fa"})

    if file_metadata:
        # Use the file's _id to get the file
        file_id = file_metadata['_id']
        grid_out = fs.get(file_id)
        
        # Deserialize the content to a NumPy array
        content = grid_out.read()
        result = bson.BSON(content).decode()
        print(result.keys())
    else:
        print(f"No file found with filename fs.files")

   
    


if __name__ == '__main__':
    utc_offset= -6
    # Create a date range from 6:00 to 20:00 with a 10-minute interval
    timestamps = pd.date_range('2023-09-12 11:00', '2023-09-12 11:10', freq='30T')

    # Create a DataFrame using the timestamps as a column
    df_solar_data = pd.DataFrame({'TimeStamp': timestamps})

    # UTC time
    df_solar_data['TimeStamp'] = pd.DatetimeIndex(df_solar_data['TimeStamp']) - pd.DateOffset(hours=utc_offset)

    # To_Datetime
    df_solar_data["TimeStamp"] = df_solar_data["TimeStamp"].apply(pd.to_datetime)
    df_solar_data.set_index("TimeStamp", inplace = True)

    # Add time index
    df_solar_data["TimeStamp"] = df_solar_data.index


    shadow_result = solar_position_api_call_test(df_solar_data)
    print(shadow_result)
    data_file_name = calculate_shadow_api_call_test(df_solar_data,shadow_result)

    # client = MongoClient('mongodb+srv://shadowanalysis:shadowanalysis123@shadowanalysiscluster0.ovvv1uj.mongodb.net/?retryWrites=true&w=majority')
    # db = client['shadow_db']
    # visualise_data(db,data_file_name)
    
