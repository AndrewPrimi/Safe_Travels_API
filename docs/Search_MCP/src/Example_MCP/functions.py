"""Example functions that will be called by MCP tools.

This file contains the actual implementation of your MCP server's functionality.
Keep your business logic separate from the server definition for better organization.
"""

import httpx
from typing import Dict, Any
from .config import BASE_URL, ExampleMCPSettings


async def simple_search(query: str, api_key: str) -> Dict[str, Any]:
    """
    A simple example function that performs a search.
    
    This is where you implement the actual logic of your MCP tool.
    
    Args:
        query: The search query from the user
        api_key: API key for authentication
        
    Returns:
        Dictionary containing search results
    """
    # Example using httpx to make an API call
    async with httpx.AsyncClient() as client:
        try:
            # Build the request
            response = await client.get(
                f"{BASE_URL}/search",
                params={"q": query},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30.0
            )
            response.raise_for_status()
            
            # Return the JSON response
            return response.json()
            
        except httpx.HTTPError as e:
            # Handle errors gracefully
            return {
                "error": f"Search failed: {str(e)}",
                "status": "error"
            }


