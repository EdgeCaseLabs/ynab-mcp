"""
Account-related MCP tools for YNAB
"""
import os
from typing import Optional, Any, Dict
from mcp.server.fastmcp import FastMCP
import ynab
from ynab.api import accounts_api
from ynab.models import PostAccountWrapper, SaveAccount
import logging

logger = logging.getLogger(__name__)

# Import the logging decorator
from ..debug_utils import log_tool_call


def register_tools(mcp: FastMCP, get_client_func):
    """Register account-related tools with the MCP server"""
    
    def get_budget_id(budget_id: str) -> str:
        """Helper to resolve budget ID"""
        if budget_id == "default":
            default_budget = os.getenv("DEFAULT_BUDGET_ID")
            if default_budget:
                return default_budget
            return "last-used"
        return budget_id
    
    @mcp.tool()
    @log_tool_call
    def get_accounts(
        budget_id: str = "default",
        last_knowledge_of_server: Optional[int] = None,
        include_closed: bool = False,
        include_deleted: bool = False
    ) -> Dict[str, Any]:
        """
        Get accounts for a budget with optional filtering.
        
        Args:
            budget_id: Budget ID, 'last-used', or 'default' (uses DEFAULT_BUDGET_ID env var)
            last_knowledge_of_server: The starting server knowledge for delta requests
            include_closed: Whether to include closed accounts (default: False)
            include_deleted: Whether to include deleted accounts (default: False)
            
        Returns:
            List of accounts with their details, filtered by the specified criteria
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            with get_client_func() as api_client:
                api = accounts_api.AccountsApi(api_client)
                response = api.get_accounts(
                    budget_id=budget_id,
                    last_knowledge_of_server=last_knowledge_of_server
                )
                
                accounts_list = []
                for account in response.data.accounts:
                    # Filter out closed accounts unless explicitly requested
                    if account.closed and not include_closed:
                        continue
                    
                    # Filter out deleted accounts unless explicitly requested
                    if account.deleted and not include_deleted:
                        continue
                    
                    accounts_list.append({
                        "id": account.id,
                        "name": account.name,
                        "type": account.type,
                        "on_budget": account.on_budget,
                        "closed": account.closed,
                        "note": account.note,
                        "balance": account.balance,
                        "cleared_balance": account.cleared_balance,
                        "uncleared_balance": account.uncleared_balance,
                        "transfer_payee_id": account.transfer_payee_id,
                        "direct_import_linked": account.direct_import_linked,
                        "direct_import_in_error": account.direct_import_in_error,
                        "deleted": account.deleted
                    })
                
                return {
                    "accounts": accounts_list,
                    "server_knowledge": response.data.server_knowledge
                }
        except Exception as e:
            logger.exception(f"Error getting accounts: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    @log_tool_call
    def get_account_by_id(
        account_id: str,
        budget_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Get details for a specific account.
        
        Args:
            account_id: The account ID
            budget_id: Budget ID, 'last-used', or 'default'
            
        Returns:
            Account details
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            with get_client_func() as api_client:
                api = accounts_api.AccountsApi(api_client)
                response = api.get_account_by_id(
                    budget_id=budget_id,
                    account_id=account_id
                )
                
                account = response.data.account
                return {
                    "id": account.id,
                    "name": account.name,
                    "type": account.type,
                    "on_budget": account.on_budget,
                    "closed": account.closed,
                    "note": account.note,
                    "balance": account.balance,
                    "cleared_balance": account.cleared_balance,
                    "uncleared_balance": account.uncleared_balance,
                    "transfer_payee_id": account.transfer_payee_id,
                    "direct_import_linked": account.direct_import_linked,
                    "direct_import_in_error": account.direct_import_in_error,
                    "deleted": account.deleted
                }
        except Exception as e:
            logger.exception(f"Error getting account {account_id}: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    @log_tool_call
    def create_account(
        name: str,
        type: str,
        balance: int,
        budget_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Create a new account in a budget.
        
        Args:
            name: Account name
            type: Account type (checking, savings, creditCard, cash, lineOfCredit, 
                  otherAsset, otherLiability, payPal, merchantAccount, investmentAccount, mortgage)
            balance: Initial account balance in milliunits (e.g., $10.50 = 10500)
            budget_id: Budget ID, 'last-used', or 'default'
            
        Returns:
            Created account details
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            # Validate account type
            valid_types = [
                "checking", "savings", "creditCard", "cash", "lineOfCredit",
                "otherAsset", "otherLiability", "payPal", "merchantAccount",
                "investmentAccount", "mortgage"
            ]
            if type not in valid_types:
                return {
                    "error": f"Invalid account type. Must be one of: {', '.join(valid_types)}"
                }
            
            with get_client_func() as api_client:
                api = accounts_api.AccountsApi(api_client)
                
                # Create account data
                account_data = SaveAccount(
                    name=name,
                    type=type,
                    balance=balance
                )
                
                wrapper = PostAccountWrapper(account=account_data)
                
                response = api.create_account(
                    budget_id=budget_id,
                    data=wrapper
                )
                
                account = response.data.account
                return {
                    "id": account.id,
                    "name": account.name,
                    "type": account.type,
                    "on_budget": account.on_budget,
                    "closed": account.closed,
                    "balance": account.balance,
                    "cleared_balance": account.cleared_balance,
                    "uncleared_balance": account.uncleared_balance,
                    "transfer_payee_id": account.transfer_payee_id,
                    "message": "Account created successfully"
                }
        except Exception as e:
            logger.exception(f"Error creating account: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    @log_tool_call
    def get_account_balance(
        account_id: str,
        budget_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Get balance information for a specific account.
        
        Args:
            account_id: The account ID
            budget_id: Budget ID, 'last-used', or 'default'
            
        Returns:
            Account balance details in milliunits
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            with get_client_func() as api_client:
                api = accounts_api.AccountsApi(api_client)
                response = api.get_account_by_id(
                    budget_id=budget_id,
                    account_id=account_id
                )
                
                account = response.data.account
                return {
                    "account_name": account.name,
                    "balance": account.balance,
                    "cleared_balance": account.cleared_balance,
                    "uncleared_balance": account.uncleared_balance,
                    "balance_formatted": f"${account.balance / 1000:.2f}",
                    "cleared_balance_formatted": f"${account.cleared_balance / 1000:.2f}",
                    "uncleared_balance_formatted": f"${account.uncleared_balance / 1000:.2f}"
                }
        except Exception as e:
            logger.exception(f"Error getting account balance for {account_id}: {e}")
            return {"error": str(e)}