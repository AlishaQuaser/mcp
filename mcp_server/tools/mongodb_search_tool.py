from typing import Dict, Any, List
from pydantic import BaseModel, Field
from .base_tool import BaseTool, ToolOutput
from database.mongodb_client import mongodb_client
from utils.logger import logger

class MongoDBSearchInput(BaseModel):
    """Input model for MongoDB search tool"""
    query: Dict[str, Any] = Field(default_factory=dict, description="MongoDB query dictionary")
    limit: int = Field(default=10, description="Maximum number of documents to return", ge=1, le=100)
    skip: int = Field(default=0, description="Number of documents to skip", ge=0)
    fields: List[str] = Field(default=None, description="Specific fields to return (optional)")

class MongoDBSearchTool(BaseTool):
    """
    MongoDB search tool for MCP architecture
    Searches documents in MongoDB collection and returns structured results
    """

    def __init__(self):
        super().__init__(
            name="mongodb_search",
            description="Search documents in MongoDB collection using query parameters"
        )

    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for MongoDB search inputs"""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "object",
                    "description": "MongoDB query dictionary (e.g., {'name': 'John', 'age': {'$gt': 25}})",
                    "default": {}
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of documents to return",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 10
                },
                "skip": {
                    "type": "integer",
                    "description": "Number of documents to skip for pagination",
                    "minimum": 0,
                    "default": 0
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to return (optional)",
                    "default": None
                }
            },
            "required": []
        }

    async def execute(self, inputs: Dict[str, Any]) -> ToolOutput:
        """
        Execute MongoDB search with given parameters

        Args:
            inputs: Dictionary containing query, limit, skip, and fields

        Returns:
            ToolOutput with documents and metadata
        """
        try:
            # Validate inputs
            search_input = MongoDBSearchInput(**inputs)

            logger.info("Executing MongoDB search",
                        query=search_input.query,
                        limit=search_input.limit,
                        skip=search_input.skip)

            # Execute search
            documents = mongodb_client.search_documents(
                query=search_input.query,
                limit=search_input.limit,
                skip=search_input.skip
            )

            # Filter fields if specified
            if search_input.fields:
                filtered_documents = []
                for doc in documents:
                    filtered_doc = {}
                    for field in search_input.fields:
                        if field in doc:
                            filtered_doc[field] = doc[field]
                    # Always include _id for reference
                    if '_id' in doc:
                        filtered_doc['_id'] = doc['_id']
                    filtered_documents.append(filtered_doc)
                documents = filtered_documents

            # Get total count for metadata
            total_count = mongodb_client.count_documents(search_input.query)

            # Prepare metadata
            metadata = {
                "total_count": total_count,
                "returned_count": len(documents),
                "query": search_input.query,
                "limit": search_input.limit,
                "skip": search_input.skip,
                "has_more": total_count > (search_input.skip + len(documents))
            }

            logger.info("MongoDB search completed successfully",
                        returned_count=len(documents),
                        total_count=total_count)

            return ToolOutput(
                success=True,
                data=documents,
                metadata=metadata
            )

        except Exception as e:
            error_msg = f"MongoDB search failed: {str(e)}"
            logger.error("MongoDB search error", error=error_msg)

            return ToolOutput(
                success=False,
                error=error_msg,
                metadata={"query": inputs.get("query", {})}
            )