from flask_jwt_extended import JWTManager
from flasgger import Swagger
from pymongo import MongoClient

jwt = JWTManager()
swagger = Swagger()
mongo_client = None
db = None

def init_mongo(app):
    global mongo_client, db
    mongo_client = MongoClient(app.config["MONGO_URI"])
    db = mongo_client.get_default_database()
