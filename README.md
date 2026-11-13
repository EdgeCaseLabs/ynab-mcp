# YNAB MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io) server for the
[YNAB](https://www.ynab.com) (You Need A Budget) API. It exposes budgets,
accounts, transactions, categories, and payees as MCP tools so Claude can read
and update your budget.

> **Reconciling Amazon purchases?** If you use this alongside the Amazon
> Transaction Scraper and the `amazon-ynab-correlator` skill, follow the
> end-to-end guide in the scraper's `SETUP.md` instead. It wires both MCP
> servers into Claude Desktop together.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Python 3.10+ (uv will install it if needed)
- A YNAB Personal Access Token from https://app.ynab.com/settings/developer

## Setup for Claude Desktop

1. Clone the repo and install dependencies:

   ```bash
   git clone https://github.com/EdgeCaseLabs/ynab-mcp.git
   cd ynab-mcp
   uv sync
   ```

2. Find your `uv` path. Claude Desktop does not inherit your shell `PATH`, so
   the config below needs the absolute path:

   ```bash
   which uv
   ```

3. Add the server to your Claude Desktop config:

   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

   ```json
   {
     "mcpServers": {
       "ynab": {
         "command": "/absolute/path/to/uv",
         "args": [
           "run",
           "--directory",
           "/absolute/path/to/ynab-mcp",
           "python",
           "-m",
           "ynab_mcp_server"
         ],
         "env": {
           "YNAB_API_KEY": "your_ynab_api_key_here",
           "DEFAULT_BUDGET_ID": ""
         }
       }
     }
   }
   ```

   Replace both absolute paths. A copy of this snippet lives in
   `claude_desktop_config.json`.

4. Restart Claude Desktop. The YNAB tools appear under the tools menu.

5. Try it:

   - "Show me my budgets"
   - "What's the balance in my checking account?"
   - "How much have I spent on groceries this month?"
   - "Create a $25 transaction at Starbucks in my checking account"

## Configuration

Set these in the `env` block of the Claude Desktop config. (A `.env` file in
the repo root also works; see `.env.sample`.)

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `YNAB_API_KEY` | Yes | YNAB Personal Access Token | - |
| `DEFAULT_BUDGET_ID` | No | Budget used when a tool call omits `budget_id` | `last-used` |
| `LOG_LEVEL` | No | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` |

## Claude Code

Same server, registered with the `claude mcp` CLI instead of the Desktop
config file:

```bash
claude mcp add ynab --scope user \
  -e YNAB_API_KEY=your_ynab_api_key_here \
  -e DEFAULT_BUDGET_ID= \
  -- /absolute/path/to/uv run --directory /absolute/path/to/ynab-mcp python -m ynab_mcp_server
```

Use `--scope project` instead to write a `.mcp.json` in the current repo.
Verify with `claude mcp list`.

## Available Tools

**User**: `get_user`, `verify_api_key`

**Budgets**: `get_budgets`, `get_budget_by_id`, `get_budget_settings`

**Accounts**: `get_accounts`, `get_account_by_id`, `get_account_balance`,
`create_account`

**Transactions**: `get_transactions`, `get_transaction_by_id`,
`create_transaction`, `update_transaction`, `delete_transaction`,
`import_transactions`

**Categories**: `get_categories`, `get_category_by_id`, `get_month_category`,
`get_category_balance`, `update_category`, `update_month_category`

**Payees**: `get_payees`, `get_payee_by_id`, `search_payees`, `update_payee`,
`get_payee_locations`, `get_payee_location_by_id`,
`get_payee_locations_by_payee`

Most tools accept an optional `budget_id`; when omitted, `DEFAULT_BUDGET_ID`
(or `last-used`) applies.

### Milliunits

YNAB expresses money in milliunits: `$1.00` = `1000`, `-$25.00` = `-25000`
(negative for outflows). Tools take and return milliunits.

## Troubleshooting

**Server does not appear in Claude Desktop**
- `command` must be the absolute path from `which uv`.
- `--directory` must be the absolute path to the cloned repo.
- Check Claude Desktop's MCP log:
  `~/Library/Logs/Claude/mcp-server-ynab.log` (macOS).

**Debug tool calls**
Add `"--logging"` to the end of the `args` array. Every tool call is then
logged to stderr as `TOOL_CALL: name(param=value, ...)`, which shows up in the
log file above.

**API key errors**
- Ask Claude to run `verify_api_key`.
- Confirm the token is still active at https://app.ynab.com/settings/developer.

**Rate limits**
YNAB allows 200 requests per hour per token, resetting on the hour.

## Development

```bash
uv run pytest                        # tests
uv run black ynab_mcp_server/        # format
uv run ruff ynab_mcp_server/         # lint
uv run mypy ynab_mcp_server/         # types
uv run python -m ynab_mcp_server     # run server directly (stdio)
```

Tools live in `ynab_mcp_server/tools/` and are registered in
`ynab_mcp_server/server.py`.

## Security

- Never commit a config or env file containing a real API key.
- Rotate your YNAB token if it leaks.

## License

MIT. See [LICENSE](LICENSE).
