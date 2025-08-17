"""
Transaction-related MCP tools for YNAB
"""
import os
from typing import Optional, Any, Dict, List
from datetime import date, datetime
from mcp.server.fastmcp import FastMCP
import ynab
from ynab.api import transactions_api
from ynab.models import (
    PostTransactionsWrapper, 
    SaveTransactionWithOptionalFields,
    PutTransactionWrapper,
    PatchTransactionsWrapper
)
import logging

logger = logging.getLogger(__name__)

# Import the logging decorator
from debug_utils import log_tool_call

def register_tools(mcp: FastMCP, get_client_func):
    """Register transaction-related tools with the MCP server"""
    
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
    def get_transactions(
        budget_id: str = "default",
        since_date: Optional[str] = None,
        type: Optional[str] = None,
        last_knowledge_of_server: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get transactions for a budget.
        
        Args:
            budget_id: Budget ID, 'last-used', or 'default'
            since_date: Filter transactions on or after this date (ISO format: YYYY-MM-DD)
            type: Filter by type: 'uncategorized' or 'unapproved'
            last_knowledge_of_server: The starting server knowledge for delta requests
            
        Returns:
            List of transactions
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            with get_client_func() as api_client:
                api = transactions_api.TransactionsApi(api_client)
                response = api.get_transactions(
                    budget_id=budget_id,
                    since_date=since_date,
                    type=type,
                    last_knowledge_of_server=last_knowledge_of_server
                )
                
                transactions_list = []
                for trans in response.data.transactions:
                    transactions_list.append({
                        "id": trans.id,
                        "date": trans.var_date.isoformat() if trans.var_date else None,
                        "amount": trans.amount,
                        "amount_formatted": f"${trans.amount / 1000:.2f}",
                        "memo": trans.memo,
                        "cleared": trans.cleared,
                        "approved": trans.approved,
                        "flag_color": trans.flag_color,
                        "account_id": trans.account_id,
                        "account_name": trans.account_name,
                        "payee_id": trans.payee_id,
                        "payee_name": trans.payee_name,
                        "category_id": trans.category_id,
                        "category_name": trans.category_name,
                        "transfer_account_id": trans.transfer_account_id,
                        "import_id": trans.import_id,
                        "deleted": trans.deleted,
                        "subtransactions": trans.subtransactions
                    })
                
                return {
                    "transactions": transactions_list,
                    "server_knowledge": response.data.server_knowledge
                }
        except Exception as e:
            logger.error(f"Error getting transactions: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    @log_tool_call
    def get_transaction_by_id(
        transaction_id: str,
        budget_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Get a single transaction by ID.
        
        Args:
            transaction_id: The transaction ID
            budget_id: Budget ID, 'last-used', or 'default'
            
        Returns:
            Transaction details
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            with get_client_func() as api_client:
                api = transactions_api.TransactionsApi(api_client)
                response = api.get_transaction_by_id(
                    budget_id=budget_id,
                    transaction_id=transaction_id
                )
                
                trans = response.data.transaction
                return {
                    "id": trans.id,
                    "date": trans.var_date.isoformat() if trans.var_date else None,
                    "amount": trans.amount,
                    "amount_formatted": f"${trans.amount / 1000:.2f}",
                    "memo": trans.memo,
                    "cleared": trans.cleared,
                    "approved": trans.approved,
                    "flag_color": trans.flag_color,
                    "account_id": trans.account_id,
                    "account_name": trans.account_name,
                    "payee_id": trans.payee_id,
                    "payee_name": trans.payee_name,
                    "category_id": trans.category_id,
                    "category_name": trans.category_name,
                    "transfer_account_id": trans.transfer_account_id,
                    "import_id": trans.import_id,
                    "deleted": trans.deleted,
                    "subtransactions": trans.subtransactions
                }
        except Exception as e:
            logger.error(f"Error getting transaction {transaction_id}: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    @log_tool_call
    def create_transaction(
        account_id: str,
        amount: int,
        date: str,
        payee_name: Optional[str] = None,
        payee_id: Optional[str] = None,
        category_id: Optional[str] = None,
        cleared: str = "uncleared",
        approved: bool = False,
        memo: Optional[str] = None,
        flag_color: Optional[str] = None,
        budget_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Create a new transaction.
        
        Args:
            account_id: Account ID for the transaction
            amount: Transaction amount in milliunits (e.g., -$10.50 = -10500)
            date: Transaction date (ISO format: YYYY-MM-DD)
            payee_name: Payee name (creates new payee if doesn't exist)
            payee_id: Existing payee ID (use instead of payee_name)
            category_id: Category ID
            cleared: Status: 'cleared', 'uncleared', or 'reconciled'
            approved: Whether transaction is approved
            memo: Transaction memo
            flag_color: Flag color: 'red', 'orange', 'yellow', 'green', 'blue', 'purple'
            budget_id: Budget ID, 'last-used', or 'default'
            
        Returns:
            Created transaction details
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            # Validate cleared status
            if cleared not in ["cleared", "uncleared", "reconciled"]:
                return {"error": "cleared must be 'cleared', 'uncleared', or 'reconciled'"}
            
            # Validate flag color if provided
            valid_flags = ["red", "orange", "yellow", "green", "blue", "purple"]
            if flag_color and flag_color not in valid_flags:
                return {"error": f"flag_color must be one of: {', '.join(valid_flags)}"}
            
            with get_client_func() as api_client:
                api = transactions_api.TransactionsApi(api_client)
                
                # Create transaction data
                transaction_data = SaveTransactionWithOptionalFields(
                    account_id=account_id,
                    amount=amount,
                    date=date,
                    payee_name=payee_name,
                    payee_id=payee_id,
                    category_id=category_id,
                    cleared=cleared,
                    approved=approved,
                    memo=memo,
                    flag_color=flag_color
                )
                
                wrapper = PostTransactionsWrapper(transaction=transaction_data)
                
                response = api.create_transaction(
                    budget_id=budget_id,
                    data=wrapper
                )
                
                if response.data.transaction:
                    trans = response.data.transaction
                    return {
                        "id": trans.id,
                        "date": trans.var_date.isoformat() if trans.var_date else None,
                        "amount": trans.amount,
                        "amount_formatted": f"${trans.amount / 1000:.2f}",
                        "payee_name": trans.payee_name,
                        "category_name": trans.category_name,
                        "memo": trans.memo,
                        "cleared": trans.cleared,
                        "approved": trans.approved,
                        "message": "Transaction created successfully"
                    }
                else:
                    return {"message": "Transaction created", "duplicate_import_ids": response.data.duplicate_import_ids}
        except Exception as e:
            logger.error(f"Error creating transaction: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    @log_tool_call
    def update_transaction(
        transaction_id: str,
        account_id: Optional[str] = None,
        amount: Optional[int] = None,
        date: Optional[str] = None,
        payee_name: Optional[str] = None,
        payee_id: Optional[str] = None,
        category_id: Optional[str] = None,
        cleared: Optional[str] = None,
        approved: Optional[bool] = None,
        memo: Optional[str] = None,
        flag_color: Optional[str] = None,
        budget_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Update an existing transaction.
        
        Args:
            transaction_id: The transaction ID to update
            account_id: New account ID
            amount: New amount in milliunits
            date: New date (ISO format: YYYY-MM-DD)
            payee_name: New payee name
            payee_id: New payee ID
            category_id: New category ID
            cleared: New status: 'cleared', 'uncleared', or 'reconciled'
            approved: New approved status
            memo: New memo
            flag_color: New flag color
            budget_id: Budget ID, 'last-used', or 'default'
            
        Returns:
            Updated transaction details
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            with get_client_func() as api_client:
                api = transactions_api.TransactionsApi(api_client)
                
                # Create update data with only provided fields
                update_data = {}
                if account_id is not None:
                    update_data["account_id"] = account_id
                if amount is not None:
                    update_data["amount"] = amount
                if date is not None:
                    update_data["date"] = date
                if payee_name is not None:
                    update_data["payee_name"] = payee_name
                if payee_id is not None:
                    update_data["payee_id"] = payee_id
                if category_id is not None:
                    update_data["category_id"] = category_id
                if cleared is not None:
                    update_data["cleared"] = cleared
                if approved is not None:
                    update_data["approved"] = approved
                if memo is not None:
                    update_data["memo"] = memo
                if flag_color is not None:
                    update_data["flag_color"] = flag_color
                
                transaction_data = SaveTransactionWithOptionalFields(**update_data)
                wrapper = PutTransactionWrapper(transaction=transaction_data)
                
                response = api.update_transaction(
                    budget_id=budget_id,
                    transaction_id=transaction_id,
                    data=wrapper
                )
                
                trans = response.data.transaction
                return {
                    "id": trans.id,
                    "date": trans.var_date.isoformat() if trans.var_date else None,
                    "amount": trans.amount,
                    "amount_formatted": f"${trans.amount / 1000:.2f}",
                    "payee_name": trans.payee_name,
                    "category_name": trans.category_name,
                    "memo": trans.memo,
                    "cleared": trans.cleared,
                    "approved": trans.approved,
                    "message": "Transaction updated successfully"
                }
        except Exception as e:
            logger.error(f"Error updating transaction {transaction_id}: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    @log_tool_call
    def delete_transaction(
        transaction_id: str,
        budget_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Delete a transaction.
        
        Args:
            transaction_id: The transaction ID to delete
            budget_id: Budget ID, 'last-used', or 'default'
            
        Returns:
            Deletion confirmation
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            with get_client_func() as api_client:
                api = transactions_api.TransactionsApi(api_client)
                response = api.delete_transaction(
                    budget_id=budget_id,
                    transaction_id=transaction_id
                )
                
                trans = response.data.transaction
                return {
                    "id": trans.id,
                    "deleted": True,
                    "message": f"Transaction {trans.id} deleted successfully"
                }
        except Exception as e:
            logger.error(f"Error deleting transaction {transaction_id}: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    @log_tool_call
    def import_transactions(
        budget_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Import transactions from linked accounts.
        
        Args:
            budget_id: Budget ID, 'last-used', or 'default'
            
        Returns:
            Import results including number of imported transactions
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            with get_client_func() as api_client:
                api = transactions_api.TransactionsApi(api_client)
                response = api.import_transactions(budget_id=budget_id)
                
                return {
                    "transaction_ids": response.data.transaction_ids,
                    "count": len(response.data.transaction_ids) if response.data.transaction_ids else 0,
                    "message": f"Imported {len(response.data.transaction_ids) if response.data.transaction_ids else 0} transactions"
                }
        except Exception as e:
            logger.error(f"Error importing transactions: {e}")
            return {"error": str(e)}