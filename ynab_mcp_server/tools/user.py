"""
User-related MCP tools for YNAB
"""
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
import ynab
from ynab.api import user_api
import logging

logger = logging.getLogger(__name__)

# Import the logging decorator
from ..debug_utils import log_tool_call

def register_tools(mcp: FastMCP, get_client_func):
    """Register user-related tools with the MCP server"""
    
    @mcp.tool()
    @log_tool_call
    def get_user() -> Dict[str, Any]:
        """
        Get authenticated user information.
        
        Returns:
            User details including ID and name
        """
        try:
            with get_client_func() as api_client:
                api = user_api.UserApi(api_client)
                response = api.get_user()
                
                user = response.data.user
                return {
                    "id": user.id,
                    "name": user.name if hasattr(user, 'name') else None,
                    "message": "User information retrieved successfully"
                }
        except Exception as e:
            logger.exception(f"Error getting user information: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    @log_tool_call
    def verify_api_key() -> Dict[str, Any]:
        """
        Verify that the YNAB API key is valid and working.
        
        Returns:
            Verification status and user information if successful
        """
        try:
            with get_client_func() as api_client:
                api = user_api.UserApi(api_client)
                response = api.get_user()
                
                user = response.data.user
                return {
                    "valid": True,
                    "user_id": user.id,
                    "message": "API key is valid and authenticated"
                }
        except Exception as e:
            logger.exception(f"API key verification failed: {e}")
            return {
                "valid": False,
                "error": str(e),
                "message": "API key verification failed. Please check your YNAB_API_KEY environment variable."
            }