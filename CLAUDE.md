# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Key Development Commands

### Running the Server
```bash
# Standard mode (no debug logging)
uv run src/server.py

# With debug logging enabled
uv run src/server.py --logging
```

### Development Tools
```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Code formatting and linting
uv run black src/
uv run ruff src/
uv run mypy src/
```

### Environment Setup
1. Copy `.env.sample` to `.env` and configure YNAB API key
2. Get YNAB API key from: https://app.ynab.com/settings/developer

## Architecture Overview

This is a **Model Context Protocol (MCP) server** that exposes the YNAB (You Need A Budget) API as MCP tools for AI assistants like Claude Desktop.

### Core Architecture Concepts

**Server Structure**: Uses FastMCP framework with a modular tool registration system. The main server (`src/server.py`) imports and registers tool modules from `src/tools/`, each containing domain-specific YNAB API operations.

**Tool Organization**: Tools are grouped by YNAB domain:
- `budgets.py` - Budget management (3 tools)
- `accounts.py` - Account operations (4 tools) 
- `transactions.py` - Transaction CRUD (6 tools)
- `categories.py` - Category and budget management (6 tools)
- `payees.py` - Payee and location management (7 tools)
- `user.py` - User authentication (2 tools)

**API Client Pattern**: Uses a global YNAB API client factory (`get_ynab_client()`) that all tools access via dependency injection during registration. The client handles authentication and connection management.

**Budget ID Resolution**: All tools use a common pattern where `budget_id="default"` resolves to `DEFAULT_BUDGET_ID` environment variable or falls back to `"last-used"`.

**Debug Logging System**: Tools are decorated with `@log_tool_call` which conditionally logs function calls in format `TOOL_CALL: function_name(param1='value', param2=42)` to stderr when enabled via `--logging` flag.

### Key Implementation Patterns

**Error Handling**: All tools use try/catch with logger.error() and return `{"error": str(e)}` on exceptions.

**Date Field Access**: YNAB SDK uses `var_date` internally - access as `trans.var_date.isoformat()` not `trans.date`.

**Milliunits**: YNAB uses milliunits for money (1 dollar = 1000 milliunits). Tools provide both raw and formatted values.

**Account Filtering**: `get_accounts()` excludes closed/deleted accounts by default with `include_closed`/`include_deleted` parameters.

**Tool Registration**: Each module exports `register_tools(mcp, get_client_func)` function that decorates and registers all MCP tools with the FastMCP server.

## Critical Implementation Details

- **Transaction Date Bug**: Always use `trans.var_date.isoformat()` not `trans.date` due to YNAB SDK field naming
- **Debug Logging**: Controlled by global `LOGGING_ENABLED` flag in `debug_utils.py`, set via command-line `--logging` argument
- **Circular Imports**: Debug utilities are in separate `debug_utils.py` module to avoid import cycles
- **Environment Variables**: All configuration via `.env` file loaded with python-dotenv

## Testing and Integration

The server runs in STDIO mode for Claude Desktop integration. Configuration example in `claude_desktop_config.json` shows proper uv command setup with environment variables.

Rate limiting: YNAB API allows 200 requests/hour - server handles this gracefully but be mindful during development.