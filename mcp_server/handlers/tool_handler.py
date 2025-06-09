from typing import Dict, Any, List
from ..tools.base_tool import BaseTool, ToolOutput
from ..tools.mongodb_search_tool import MongoDBSearchTool
from utils.logger import logger

class ToolHandler:
    """
    Handles tool registration and execution for MCP server
    Others can register new tools here easily
    """

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """Register default tools"""
        # Register MongoDB search tool
        mongodb_tool = MongoDBSearchTool()
        self.register_tool(mongodb_tool)

        logger.info("Default tools registered",
                    tool_count=len(self.tools),
                    tools=list(self.tools.keys()))

    def register_tool(self, tool: BaseTool):
        """
        Register a new tool

        Args:
            tool: Instance of BaseTool or its subclass
        """
        self.tools[tool.name] = tool
        logger.info("Tool registered", tool_name=tool.name, tool_description=tool.description)

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of all available tools with their schemas

        Returns:
            List of tool information dictionaries
        """
        return [tool.get_tool_info() for tool in self.tools.values()]

    def get_tool(self, tool_name: str) -> BaseTool:
        """
        Get a specific tool by name

        Args:
            tool_name: Name of the tool

        Returns:
            Tool instance or None if not found
        """
        return self.tools.get(tool_name)

    async def execute_tool(self, tool_name: str, inputs: Dict[str, Any]) -> ToolOutput:
        """
        Execute a tool with given inputs

        Args:
            tool_name: Name of the tool to execute
            inputs: Input parameters for the tool

        Returns:
            ToolOutput with results or error
        """
        try:
            tool = self.get_tool(tool_name)
            if not tool:
                error_msg = f"Tool '{tool_name}' not found"
                logger.error("Tool execution failed", error=error_msg, tool_name=tool_name)
                return ToolOutput(
                    success=False,
                    error=error_msg,
                    metadata={"available_tools": list(self.tools.keys())}
                )

            logger.info("Executing tool", tool_name=tool_name, inputs=inputs)
            result = await tool.execute(inputs)

            logger.info("Tool execution completed",
                        tool_name=tool_name,
                        success=result.success)

            return result

        except Exception as e:
            error_msg = f"Tool execution error: {str(e)}"
            logger.error("Tool execution exception",
                         error=error_msg,
                         tool_name=tool_name)

            return ToolOutput(
                success=False,
                error=error_msg,
                metadata={"tool_name": tool_name}
            )

# Global tool handler instance
tool_handler = ToolHandler()