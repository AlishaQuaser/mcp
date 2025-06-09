from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from typing import List, Dict, Any, Optional
from config.settings import settings
from utils.logger import logger

class MongoDBClient:
    def __init__(self):
        self.client = None
        self.database = None
        self.collection = None
        self._connect()

    def _connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(settings.MONGODB_URI)
            # Test connection
            self.client.admin.command('ping')
            self.database = self.client[settings.MONGODB_DATABASE]
            self.collection = self.database[settings.MONGODB_COLLECTION]
            logger.info("MongoDB connection established",
                        database=settings.MONGODB_DATABASE,
                        collection=settings.MONGODB_COLLECTION)
        except ConnectionFailure as e:
            logger.error("Failed to connect to MongoDB", error=str(e))
            raise

    def search_documents(self, query: Dict[str, Any], limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Search documents in MongoDB collection

        Args:
            query: MongoDB query dictionary
            limit: Maximum number of documents to return
            skip: Number of documents to skip

        Returns:
            List of matching documents
        """
        try:
            cursor = self.collection.find(query).skip(skip).limit(limit)
            documents = []

            for doc in cursor:
                # Convert ObjectId to string for JSON serialization
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
                documents.append(doc)

            logger.info("Document search completed",
                        query=query,
                        results_count=len(documents),
                        limit=limit,
                        skip=skip)

            return documents

        except PyMongoError as e:
            logger.error("MongoDB search failed", error=str(e), query=query)
            raise

    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a single document by ID"""
        try:
            from bson import ObjectId
            doc = self.collection.find_one({"_id": ObjectId(doc_id)})
            if doc:
                doc['_id'] = str(doc['_id'])
            return doc
        except Exception as e:
            logger.error("Failed to get document by ID", doc_id=doc_id, error=str(e))
            return None

    def count_documents(self, query: Dict[str, Any]) -> int:
        """Count documents matching query"""
        try:
            count = self.collection.count_documents(query)
            logger.info("Document count completed", query=query, count=count)
            return count
        except PyMongoError as e:
            logger.error("MongoDB count failed", error=str(e), query=query)
            return 0

    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Global instance
mongodb_client = MongoDBClient()