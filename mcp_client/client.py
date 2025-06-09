import requests
import json
from typing import Dict, Any, List, Optional
from config.settings import settings
from utils.logger import logger

class MCPClient:
    """
    MCP Client for communicating with MCP Server
    Sends prompts and receives structured document results
    """

    def __init__(self, server_url: Optional[str] = None):
        self.server_url = server_url or f"http://{settings.MCP_SERVER_HOST}:{settings.MCP_SERVER_PORT}"
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": f"MCP-Client/{settings.MCP_VERSION}"
        })

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make HTTP request to MCP server

        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint
            data: Request data for POST requests

        Returns:
            Response JSON data
        """
        try:
            url = f"{self.server_url}{endpoint}"

            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error("MCP request failed",
                         method=method,
                         endpoint=endpoint,
                         error=str(e))
            raise

    def health_check(self) -> Dict[str, Any]:
        """
        Check if MCP server is healthy

        Returns:
            Health status information
        """
        try:
            result = self._make_request("GET", "/health")
            logger.info("Health check completed", status=result.get("status"))
            return result
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return {"status": "unhealthy", "error": str(e)}

    def list_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of available tools from MCP server

        Returns:
            List of available tools with their schemas
        """
        try:
            result = self._make_request("GET", "/tools")
            tools = result.get("tools", [])
            logger.info("Available tools retrieved", count=len(tools))
            return tools
        except Exception as e:
            logger.error("Failed to list tools", error=str(e))
            return []

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific tool

        Args:
            tool_name: Name of the tool

        Returns:
            Tool information or None if not found
        """
        try:
            result = self._make_request("GET", f"/tools/{tool_name}")
            logger.info("Tool info retrieved", tool_name=tool_name)
            return result
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning("Tool not found", tool_name=tool_name)
                return None
            raise
        except Exception as e:
            logger.error("Failed to get tool info", tool_name=tool_name, error=str(e))
            return None

    def search_documents(self,
                         query: Dict[str, Any] = None,
                         limit: int = 10,
                         skip: int = 0,
                         fields: List[str] = None) -> Dict[str, Any]:
        """
        Search documents using MongoDB search tool

        Args:
            query: MongoDB query dictionary
            limit: Maximum number of documents to return
            skip: Number of documents to skip
            fields: Specific fields to return

        Returns:
            Search results with documents and metadata
        """
        try:
            request_data = {
                "tool_name": "mongodb_search",
                "inputs": {
                    "query": query or {},
                    "limit": limit,
                    "skip": skip
                },
                "metadata": {
                    "client_request": True,
                    "timestamp": None  # Server will add timestamp
                }
            }

            if fields:
                request_data["inputs"]["fields"] = fields

            logger.info("Searching documents",
                        query=query,
                        limit=limit,
                        skip=skip)

            result = self._make_request("POST", "/execute", request_data)

            if result.get("success"):
                logger.info("Document search successful",
                            returned_count=len(result.get("data", [])),
                            total_count=result.get("metadata", {}).get("total_count", 0))
            else:
                logger.error("Document search failed", error=result.get("error"))

            return result

        except Exception as e:
            logger.error("Document search error", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "data": [],
                "metadata": {}
            }

    def execute_custom_tool(self,
                            tool_name: str,
                            inputs: Dict[str, Any],
                            metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute any custom tool on MCP server

        Args:
            tool_name: Name of the tool to execute
            inputs: Input parameters for the tool
            metadata: Additional metadata for the request

        Returns:
            Tool execution results
        """
        try:
            request_data = {
                "tool_name": tool_name,
                "inputs": inputs,
                "metadata": metadata or {}
            }

            logger.info("Executing custom tool",
                        tool_name=tool_name,
                        inputs=inputs)

            result = self._make_request("POST", "/execute", request_data)

            if result.get("success"):
                logger.info("Custom tool execution successful", tool_name=tool_name)
            else:
                logger.error("Custom tool execution failed",
                             tool_name=tool_name,
                             error=result.get("error"))

            return result

        except Exception as e:
            logger.error("Custom tool execution error",
                         tool_name=tool_name,
                         error=str(e))
            return {
                "success": False,
                "error": str(e),
                "data": None,
                "metadata": {"tool_name": tool_name}
            }

    def process_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Process a natural language prompt and return structured results
        This is a simple implementation - you can enhance it later

        Args:
            prompt: Natural language prompt

        Returns:
            Structured results from document search
        """
        try:
            # Simple prompt processing - you can enhance this later
            # For now, it performs a basic text search

            # Extract potential search terms from prompt
            search_terms = prompt.lower().strip()

            # Create a basic text search query
            # This assumes your documents have a 'content' or 'text' field
            query = {
                "$or": [
                    {"content": {"$regex": search_terms, "$options": "i"}},
                    {"title": {"$regex": search_terms, "$options": "i"}},
                    {"description": {"$regex": search_terms, "$options": "i"}}
                ]
            }

            logger.info("Processing prompt", prompt=prompt, generated_query=query)

            # Execute search
            result = self.search_documents(query=query, limit=20)

            # Add prompt processing metadata
            if result.get("metadata"):
                result["metadata"]["original_prompt"] = prompt
                result["metadata"]["query_type"] = "text_search"

            return result

        except Exception as e:
            logger.error("Prompt processing error", prompt=prompt, error=str(e))
            return {
                "success": False,
                "error": f"Prompt processing failed: {str(e)}",
                "data": [],
                "metadata": {"original_prompt": prompt}
            }

# Global client instance
mcp_client = MCPClient()