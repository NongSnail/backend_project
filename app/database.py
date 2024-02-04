from pymongo import MongoClient
import pymongo
from app.config import settings

client = MongoClient(
    settings.DATABASE_URL,
    serverSelectionTimeoutMS=3000,
)

try:
    conn = client.server_info()
    print(f'Connected to MongoDB {conn.get("version")}')
except Exception as e:
    print(f"Unable to connect to the MongoDB server. Error: {e}")

db = client[settings.MONGO_INITDB_DATABASE]
User = db.users
User_Message = db.user_message
User.create_index([("email", pymongo.ASCENDING)], unique=True)
User_Message.create_index(["user_message"])
