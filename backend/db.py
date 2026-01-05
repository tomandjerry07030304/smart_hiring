"""
Database module - Wrapper for backward compatibility
Imports get_db from models.database
"""
from backend.models.database import Database, get_db, db_instance

__all__ = ['Database', 'get_db', 'db_instance']
