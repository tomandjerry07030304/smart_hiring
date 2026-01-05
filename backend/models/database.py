from pymongo import MongoClient
from config.config import config
import os
import ssl

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
            mongo_uri = cfg.MONGODB_URI
            
            # For MongoDB Atlas (cloud), add SSL settings
            if 'mongodb.net' in mongo_uri or 'mongodb+srv' in mongo_uri:
                print("🔒 Connecting to MongoDB Atlas with SSL...")
                # Add TLS settings if not already in URI
                if 'tls=' not in mongo_uri and 'ssl=' not in mongo_uri:
                    separator = '&' if '?' in mongo_uri else '?'
                    mongo_uri = f"{mongo_uri}{separator}tls=true&tlsAllowInvalidCertificates=true"
                
                self._client = MongoClient(
                    mongo_uri,
                    serverSelectionTimeoutMS=30000,
                    connectTimeoutMS=30000,
                    socketTimeoutMS=30000
                )
            else:
                # Local MongoDB
                self._client = MongoClient(mongo_uri)
            
            self._db = self._client[cfg.DB_NAME]
            print(f"✅ Connected to MongoDB: {cfg.DB_NAME}")
        return self._db
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
