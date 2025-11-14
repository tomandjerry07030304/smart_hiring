from pymongo import MongoClient
from config.config import config
import os

class Database:
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def connect(self, env='development'):
        """Connect to MongoDB"""
        if self._client is None:
            cfg = config[env]
            self._client = MongoClient(cfg.MONGODB_URI)
            self._db = self._client[cfg.DB_NAME]
            print(f"✅ Connected to MongoDB: {cfg.DB_NAME}")
        return self._db
    
    def get_db(self):
        """Get database instance"""
        if self._db is None:
            return self.connect()
        return self._db
    
    def close(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            print("✅ Database connection closed")

# Global database instance
db_instance = Database()

def get_db():
    """Helper function to get database"""
    return db_instance.get_db()
