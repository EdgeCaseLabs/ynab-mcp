"""
Payee-related MCP tools for YNAB
"""
import os
from typing import Optional, Any, Dict
from mcp.server.fastmcp import FastMCP
import ynab
from ynab.api import payees_api, payee_locations_api
from ynab.models import PatchPayeeWrapper, SavePayee
import logging

logger = logging.getLogger(__name__)

def register_tools(mcp: FastMCP, get_client_func):
    """Register payee-related tools with the MCP server"""
    
    def get_budget_id(budget_id: str) -> str:
        """Helper to resolve budget ID"""
        if budget_id == "default":
            default_budget = os.getenv("DEFAULT_BUDGET_ID")
            if default_budget:
                return default_budget
            return "last-used"
        return budget_id
    
    @mcp.tool()
    def get_payees(
        budget_id: str = "default",
        last_knowledge_of_server: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get all payees for a budget.
        
        Args:
            budget_id: Budget ID, 'last-used', or 'default'
            last_knowledge_of_server: The starting server knowledge for delta requests
            
        Returns:
            List of payees
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            with get_client_func() as api_client:
                api = payees_api.PayeesApi(api_client)
                response = api.get_payees(
                    budget_id=budget_id,
                    last_knowledge_of_server=last_knowledge_of_server
                )
                
                payees_list = []
                for payee in response.data.payees:
                    payees_list.append({
                        "id": payee.id,
                        "name": payee.name,
                        "transfer_account_id": payee.transfer_account_id,
                        "deleted": payee.deleted
                    })
                
                return {
                    "payees": payees_list,
                    "server_knowledge": response.data.server_knowledge
                }
        except Exception as e:
            logger.error(f"Error getting payees: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    def get_payee_by_id(
        payee_id: str,
        budget_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Get a specific payee by ID.
        
        Args:
            payee_id: The payee ID
            budget_id: Budget ID, 'last-used', or 'default'
            
        Returns:
            Payee details
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            with get_client_func() as api_client:
                api = payees_api.PayeesApi(api_client)
                response = api.get_payee_by_id(
                    budget_id=budget_id,
                    payee_id=payee_id
                )
                
                payee = response.data.payee
                return {
                    "id": payee.id,
                    "name": payee.name,
                    "transfer_account_id": payee.transfer_account_id,
                    "deleted": payee.deleted
                }
        except Exception as e:
            logger.error(f"Error getting payee {payee_id}: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    def update_payee(
        payee_id: str,
        name: str,
        budget_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Update a payee's name.
        
        Args:
            payee_id: The payee ID to update
            name: New name for the payee
            budget_id: Budget ID, 'last-used', or 'default'
            
        Returns:
            Updated payee details
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            with get_client_func() as api_client:
                api = payees_api.PayeesApi(api_client)
                
                payee_data = SavePayee(name=name)
                wrapper = PatchPayeeWrapper(payee=payee_data)
                
                response = api.update_payee(
                    budget_id=budget_id,
                    payee_id=payee_id,
                    data=wrapper
                )
                
                payee = response.data.payee
                return {
                    "id": payee.id,
                    "name": payee.name,
                    "transfer_account_id": payee.transfer_account_id,
                    "deleted": payee.deleted,
                    "message": "Payee updated successfully"
                }
        except Exception as e:
            logger.error(f"Error updating payee {payee_id}: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    def get_payee_locations(
        budget_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Get all payee locations for a budget.
        
        Args:
            budget_id: Budget ID, 'last-used', or 'default'
            
        Returns:
            List of payee locations
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            with get_client_func() as api_client:
                api = payee_locations_api.PayeeLocationsApi(api_client)
                response = api.get_payee_locations(budget_id=budget_id)
                
                locations_list = []
                for location in response.data.payee_locations:
                    locations_list.append({
                        "id": location.id,
                        "payee_id": location.payee_id,
                        "latitude": location.latitude,
                        "longitude": location.longitude,
                        "deleted": location.deleted
                    })
                
                return {"payee_locations": locations_list}
        except Exception as e:
            logger.error(f"Error getting payee locations: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    def get_payee_location_by_id(
        payee_location_id: str,
        budget_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Get a specific payee location by ID.
        
        Args:
            payee_location_id: The payee location ID
            budget_id: Budget ID, 'last-used', or 'default'
            
        Returns:
            Payee location details
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            with get_client_func() as api_client:
                api = payee_locations_api.PayeeLocationsApi(api_client)
                response = api.get_payee_location_by_id(
                    budget_id=budget_id,
                    payee_location_id=payee_location_id
                )
                
                location = response.data.payee_location
                return {
                    "id": location.id,
                    "payee_id": location.payee_id,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "deleted": location.deleted
                }
        except Exception as e:
            logger.error(f"Error getting payee location {payee_location_id}: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    def get_payee_locations_by_payee(
        payee_id: str,
        budget_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Get all locations for a specific payee.
        
        Args:
            payee_id: The payee ID
            budget_id: Budget ID, 'last-used', or 'default'
            
        Returns:
            List of locations for the payee
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            with get_client_func() as api_client:
                api = payee_locations_api.PayeeLocationsApi(api_client)
                response = api.get_payee_locations_by_payee(
                    budget_id=budget_id,
                    payee_id=payee_id
                )
                
                locations_list = []
                for location in response.data.payee_locations:
                    locations_list.append({
                        "id": location.id,
                        "payee_id": location.payee_id,
                        "latitude": location.latitude,
                        "longitude": location.longitude,
                        "deleted": location.deleted
                    })
                
                return {
                    "payee_id": payee_id,
                    "locations": locations_list
                }
        except Exception as e:
            logger.error(f"Error getting locations for payee {payee_id}: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    def search_payees(
        search_term: str,
        budget_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Search for payees by name.
        
        Args:
            search_term: The search term to match against payee names
            budget_id: Budget ID, 'last-used', or 'default'
            
        Returns:
            List of matching payees
        """
        try:
            budget_id = get_budget_id(budget_id)
            
            with get_client_func() as api_client:
                api = payees_api.PayeesApi(api_client)
                response = api.get_payees(budget_id=budget_id)
                
                # Filter payees by search term (case-insensitive)
                search_lower = search_term.lower()
                matching_payees = []
                
                for payee in response.data.payees:
                    if search_lower in payee.name.lower():
                        matching_payees.append({
                            "id": payee.id,
                            "name": payee.name,
                            "transfer_account_id": payee.transfer_account_id,
                            "deleted": payee.deleted
                        })
                
                return {
                    "search_term": search_term,
                    "matches": matching_payees,
                    "count": len(matching_payees)
                }
        except Exception as e:
            logger.error(f"Error searching payees: {e}")
            return {"error": str(e)}