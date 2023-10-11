import os
import configparser
from shadow_analysis.factory import create_app

config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(".ini")))

if __name__ == "__main__":
    app = create_app()
    app.config['MONGO_DBNAME'] = 'shadow_db'
    app.config['SECRET_KEY'] = "3bf9eea8de958ecdc54356f31b6b5ba249629888"
    app.config['MONGO_URI'] = config['PROD']['DB_URI']
    app.run(host='0.0.0.0',port=5001)
    