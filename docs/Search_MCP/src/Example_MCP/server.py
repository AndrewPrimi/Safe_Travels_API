"""Example MCP Server implementation using FastMCP framework."""

import os
import sys
import httpx
import logging
import asyncio
from typing import Optional
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

# Import your configuration and implementation functions
from .config import ExampleMCPSettings
from .functions import simple_search

# Configure logging - this helps with debugging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True
)

logger = logging.getLogger("example-mcp")

# Global httpx client - reused across requests for better performance
http_client: Optional[httpx.AsyncClient] = None

# Load settings from environment variables
settings = ExampleMCPSettings()

@asynccontextmanager
async def lifespan(mcp: FastMCP):
    """
    Manages the lifecycle of the MCP server.
    
    This function runs when the server starts up and shuts down.
    Use it to initialize resources (like HTTP clients) and clean them up.
    """
    global http_client
    
    # Startup: Initialize resources
    logger.info("Example MCP server starting up...")
    http_client = httpx.AsyncClient(timeout=30.0)
    logger.info("HTTP client initialized")
    
    yield  # Server runs while this yields
    
    # Shutdown: Clean up resources
    logger.info("Example MCP server shutting down...")
    if http_client and not http_client.is_closed:
        await http_client.aclose()
        http_client = None
    logger.info("Cleanup complete")

# Initialize your MCP server with FastMCP
mcp = FastMCP(
    name="example-mcp",  # Name shown to AI models
    instructions="This is an example MCP server that demonstrates basic functionality",  # What this server does
    dependencies=["httpx>=0.27.0", "pydantic-settings>=2.0.0"],  # Python packages needed
    lifespan=lifespan  # Lifecycle manager defined above
)

# Define your first tool using the @mcp.tool decorator
@mcp.tool(
    description="Search for information using an example API"  # This description is shown to the AI
)
async def search(query: str) -> str:
    """
    Perform a search using the example API.
    
    This docstring is ALSO for the AI to see.
    The 'description' parameter above is what the AI sees.
    
    Args:
        query: The search term or question
        
    Returns:
        Search results as a formatted string
    """
    # Check if http client is available
    if not http_client:
        logger.error("HTTP client not initialized")
        return "Error: Server not properly initialized"
    
    try:
        # Call your implementation function
        results = await simple_search(query, settings.EXAMPLE_API_KEY)
        
        # Format the results for display
        if "error" in results:
            return f"Search failed: {results['error']}"
        
        # Simple formatting - customize based on your needs
        return results
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        return f"An error occurred: {str(e)}"



def run_server():
    """
    Starts the MCP server with HTTP transport.
    
    This function is called by __main__.py to start the server.
    """
    try:
        
        logger.info(f"Starting MCP server '{mcp.name}' on port {port}...")
        
        # Run the server
        mcp.run(
            transport="streamable-http",  # Use HTTP transport for compatibility
            host="0.0.0.0",              # Listen on all interfaces
            port=8000,                    # Port number
            path="/mcp",                  # URL path for MCP endpoints
            log_level="info",            # Logging verbosity
        )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server failed: {e}", exc_info=True)

# Allow running directly for testing
if __name__ == "__main__":
    print("Starting Example MCP Server directly...")
    run_server()


