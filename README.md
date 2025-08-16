# YNAB MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to the YNAB (You Need A Budget) API. This server exposes all YNAB API functionality as MCP tools, allowing AI assistants and other MCP clients to interact with YNAB budgets, accounts, transactions, and more.

## Features

- **Complete YNAB API Coverage**: All YNAB API methods are exposed as MCP tools
- **Docker Support**: Easy deployment using Docker and Docker Compose
- **Type-Safe**: Built with Python type hints and Pydantic models
- **Error Handling**: Comprehensive error handling and logging
- **Environment Configuration**: Simple configuration via environment variables
- **Organized Tool Structure**: Tools are logically grouped by category (budgets, accounts, transactions, etc.)

## Prerequisites

- Docker and Docker Compose (for containerized deployment)
- OR Python 3.10+ with Poetry (for local development)
- A YNAB account with a Personal Access Token

## Getting Your YNAB API Key

1. Log in to your YNAB account at https://app.ynab.com
2. Navigate to Account Settings
3. Go to the Developer Settings section
4. Create a new Personal Access Token
5. Save this token securely - you'll need it for configuration

## Installation

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ynab-mcp.git
cd ynab-mcp
```

2. Copy the environment template:
```bash
cp .env.sample .env
```

3. Edit `.env` and add your YNAB API key:
```env
YNAB_API_KEY=your_actual_api_key_here
```

4. Build and run with Docker Compose:
```bash
docker compose up --build
```

### Local Development Setup

1. Install Poetry if you haven't already:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

3. Copy and configure environment:
```bash
cp .env.sample .env
# Edit .env with your API key
```

4. Run the server:
```bash
poetry run python -m mcp run src/server.py
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
- `get_accounts(budget_id, last_knowledge_of_server)` - Get all accounts
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

### Using with MCP Client

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

## Docker Commands

### Build the image
```bash
docker build -t ynab-mcp:latest .
```

### Run with Docker Compose
```bash
# Start the service
docker compose up -d

# View logs
docker compose logs -f

# Stop the service
docker compose down
```

### Run standalone container
```bash
docker run --env-file .env ynab-mcp:latest
```

## Development

### Running Tests
```bash
poetry run pytest
```

### Linting and Formatting
```bash
# Format code
poetry run black src/

# Lint code
poetry run ruff src/

# Type checking
poetry run mypy src/
```

### Adding New Tools

To add new tools, create or modify files in `src/tools/` and register them in `src/server.py`:

1. Create tool function with MCP decorator
2. Add comprehensive docstring
3. Handle errors appropriately
4. Register in the main server

## Architecture

```
ynab-mcp/
├── src/
│   ├── server.py           # Main MCP server
│   └── tools/              # Tool implementations
│       ├── budgets.py      # Budget-related tools
│       ├── accounts.py     # Account tools
│       ├── transactions.py # Transaction tools
│       ├── categories.py   # Category tools
│       ├── payees.py       # Payee tools
│       └── user.py         # User tools
├── Dockerfile              # Docker image definition
├── compose.yml            # Docker Compose configuration
├── pyproject.toml         # Poetry dependencies
└── .env.sample            # Environment template
```

## Troubleshooting

### API Key Issues
- Ensure your API key is correctly set in the `.env` file
- Verify the key using the `verify_api_key` tool
- Check that the key has not expired in your YNAB settings

### Docker Issues
- Ensure Docker daemon is running
- Check container logs: `docker compose logs`
- Verify environment variables are loaded: `docker compose config`

### Connection Issues
- Check network connectivity
- Verify firewall settings if using HTTP transport
- Ensure the YNAB API is accessible

## Rate Limiting

The YNAB API has rate limits. This server handles rate limit responses appropriately, but be mindful of:
- Maximum of 200 requests per hour
- Rate limit resets on the hour
- Consider caching frequently accessed data

## Security

- Never commit your `.env` file with real API keys
- Use Docker secrets in production environments
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
- Containerized with Docker for easy deployment