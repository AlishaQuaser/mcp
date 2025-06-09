from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel

class ToolInput(BaseModel):
    """Base model for tool inputs"""
    pass

class ToolOutput(BaseModel):
    """Base model for tool outputs"""
    success: bool
    data: Any = None
    error: str = None
    metadata: Dict[str, Any] = {}

class BaseTool(ABC):
    """
    Base class for all MCP tools
    Others can extend this class to create new tools
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for this tool's input"""
        pass

    @abstractmethod
    async def execute(self, inputs: Dict[str, Any]) -> ToolOutput:
        """Execute the tool with given inputs"""
        pass

    def get_tool_info(self) -> Dict[str, Any]:
        """Return tool information for MCP protocol"""
        return {
            "name": self.name,
            "description": self.description,
            "schema": self.get_schema()
        }