from flask import current_app
from werkzeug.local import LocalProxy
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


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
    db.shadow_data.insert_one(result)