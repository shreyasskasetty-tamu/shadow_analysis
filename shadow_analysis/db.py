from flask import current_app
from werkzeug.local import LocalProxy
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import gridfs
import bson

def get_db():
    """
    Configuration method to return db instance
    """
    uri = current_app.config['MONGO_URI']
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = None
    if client.get_database(current_app.config['MONGO_DBNAME']) is not None:
        db = client[current_app.config['MONGO_DBNAME']]
    else:
        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
            db = client.get_database(current_app.config['MONGO_DBNAME'])
        except Exception as e:
            print(e)
    return db

# Create a proxy to use the db instance
db = LocalProxy(get_db)


def insert_shadow_result(result):
    """
    Inserts a shadow analyis result into the shadow_data collection, with the following fields:
    """ 
    fs = gridfs.GridFS(db)
    bson_data = bson.BSON.encode(result)

    if len(bson_data) > (16 * 1024 * 1024):  # Check if the data exceeds 16MB
        # If the data is too large, store it in GridFS
        result_id = fs.put(bson_data, filename=result['_id'])
        print(f"Result stored in GridFS with file ID: {result_id}")
    else:
        # If the data size is within the limit, store it directly in the collection
        db.shadow_data.insert_one(result)
        print(f"Result stored in the collection with ID: {result['_id']}")