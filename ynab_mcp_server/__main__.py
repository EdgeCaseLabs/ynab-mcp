"""
Main entry point for YNAB MCP Server
"""
import sys
import os
import logging
import argparse
from dotenv import load_dotenv

from .server import mcp, register_tools, setup_debug_logging

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the YNAB MCP server"""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="YNAB MCP Server")
    parser.add_argument("--logging", action="store_true", help="Enable debug logging for tool calls")
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup debug logging based on flag
    setup_debug_logging(args.logging)
    
    # Initialize tools
    register_tools()
    
    # Run the server in STDIO mode for Claude Desktop
    try:
        logger.info("Starting YNAB MCP server with STDIO transport")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.exception(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()