"""
Budget-related MCP tools for YNAB
"""
import os
from typing import Optional, Any, Dict
from mcp.server.fastmcp import FastMCP
import ynab
from ynab.api import budgets_api
import logging

logger = logging.getLogger(__name__)

# Import the logging decorator
from ..debug_utils import log_tool_call

def register_tools(mcp: FastMCP, get_client_func):
    """Register budget-related tools with the MCP server"""
    
    @mcp.tool()
    @log_tool_call
    def get_budgets(include_accounts: bool = False) -> Dict[str, Any]:
        """
        Get list of budgets for the authenticated user.
        
        Args:
            include_accounts: Include account information in response
            
        Returns:
            List of budget summaries
        """
        try:
            with get_client_func() as api_client:
                api = budgets_api.BudgetsApi(api_client)
                response = api.get_budgets(include_accounts=include_accounts)
                
                budgets_list = []
                for budget in response.data.budgets:
                    budget_dict = {
                        "id": budget.id,
                        "name": budget.name,
                        "last_modified_on": budget.last_modified_on.isoformat() if budget.last_modified_on else None,
                        "date_format": budget.date_format.format if budget.date_format else None,
                        "currency_format": {
                            "iso_code": budget.currency_format.iso_code,
                            "example_format": budget.currency_format.example_format,
                            "decimal_digits": budget.currency_format.decimal_digits,
                            "decimal_separator": budget.currency_format.decimal_separator,
                            "symbol_first": budget.currency_format.symbol_first,
                            "group_separator": budget.currency_format.group_separator,
                            "currency_symbol": budget.currency_format.currency_symbol,
                            "display_symbol": budget.currency_format.display_symbol
                        } if budget.currency_format else None
                    }
                    
                    if include_accounts and budget.accounts:
                        budget_dict["accounts"] = [
                            {
                                "id": acc.id,
                                "name": acc.name,
                                "type": acc.type,
                                "on_budget": acc.on_budget,
                                "closed": acc.closed,
                                "balance": acc.balance,
                                "cleared_balance": acc.cleared_balance,
                                "uncleared_balance": acc.uncleared_balance
                            } for acc in budget.accounts
                        ]
                    
                    budgets_list.append(budget_dict)
                
                return {
                    "budgets": budgets_list,
                    "default_budget": response.data.default_budget.id if response.data.default_budget else None
                }
        except Exception as e:
            logger.error(f"Error getting budgets: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    @log_tool_call
    def get_budget_by_id(
        budget_id: str,
        last_knowledge_of_server: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific budget.
        
        Args:
            budget_id: The budget ID or 'last-used' for the last used budget
            last_knowledge_of_server: The starting server knowledge for delta requests
            
        Returns:
            Detailed budget information including accounts, categories, payees, etc.
        """
        try:
            # Use default budget if configured and no specific ID provided
            if budget_id == "default":
                default_budget = os.getenv("DEFAULT_BUDGET_ID")
                if default_budget:
                    budget_id = default_budget
                else:
                    budget_id = "last-used"
            
            with get_client_func() as api_client:
                api = budgets_api.BudgetsApi(api_client)
                response = api.get_budget_by_id(
                    budget_id=budget_id,
                    last_knowledge_of_server=last_knowledge_of_server
                )
                
                budget = response.data.budget
                budget_dict = {
                    "id": budget.id,
                    "name": budget.name,
                    "last_modified_on": budget.last_modified_on.isoformat() if budget.last_modified_on else None,
                    "server_knowledge": response.data.server_knowledge
                }
                
                # Include accounts
                if budget.accounts:
                    budget_dict["accounts"] = [
                        {
                            "id": acc.id,
                            "name": acc.name,
                            "type": acc.type,
                            "on_budget": acc.on_budget,
                            "closed": acc.closed,
                            "balance": acc.balance,
                            "cleared_balance": acc.cleared_balance,
                            "uncleared_balance": acc.uncleared_balance,
                            "transfer_payee_id": acc.transfer_payee_id,
                            "deleted": acc.deleted
                        } for acc in budget.accounts
                    ]
                
                # Include category groups with categories
                if budget.category_groups:
                    budget_dict["category_groups"] = [
                        {
                            "id": group.id,
                            "name": group.name,
                            "hidden": group.hidden,
                            "deleted": group.deleted,
                            "categories": [
                                {
                                    "id": cat.id,
                                    "name": cat.name,
                                    "hidden": cat.hidden,
                                    "note": cat.note,
                                    "budgeted": cat.budgeted,
                                    "activity": cat.activity,
                                    "balance": cat.balance,
                                    "deleted": cat.deleted
                                } for cat in (group.categories or [])
                            ]
                        } for group in budget.category_groups
                    ]
                
                # Include payees
                if budget.payees:
                    budget_dict["payees"] = [
                        {
                            "id": payee.id,
                            "name": payee.name,
                            "transfer_account_id": payee.transfer_account_id,
                            "deleted": payee.deleted
                        } for payee in budget.payees
                    ]
                
                # Include months
                if budget.months:
                    budget_dict["months"] = [
                        {
                            "month": month.month,
                            "income": month.income,
                            "budgeted": month.budgeted,
                            "activity": month.activity,
                            "to_be_budgeted": month.to_be_budgeted,
                            "deleted": month.deleted
                        } for month in budget.months
                    ]
                
                return budget_dict
        except Exception as e:
            logger.error(f"Error getting budget {budget_id}: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    @log_tool_call
    def get_budget_settings(budget_id: str) -> Dict[str, Any]:
        """
        Get settings for a specific budget.
        
        Args:
            budget_id: The budget ID or 'last-used' for the last used budget
            
        Returns:
            Budget settings including date format and currency format
        """
        try:
            if budget_id == "default":
                default_budget = os.getenv("DEFAULT_BUDGET_ID")
                if default_budget:
                    budget_id = default_budget
                else:
                    budget_id = "last-used"
            
            with get_client_func() as api_client:
                api = budgets_api.BudgetsApi(api_client)
                response = api.get_budget_settings_by_id(budget_id=budget_id)
                
                settings = response.data.settings
                return {
                    "date_format": {
                        "format": settings.date_format.format
                    } if settings.date_format else None,
                    "currency_format": {
                        "iso_code": settings.currency_format.iso_code,
                        "example_format": settings.currency_format.example_format,
                        "decimal_digits": settings.currency_format.decimal_digits,
                        "decimal_separator": settings.currency_format.decimal_separator,
                        "symbol_first": settings.currency_format.symbol_first,
                        "group_separator": settings.currency_format.group_separator,
                        "currency_symbol": settings.currency_format.currency_symbol,
                        "display_symbol": settings.currency_format.display_symbol
                    } if settings.currency_format else None
                }
        except Exception as e:
            logger.error(f"Error getting budget settings for {budget_id}: {e}")
            return {"error": str(e)}