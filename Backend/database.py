from pymongo import MongoClient
from typing import Dict, Any, Optional
from logger import logger
from config import config
from datetime import datetime
import numpy as np

class DatabaseManager:
    """
    Manages database operations for storing and retrieving audio fingerprints.
    """
    
    def __init__(self):
        """Initialize the database connection."""
        self.client = None
        self.db = None
        self.collection = None
        self.connect()

    def connect(self) -> None:
        """Establish connection to MongoDB."""
        try:
            self.client = MongoClient(config['MONGODB_URI'], serverSelectionTimeoutMS=5000)
            # Test the connection
            self.client.server_info()
            self.db = self.client[config['DB_NAME']]
            self.collection = self.db[config['COLLECTION_NAME']]
            logger.info(f"Connected to MongoDB database: {config['DB_NAME']}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            # Don't raise the exception, just log it
            # This allows the application to start even if MongoDB is not available
            self.client = None
            self.db = None
            self.collection = None

    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self.client is not None and self.db is not None and self.collection is not None

    def _convert_to_serializable(self, data: Any) -> Any:
        """
        Convert data to a MongoDB-serializable format.
        
        Args:
            data: Data to convert
            
        Returns:
            Converted data
        """
        if isinstance(data, np.ndarray):
            return data.tolist()
        elif isinstance(data, dict):
            return {k: self._convert_to_serializable(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_to_serializable(item) for item in data]
        return data

    def store_fingerprint(self, unique_id: int, fingerprint: Dict[str, Any], original_filename: str) -> bool:
        """
        Store a fingerprint in the database.
        
        Args:
            unique_id: Unique identifier for the fingerprint
            fingerprint: Fingerprint data to store
            original_filename: Original filename of the audio
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Database connection not available")
            return False

        try:
            # Check if fingerprint already exists
            if self.collection.find_one({"unique_id": unique_id}) is not None:
                logger.warning(f"Fingerprint with unique_id {unique_id} already exists")
                return False
            
            # Convert fingerprint to serializable format
            serializable_fingerprint = self._convert_to_serializable(fingerprint)
            
            # Store the fingerprint
            document = {
                "unique_id": unique_id,
                "fingerprint": serializable_fingerprint,
                "original_filename": original_filename,
                "timestamp": datetime.now()
            }
            result = self.collection.insert_one(document)
            
            if result.inserted_id is not None:
                logger.info(f"Fingerprint stored successfully with unique_id: {unique_id}")
                return True
            else:
                logger.error("Failed to store fingerprint")
                return False
                
        except Exception as e:
            logger.error(f"Error storing fingerprint: {str(e)}")
            return False

    def get_fingerprint(self, unique_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a fingerprint from the database.
        
        Args:
            unique_id: Unique identifier of the fingerprint to retrieve
            
        Returns:
            Dict containing fingerprint data or None if not found
        """
        if not self.is_connected():
            logger.error("Database connection not available")
            return None

        try:
            result = self.collection.find_one({"unique_id": unique_id})
            if result is not None:
                # Convert list back to numpy array if needed
                if isinstance(result.get('fingerprint'), list):
                    result['fingerprint'] = np.array(result['fingerprint'])
                logger.info(f"Fingerprint retrieved successfully for unique_id: {unique_id}")
                return result
            else:
                logger.warning(f"No fingerprint found for unique_id: {unique_id}")
                return None
        except Exception as e:
            logger.error(f"Error retrieving fingerprint: {str(e)}")
            return None

    def delete_fingerprint(self, unique_id: int) -> bool:
        """
        Delete a fingerprint from the database.
        
        Args:
            unique_id: Unique identifier of the fingerprint to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Database connection not available")
            return False

        try:
            result = self.collection.delete_one({"unique_id": unique_id})
            if result.deleted_count > 0:
                logger.info(f"Fingerprint deleted successfully for unique_id: {unique_id}")
                return True
            else:
                logger.warning(f"No fingerprint found to delete for unique_id: {unique_id}")
                return False
        except Exception as e:
            logger.error(f"Error deleting fingerprint: {str(e)}")
            return False

    def close(self) -> None:
        """Close the database connection."""
        try:
            if self.client is not None:
                self.client.close()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {str(e)}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

# Create a global database manager instance
db_manager = DatabaseManager() 