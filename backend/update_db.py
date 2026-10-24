from pymongo import MongoClient

client = MongoClient("mongodb+srv://root:root@cluster0.segr9.mongodb.net/vms_db?retryWrites=true&w=majority")
db = client.get_default_database()
db.cameras.update_one({"camera_code": "100001"}, {"$set": {"current_ip": "192.168.1.4"}})
print("Updated successfully")
