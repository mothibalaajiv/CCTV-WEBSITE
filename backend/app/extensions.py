import certifi
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from pymongo import MongoClient

jwt = JWTManager()
swagger = Swagger()
mongo_client = None
db = None

def init_mongo(app):
    global mongo_client, db
    try:
        import dns.resolver
        res = dns.resolver.Resolver(configure=True)
        for ns in ['8.8.8.8', '1.1.1.1']:
            if ns not in res.nameservers:
                res.nameservers.append(ns)
        res.lifetime = 10
        res.timeout = 5
        dns.resolver.default_resolver = res
    except Exception:
        pass

    mongo_client = MongoClient(
        app.config["MONGO_URI"],
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=15000,
        connectTimeoutMS=15000,
        socketTimeoutMS=15000
    )
    db = mongo_client.get_default_database()

