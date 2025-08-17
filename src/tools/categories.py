"""
Category-related MCP tools for YNAB
"""
import os
from typing import Optional, Any, Dict
from mcp.server.fastmcp import FastMCP
import ynab
from ynab.api import categories_api
from ynab.models import PatchCategoryWrapper, SaveCategory, PatchMonthCategoryWrapper, SaveMonthCategory
import logging

logger = logging.getLogger(__name__)

# Import the logging decorator
from debug_utils import log_tool_call

def register_tools(mcp: FastMCP, get_client_func):
    """Register category-related tools with the MCP server"""
    
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
    def get_categories(
        budget_id: str = "default",
        last_knowledge_of_server: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get all categories grouped by category group.
        
        Args:
            budget_id: Budget ID, 'last-used', or 'default'
            last_knowledge_of_server: The starting server knowledge for delta requests
            
        Returns:
            Category groups with their categories
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            with get_client_func() as api_client:
                api = categories_api.CategoriesApi(api_client)
                response = api.get_categories(
                    budget_id=budget_id,
                    last_knowledge_of_server=last_knowledge_of_server
                )
                
                category_groups = []
                for group in response.data.category_groups:
                    group_dict = {
                        "id": group.id,
                        "name": group.name,
                        "hidden": group.hidden,
                        "deleted": group.deleted,
                        "categories": []
                    }
                    
                    if group.categories:
                        for cat in group.categories:
                            group_dict["categories"].append({
                                "id": cat.id,
                                "name": cat.name,
                                "hidden": cat.hidden,
                                "note": cat.note,
                                "budgeted": cat.budgeted,
                                "budgeted_formatted": f"${cat.budgeted / 1000:.2f}",
                                "activity": cat.activity,
                                "activity_formatted": f"${cat.activity / 1000:.2f}",
                                "balance": cat.balance,
                                "balance_formatted": f"${cat.balance / 1000:.2f}",
                                "goal_type": cat.goal_type,
                                "goal_creation_month": cat.goal_creation_month,
                                "goal_target": cat.goal_target,
                                "goal_target_month": cat.goal_target_month,
                                "goal_percentage_complete": cat.goal_percentage_complete,
                                "deleted": cat.deleted
                            })
                    
                    category_groups.append(group_dict)
                
                return {
                    "category_groups": category_groups,
                    "server_knowledge": response.data.server_knowledge
                }
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    @log_tool_call
    def get_category_by_id(
        category_id: str,
        budget_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Get a specific category by ID.
        
        Args:
            category_id: The category ID
            budget_id: Budget ID, 'last-used', or 'default'
            
        Returns:
            Category details
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            with get_client_func() as api_client:
                api = categories_api.CategoriesApi(api_client)
                response = api.get_category_by_id(
                    budget_id=budget_id,
                    category_id=category_id
                )
                
                cat = response.data.category
                return {
                    "id": cat.id,
                    "category_group_id": cat.category_group_id,
                    "category_group_name": cat.category_group_name,
                    "name": cat.name,
                    "hidden": cat.hidden,
                    "note": cat.note,
                    "budgeted": cat.budgeted,
                    "budgeted_formatted": f"${cat.budgeted / 1000:.2f}",
                    "activity": cat.activity,
                    "activity_formatted": f"${cat.activity / 1000:.2f}",
                    "balance": cat.balance,
                    "balance_formatted": f"${cat.balance / 1000:.2f}",
                    "goal_type": cat.goal_type,
                    "goal_creation_month": cat.goal_creation_month,
                    "goal_target": cat.goal_target,
                    "goal_target_month": cat.goal_target_month,
                    "goal_percentage_complete": cat.goal_percentage_complete,
                    "deleted": cat.deleted
                }
        except Exception as e:
            logger.error(f"Error getting category {category_id}: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    @log_tool_call
    def get_month_category(
        category_id: str,
        month: str,
        budget_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Get a category for a specific month.
        
        Args:
            category_id: The category ID
            month: The month (ISO format: YYYY-MM-01)
            budget_id: Budget ID, 'last-used', or 'default'
            
        Returns:
            Category details for the specified month
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            with get_client_func() as api_client:
                api = categories_api.CategoriesApi(api_client)
                response = api.get_month_category_by_id(
                    budget_id=budget_id,
                    month=month,
                    category_id=category_id
                )
                
                cat = response.data.category
                return {
                    "id": cat.id,
                    "category_group_id": cat.category_group_id,
                    "category_group_name": cat.category_group_name,
                    "name": cat.name,
                    "hidden": cat.hidden,
                    "note": cat.note,
                    "budgeted": cat.budgeted,
                    "budgeted_formatted": f"${cat.budgeted / 1000:.2f}",
                    "activity": cat.activity,
                    "activity_formatted": f"${cat.activity / 1000:.2f}",
                    "balance": cat.balance,
                    "balance_formatted": f"${cat.balance / 1000:.2f}",
                    "goal_type": cat.goal_type,
                    "goal_target": cat.goal_target,
                    "goal_target_month": cat.goal_target_month,
                    "goal_percentage_complete": cat.goal_percentage_complete,
                    "deleted": cat.deleted
                }
        except Exception as e:
            logger.error(f"Error getting month category {category_id} for {month}: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    @log_tool_call
    def update_category(
        category_id: str,
        name: Optional[str] = None,
        note: Optional[str] = None,
        hidden: Optional[bool] = None,
        budget_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Update a category.
        
        Args:
            category_id: The category ID to update
            name: New category name
            note: New note for the category
            hidden: Whether the category is hidden
            budget_id: Budget ID, 'last-used', or 'default'
            
        Returns:
            Updated category details
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            with get_client_func() as api_client:
                api = categories_api.CategoriesApi(api_client)
                
                # Create update data
                update_data = {}
                if name is not None:
                    update_data["name"] = name
                if note is not None:
                    update_data["note"] = note
                if hidden is not None:
                    update_data["hidden"] = hidden
                
                category_data = SaveCategory(**update_data)
                wrapper = PatchCategoryWrapper(category=category_data)
                
                response = api.update_category(
                    budget_id=budget_id,
                    category_id=category_id,
                    data=wrapper
                )
                
                cat = response.data.category
                return {
                    "id": cat.id,
                    "name": cat.name,
                    "hidden": cat.hidden,
                    "note": cat.note,
                    "budgeted": cat.budgeted,
                    "budgeted_formatted": f"${cat.budgeted / 1000:.2f}",
                    "activity": cat.activity,
                    "activity_formatted": f"${cat.activity / 1000:.2f}",
                    "balance": cat.balance,
                    "balance_formatted": f"${cat.balance / 1000:.2f}",
                    "message": "Category updated successfully"
                }
        except Exception as e:
            logger.error(f"Error updating category {category_id}: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    @log_tool_call
    def update_month_category(
        category_id: str,
        month: str,
        budgeted: int,
        budget_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Update a category's budgeted amount for a specific month.
        
        Args:
            category_id: The category ID to update
            month: The month to update (ISO format: YYYY-MM-01)
            budgeted: The budgeted amount in milliunits (e.g., $100.50 = 100500)
            budget_id: Budget ID, 'last-used', or 'default'
            
        Returns:
            Updated category details for the month
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            with get_client_func() as api_client:
                api = categories_api.CategoriesApi(api_client)
                
                category_data = SaveMonthCategory(budgeted=budgeted)
                wrapper = PatchMonthCategoryWrapper(category=category_data)
                
                response = api.update_month_category(
                    budget_id=budget_id,
                    month=month,
                    category_id=category_id,
                    data=wrapper
                )
                
                cat = response.data.category
                return {
                    "id": cat.id,
                    "name": cat.name,
                    "month": month,
                    "budgeted": cat.budgeted,
                    "budgeted_formatted": f"${cat.budgeted / 1000:.2f}",
                    "activity": cat.activity,
                    "activity_formatted": f"${cat.activity / 1000:.2f}",
                    "balance": cat.balance,
                    "balance_formatted": f"${cat.balance / 1000:.2f}",
                    "message": f"Category budget updated for {month}"
                }
        except Exception as e:
            logger.error(f"Error updating month category {category_id} for {month}: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    @log_tool_call
    def get_category_balance(
        category_id: str,
        month: Optional[str] = None,
        budget_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Get the balance for a category.
        
        Args:
            category_id: The category ID
            month: Optional month (ISO format: YYYY-MM-01), defaults to current
            budget_id: Budget ID, 'last-used', or 'default'
            
        Returns:
            Category balance information
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            with get_client_func() as api_client:
                api = categories_api.CategoriesApi(api_client)
                
                if month:
                    response = api.get_month_category_by_id(
                        budget_id=budget_id,
                        month=month,
                        category_id=category_id
                    )
                else:
                    response = api.get_category_by_id(
                        budget_id=budget_id,
                        category_id=category_id
                    )
                
                cat = response.data.category
                return {
                    "category_name": cat.name,
                    "month": month if month else "current",
                    "budgeted": cat.budgeted,
                    "budgeted_formatted": f"${cat.budgeted / 1000:.2f}",
                    "activity": cat.activity,
                    "activity_formatted": f"${cat.activity / 1000:.2f}",
                    "balance": cat.balance,
                    "balance_formatted": f"${cat.balance / 1000:.2f}",
                    "available": cat.balance,
                    "available_formatted": f"${cat.balance / 1000:.2f}"
                }
        except Exception as e:
            logger.error(f"Error getting category balance for {category_id}: {e}")
            return {"error": str(e)}