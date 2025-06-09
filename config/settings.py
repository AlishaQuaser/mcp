import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # MCP Server Configuration
    MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "localhost")
    MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", 8000))

    # MongoDB Configuration
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://hiretalent-dev:Yulwbmn87x92EQ0U@hiretalent.doscksq.mongodb.net/")
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "auth-dev")
    MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "businesses")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # MCP Protocol Version
    MCP_VERSION = "1.0.0"

settings = Settings()