import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()  

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

if not MONGO_URI:
    raise ValueError("❌ MONGO_URI is missing. Add it to .env!")

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]
