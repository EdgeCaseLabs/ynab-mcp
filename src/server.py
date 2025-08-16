"""
YNAB MCP Server - Main server implementation
"""
import os
import logging
from typing import Optional, Dict
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import ynab
from ynab.api_client import ApiClient
from ynab.configuration import Configuration

# Import tool modules
from tools import (
    budgets,
    accounts,
    transactions,
    categories,
    payees,
    user
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP(os.getenv("MCP_SERVER_NAME", "YNAB MCP Server"))

# Global YNAB client
ynab_client: Optional[ApiClient] = None


def get_ynab_client() -> ApiClient:
    """Get or create YNAB API client"""
    global ynab_client
    
    if ynab_client is None:
        api_key = os.getenv("YNAB_API_KEY")
        if not api_key:
            raise ValueError("YNAB_API_KEY environment variable is not set")
        
        configuration = Configuration(
            access_token=api_key
        )
        ynab_client = ApiClient(configuration)
        logger.info("YNAB API client initialized")
    
    return ynab_client

# Register all tool modules
def register_tools():
    """Register all YNAB tools with the MCP server"""
    try:
        # Register budget tools
        budgets.register_tools(mcp, get_ynab_client)
        logger.info("Budget tools registered")
        
        # Register account tools
        accounts.register_tools(mcp, get_ynab_client)
        logger.info("Account tools registered")
        
        # Register transaction tools
        transactions.register_tools(mcp, get_ynab_client)
        logger.info("Transaction tools registered")
        
        # Register category tools
        categories.register_tools(mcp, get_ynab_client)
        logger.info("Category tools registered")
        
        # Register payee tools
        payees.register_tools(mcp, get_ynab_client)
        logger.info("Payee tools registered")
        
        # Register user tools
        user.register_tools(mcp, get_ynab_client)
        logger.info("User tools registered")
        
        logger.info("All YNAB tools registered successfully")
    except Exception as e:
        logger.error(f"Failed to register tools: {e}")
        raise

# Initialize tools on startup
register_tools()



if __name__ == "__main__":
    # Run the server in STDIO mode for Claude Desktop
    try:
        logger.info("Starting YNAB MCP server with STDIO transport")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise