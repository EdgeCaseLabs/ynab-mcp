"""
YNAB MCP Server - A Model Context Protocol server for YNAB API
"""

__version__ = "0.1.0"
__author__ = "Wes Thomas"
__email__ = "westhomas@edgecaselabs.com"

from .server import mcp, get_ynab_client, register_tools, setup_debug_logging

__all__ = ["mcp", "get_ynab_client", "register_tools", "setup_debug_logging"]