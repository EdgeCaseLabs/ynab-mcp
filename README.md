# YNAB MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to the YNAB (https://www.ynab.com) aka You Need A Budget API. This server exposes all YNAB API functionality as MCP tools, allowing AI assistants and other MCP clients to interact with YNAB budgets, accounts, transactions, and more.

## Features

- **Complete YNAB API Coverage**: All YNAB API methods are exposed as MCP tools
- **uv Integration**: Fast dependency management with uv
- **Type-Safe**: Built with Python type hints and Pydantic models
- **Error Handling**: Comprehensive error handling and logging
- **Debug Logging**: Optional tool call logging for debugging MCP interactions
- **Environment Configuration**: Simple configuration via environment variables
- **Organized Tool Structure**: Tools are logically grouped by category (budgets, accounts, transactions, etc.)

## Prerequisites

- Python 3.10+ with uv installed
- A YNAB account with a Personal Access Token

## Getting Your YNAB API Key

1. Log in to your YNAB account at https://app.ynab.com
2. Navigate to Account Settings
3. Go to the Developer Settings section
4. Create a new Personal Access Token
5. Save this token securely - you'll need it for configuration

## Installation

### Quick Install (Recommended)

If you have `uv` installed, you can run the server directly without cloning:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run the server directly from PyPI
uvx ynab-mcp-server

# Or with debug logging
uvx ynab-mcp-server --logging
```

### Install from PyPI

```bash
# Using pip
pip install ynab-mcp-server

# Or using uv
uv pip install ynab-mcp-server

# Run the server
ynab-mcp-server
```

### Install from Source

1. Clone the repository:
```bash
git clone https://github.com/EdgeCaseLabs/ynab-mcp.git
cd ynab-mcp
```

2. Install dependencies:
```bash
uv sync
```

3. Copy and configure environment:
```bash
cp .env.sample .env
# Edit .env with your YNAB API key
```

4. Test the server:
```bash
# Run normally
uv run python -m ynab_mcp_server

# Run with debug logging enabled
uv run python -m ynab_mcp_server --logging
```

## Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `YNAB_API_KEY` | Yes | Your YNAB Personal Access Token | - |
| `DEFAULT_BUDGET_ID` | No | Default budget ID to use when not specified | `last-used` |
| `LOG_LEVEL` | No | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `MCP_SERVER_NAME` | No | Name of the MCP server | `YNAB MCP Server` |

## Available Tools

### User Tools
- `get_user()` - Get authenticated user information
- `verify_api_key()` - Verify API key validity

### Budget Tools
- `get_budgets(include_accounts)` - Get list of budgets
- `get_budget_by_id(budget_id, last_knowledge_of_server)` - Get detailed budget information
- `get_budget_settings(budget_id)` - Get budget settings

### Account Tools
- `get_accounts(budget_id, last_knowledge_of_server, include_closed, include_deleted)` - Get accounts (excludes closed/deleted by default)
- `get_account_by_id(account_id, budget_id)` - Get specific account
- `create_account(name, type, balance, budget_id)` - Create new account
- `get_account_balance(account_id, budget_id)` - Get account balance

### Transaction Tools
- `get_transactions(budget_id, since_date, type, last_knowledge_of_server)` - Get transactions
- `get_transaction_by_id(transaction_id, budget_id)` - Get specific transaction
- `create_transaction(...)` - Create new transaction
- `update_transaction(...)` - Update existing transaction
- `delete_transaction(transaction_id, budget_id)` - Delete transaction
- `import_transactions(budget_id)` - Import transactions from linked accounts

### Category Tools
- `get_categories(budget_id, last_knowledge_of_server)` - Get all categories
- `get_category_by_id(category_id, budget_id)` - Get specific category
- `get_month_category(category_id, month, budget_id)` - Get category for specific month
- `update_category(category_id, name, note, hidden, budget_id)` - Update category
- `update_month_category(category_id, month, budgeted, budget_id)` - Update monthly budget
- `get_category_balance(category_id, month, budget_id)` - Get category balance

### Payee Tools
- `get_payees(budget_id, last_knowledge_of_server)` - Get all payees
- `get_payee_by_id(payee_id, budget_id)` - Get specific payee
- `update_payee(payee_id, name, budget_id)` - Update payee name
- `search_payees(search_term, budget_id)` - Search payees by name
- `get_payee_locations(budget_id)` - Get all payee locations
- `get_payee_location_by_id(payee_location_id, budget_id)` - Get specific location
- `get_payee_locations_by_payee(payee_id, budget_id)` - Get locations for payee

## Usage Examples

### Claude Code Plugin (Recommended)

The easiest way to use this with Claude Code is to install it as a plugin:

```bash
# Option 1: Install from local directory
cd /path/to/ynab-mcp
uv sync
cp .env.sample .env
# Edit .env with your YNAB API key
claude plugin install .

# Option 2: Install from GitHub (once published)
claude plugin install https://github.com/EdgeCaseLabs/ynab-mcp.git
# Then create .env file in ~/.claude/plugins/repos/ynab/
```

After installation, the YNAB tools will be automatically available in all your Claude Code sessions. See [.claude-plugin/README.md](.claude-plugin/README.md) for more details.

### Claude Desktop Configuration

To connect this YNAB MCP server to Claude Desktop, you need to configure it in your Claude Desktop settings.

#### Configure Claude Desktop

Create or edit your Claude Desktop configuration file:

**macOS/Linux**: `~/.config/claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add the YNAB MCP server configuration (see `claude_desktop_config.json` for a complete example):

```json
{
  "mcpServers": {
    "ynab": {
      "command": "uvx",
      "args": ["ynab-mcp-server"],
      "env": {
        "YNAB_API_KEY": "your_ynab_api_key_here",
        "DEFAULT_BUDGET_ID": "optional_default_budget_id"
      }
    }
  }
}
```

**Alternative configurations:**

If you installed from source:
```json
{
  "mcpServers": {
    "ynab": {
      "command": "/path/to/uv",
      "args": ["run", "--directory", "/absolute/path/to/ynab-mcp", "python", "-m", "ynab_mcp_server"],
      "env": {
        "YNAB_API_KEY": "your_ynab_api_key_here",
        "DEFAULT_BUDGET_ID": "optional_default_budget_id"
      }
    }
  }
}
```

To enable debug logging, add `"--logging"` to the args array:
```json
"args": ["ynab-mcp-server", "--logging"]
```

**Important**: 
- Replace `/path/to/uv` with the output of `which uv` on your system
- Replace `/absolute/path/to/ynab-mcp` with the actual absolute path to your project directory

#### Restart Claude Desktop

After updating the configuration, restart Claude Desktop. You should now see YNAB tools available in your conversations.

#### Test the Connection

Try asking Claude to help with your budget:

- "Show me my current budgets"
- "What's the balance in my checking account?"
- "Create a transaction for $25 coffee at Starbucks"
- "How much have I spent on groceries this month?"

### Using with Other MCP Clients

Once the server is running, you can connect to it using any MCP-compatible client. Here are some example tool calls:

```python
# Get all budgets
result = await client.call_tool("get_budgets", {"include_accounts": True})

# Get transactions for current month
result = await client.call_tool("get_transactions", {
    "budget_id": "default",
    "since_date": "2024-01-01"
})

# Create a new transaction
result = await client.call_tool("create_transaction", {
    "account_id": "account-uuid",
    "amount": -25000,  # $25.00 in milliunits
    "date": "2024-01-15",
    "payee_name": "Coffee Shop",
    "category_id": "category-uuid",
    "memo": "Morning coffee",
    "cleared": "cleared"
})

# Update category budget for current month
result = await client.call_tool("update_month_category", {
    "category_id": "category-uuid",
    "month": "2024-01-01",
    "budgeted": 500000  # $500.00 in milliunits
})
```

### Understanding Milliunits

YNAB uses milliunits for all monetary values:
- 1 dollar = 1000 milliunits
- $10.50 = 10500 milliunits
- -$25.00 = -25000 milliunits (negative for expenses)

## Development

### Running Tests
```bash
uv run pytest
```

### Linting and Formatting
```bash
# Format code
uv run black ynab_mcp_server/

# Lint code
uv run ruff ynab_mcp_server/

# Type checking
uv run mypy ynab_mcp_server/
```

### Adding New Tools

To add new tools, create or modify files in `ynab_mcp_server/tools/` and register them in `ynab_mcp_server/server.py`:

1. Create tool function with MCP decorator
2. Add comprehensive docstring
3. Handle errors appropriately
4. Register in the main server

## Architecture

```
ynab-mcp/
├── ynab_mcp_server/        # Main package
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # Module entry point
│   ├── server.py           # Main MCP server
│   ├── debug_utils.py      # Debug logging utilities
│   └── tools/              # Tool implementations
│       ├── budgets.py      # Budget-related tools
│       ├── accounts.py     # Account tools
│       ├── transactions.py # Transaction tools
│       ├── categories.py   # Category tools
│       ├── payees.py       # Payee tools
│       └── user.py         # User tools
├── pyproject.toml          # uv dependencies
├── uv.lock                 # Locked dependencies
├── claude_desktop_config.json # Sample Claude Desktop config
├── CLAUDE.md               # Development guide for Claude Code
└── .env.sample            # Environment template
```

## Debugging

### Debug Logging

The server supports debug logging to help troubleshoot MCP tool calls:

```bash
# Enable debug logging (if installed from PyPI)
ynab-mcp-server --logging

# Or using uvx
uvx ynab-mcp-server --logging

# Or from source
uv run python -m ynab_mcp_server --logging
```

When enabled, all tool calls are logged to stderr in the format:
```
TOOL_CALL: function_name(param1='value', param2=42)
```

This is especially useful when:
- Debugging Claude Desktop integration issues
- Understanding which tools are being called with what parameters
- Troubleshooting unexpected tool behavior

## Troubleshooting

### API Key Issues
- Ensure your API key is correctly set in the `.env` file
- Verify the key using the `verify_api_key` tool
- Check that the key has not expired in your YNAB settings


### Connection Issues
- Check network connectivity
- Ensure the YNAB API is accessible
- Verify Claude Desktop can find the `uv` command (use full path)

## Rate Limiting

The YNAB API has rate limits. This server handles rate limit responses appropriately, but be mindful of:
- Maximum of 200 requests per hour
- Rate limit resets on the hour
- Consider caching frequently accessed data

## Security

- Never commit your `.env` file with real API keys
- Store API keys securely in environment variables
- Rotate API keys regularly
- Use read-only keys when possible

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Check the [YNAB API documentation](https://api.ynab.com)
- Review [MCP documentation](https://modelcontextprotocol.io)
- Open an issue on GitHub

## Acknowledgments

- Built with the official [YNAB Python SDK](https://github.com/ynab/ynab-sdk-python)
- Powered by [Model Context Protocol](https://modelcontextprotocol.io)
- Fast dependency management with [uv](https://github.com/astral-sh/uv)