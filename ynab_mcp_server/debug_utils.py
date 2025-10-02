"""
Debug utilities for YNAB MCP Server
"""
import sys
import functools
import inspect
from typing import Dict, Any

# Global flag to control debug logging
LOGGING_ENABLED = False


def set_logging_enabled(enabled: bool) -> None:
    """Enable or disable debug logging globally"""
    global LOGGING_ENABLED
    LOGGING_ENABLED = enabled


def debug_log_tool_call(tool_name: str, arguments: Dict[str, Any]) -> None:
    """Log tool calls in a terse function signature format"""
    # Format arguments as key=value pairs, truncating long values
    def format_value(v):
        if isinstance(v, str) and len(v) > 50:
            return f'"{v[:47]}..."'
        return repr(v)
    
    args_str = ", ".join(f"{k}={format_value(v)}" for k, v in arguments.items())
    log_message = f"TOOL_CALL: {tool_name}({args_str})"
    
    # Log to stderr (captured by Claude Desktop)
    print(log_message, file=sys.stderr, flush=True)


def log_tool_call(func):
    """Decorator to log tool calls automatically"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Only log if logging is enabled
        if LOGGING_ENABLED:
            # Get function signature to map args to parameter names
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Log the call
            debug_log_tool_call(func.__name__, bound_args.arguments)
        
        # Call the original function
        return func(*args, **kwargs)
    
    return wrapper