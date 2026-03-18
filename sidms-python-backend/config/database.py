from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.uri = os.getenv('MONGODB_URI')
        self.client = None
        self.db = None
    
    def connect(self):
        try:
            self.client = MongoClient(self.uri, server_api=ServerApi('1'))
            self.db = self.client['sidms-cluster']
            # Test connection
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB Atlas successfully!")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection error: {e}")
            return False
    
    def get_db(self):
        if not self.db:
            self.connect()
        return self.db
    
    def close(self):
        if self.client:
            self.client.close()

# Global database instance
db_instance = Database()
db = db_instance.get_db()
