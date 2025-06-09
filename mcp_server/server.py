from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
from .handlers.tool_handler import tool_handler
from config.settings import settings
from utils.logger import logger
import uvicorn

# Request/Response Models
class MCPRequest(BaseModel):
    """MCP protocol request model"""
    tool_name: str
    inputs: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}

class MCPResponse(BaseModel):
    """MCP protocol response model"""
    success: bool
    data: Any = None
    error: str = None
    metadata: Dict[str, Any] = {}
    mcp_version: str = settings.MCP_VERSION

class ToolListResponse(BaseModel):
    """Response model for tool listing"""
    tools: List[Dict[str, Any]]
    count: int
    mcp_version: str = settings.MCP_VERSION

# FastAPI app
app = FastAPI(
    title="MCP Server",
    description="Model Context Protocol Server for Tool Execution",
    version=settings.MCP_VERSION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Server startup event"""
    logger.info("MCP Server starting up",
                version=settings.MCP_VERSION,
                host=settings.MCP_SERVER_HOST,
                port=settings.MCP_SERVER_PORT)

@app.on_event("shutdown")
async def shutdown_event():
    """Server shutdown event"""
    logger.info("MCP Server shutting down")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MCP Server is running",
        "version": settings.MCP_VERSION,
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.MCP_VERSION,
        "tools_count": len(tool_handler.tools)
    }

@app.get("/tools", response_model=ToolListResponse)
async def list_tools():
    """
    List all available tools

    Returns:
        List of available tools with their schemas
    """
    try:
        tools = tool_handler.get_available_tools()
        logger.info("Tools listed", count=len(tools))

        return ToolListResponse(
            tools=tools,
            count=len(tools)
        )
    except Exception as e:
        logger.error("Failed to list tools", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve tools")

@app.post("/execute", response_model=MCPResponse)
async def execute_tool(request: MCPRequest):
    """
    Execute a tool with given inputs

    Args:
        request: MCP request containing tool name and inputs

    Returns:
        MCP response with tool results
    """
    try:
        logger.info("Tool execution request received",
                    tool_name=request.tool_name,
                    inputs=request.inputs)

        # Execute the tool
        result = await tool_handler.execute_tool(
            tool_name=request.tool_name,
            inputs=request.inputs
        )

        # Merge request metadata with result metadata
        merged_metadata = {**request.metadata, **result.metadata}

        response = MCPResponse(
            success=result.success,
            data=result.data,
            error=result.error,
            metadata=merged_metadata
        )

        logger.info("Tool execution response prepared",
                    success=result.success,
                    tool_name=request.tool_name)

        return response

    except Exception as e:
        error_msg = f"Tool execution failed: {str(e)}"
        logger.error("Tool execution error", error=error_msg)

        return MCPResponse(
            success=False,
            error=error_msg,
            metadata={"tool_name": request.tool_name}
        )

@app.get("/tools/{tool_name}")
async def get_tool_info(tool_name: str):
    """
    Get information about a specific tool

    Args:
        tool_name: Name of the tool

    Returns:
        Tool information and schema
    """
    try:
        tool = tool_handler.get_tool(tool_name)
        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

        return tool.get_tool_info()

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get tool info", tool_name=tool_name, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve tool information")

def run_server():
    """Run the MCP server"""
    uvicorn.run(
        "mcp_server.server:app",
        host=settings.MCP_SERVER_HOST,
        port=settings.MCP_SERVER_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    run_server()