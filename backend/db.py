import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "visionsort")

class Database:
    client: AsyncIOMotorClient = None
    
db = Database()

async def connect_to_mongo():
    """Connect to MongoDB on app startup."""
    print(f"Connecting to MongoDB at {MONGO_URL}...")
    try:
        db.client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        # Verify connection
        await db.client.server_info()
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        print("Falling back to in-memory mode if DB not available (will not persist).")
        db.client = None

async def close_mongo_connection():
    """Close MongoDB connection on app shutdown."""
    if db.client:
        db.client.close()
        print("MongoDB connection closed.")

def get_database():
    if db.client:
        return db.client[DB_NAME]
    return None
