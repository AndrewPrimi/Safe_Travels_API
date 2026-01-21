# FastMCP v2: A Comprehensive Guide

This document serves as a reference for building and interacting with Model Context Protocol (MCP) servers using `fastmcp` v2. It combines information from the official README and supplementary documentation.

## 1. Introduction

FastMCP v2 is the actively maintained, Pythonic framework for building MCP servers and clients. It provides a comprehensive toolkit that goes beyond the core MCP specification, offering features like deployment, authentication, client libraries, server proxying, and more.

FastMCP 1.0 was incorporated into the official MCP Python SDK, but v2 is the successor, designed for simplicity and production-readiness.

## 2. Installation

It is recommended to install FastMCP using `uv`:

```bash
uv pip install fastmcp
```

For detailed instructions, including upgrading from the official MCP SDK, refer to the official Installation Guide.

## 3. Core Concepts

These are the fundamental building blocks for creating MCP applications with FastMCP.

### The `FastMCP` Server

The `FastMCP` object is the central component of your application. It holds your tools, resources, and prompts.

**Initialization:**

```python
from fastmcp import FastMCP

# Create a server instance
mcp = FastMCP(name="MyAssistantServer")
```

### Tools (`@mcp.tool`)

Tools expose Python functions (sync or async) that an LLM can execute. They are ideal for performing actions, computations, or API calls. FastMCP automatically generates the necessary schema from your function's type hints and docstring.

**Example:**

```python
from fastmcp import FastMCP

mcp = FastMCP(name="CalculatorServer")

@mcp.tool
def add(a: int, b: int) -> int:
    """Adds two integer numbers together."""
    return a + b
```

### Resources & Templates (`@mcp.resource`)

Resources expose read-only data sources, similar to a GET request in a traditional API. You can create static resources or dynamic resource templates using placeholders in the URI.

**Static Resource:**

```python
@mcp.resource("config://version")
def get_version():
    return "2.0.1"
```

**Dynamic Resource Template:**

```python
@mcp.resource("users://{user_id}/profile")
def get_profile(user_id: int):
    # In a real application, you would fetch this from a database
    return {"name": f"User {user_id}", "status": "active"}
```

### Prompts (`@mcp.prompt`)

Prompts allow you to define reusable message templates to guide LLM interactions.

**Example:**

```python
@mcp.prompt
def summarize_request(text: str) -> str:
    """Generate a prompt asking for a summary."""
    return f"Please summarize the following text:\n\n{text}"
```

### Context (`ctx: Context`)

To access session-specific capabilities, add a parameter annotated as `Context` to any `@mcp` decorated function. FastMCP will automatically inject the context object.

The `Context` object provides methods for:
- **Logging**: `ctx.info()`, `ctx.warn()`, `ctx.error()`
- **LLM Sampling**: `ctx.sample()` to request completions from the client's LLM.
- **Resource Access**: `ctx.read_resource()` to read other resources on the server.
- **HTTP Requests**: `ctx.http_request()` to make external HTTP calls.
- **Progress Reporting**: `ctx.report_progress()`

**Example:**

```python
from fastmcp import FastMCP, Context

mcp = FastMCP("My MCP Server")

@mcp.tool
async def process_data(uri: str, ctx: Context):
    await ctx.info(f"Processing {uri}...")

    # Read a resource from the same server
    data = await ctx.read_resource(uri)

    # Ask the client's LLM to summarize the data
    summary = await ctx.sample(f"Summarize: {data.content[:500]}")

    return summary.text
```

## 4. MCP Clients

The `fastmcp.Client` allows you to interact with any MCP server programmatically.

### Basic Usage

```python
from fastmcp import Client

async def main():
    # Connect to a server running from a local script via stdio
    async with Client("my_server.py") as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {tools}")

        # Call a tool
        result = await client.call_tool("add", {"a": 5, "b": 3})
        # Result is a list of content objects
        print(f"Result: {result[0].text}")
```

### In-Memory Client for Testing

For testing, you can connect a client directly to a `FastMCP` server instance in memory, which is highly efficient.

```python
from fastmcp import FastMCP, Client

mcp = FastMCP("My Test Server")

@mcp.tool
def echo(message: str) -> str:
    return message

async def test_server():
    # Connect via the in-memory transport
    async with Client(mcp) as client:
        result = await client.call_tool("echo", {"message": "hello"})
        assert result[0].text == "hello"
```

### Error Handling

It's important to handle potential errors when using the client.

```python
from fastmcp.exceptions import ClientError, ConnectionError

async def safe_call_tool():
    async with client:
        try:
            result = await client.call_tool("divide", {"a": 10, "b": 0})
            print(f"Result: {result}")
        except ClientError as e:
            # Handles errors raised by the tool on the server
            print(f"Tool call failed: {e}")
        except ConnectionError as e:
            # Handles network or connection issues
            print(f"Connection failed: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
```

## 5. Running Your Server

You can run your FastMCP server using different transport protocols.

### `mcp.run()`

The `run()` method is the simplest way to start your server.

**STDIO (Default):**
Best for local tools and simple scripts.

```python
# server.py
from fastmcp import FastMCP

mcp = FastMCP("Demo")

@mcp.tool
def hello(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run() # transport="stdio" is the default
```

**Streamable HTTP:**
Recommended for web deployments.

```python
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000, path="/mcp")
```

**SSE (Server-Sent Events):**
For compatibility with existing SSE clients.

```python
if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8000)
```

### ASGI with Uvicorn

For production deployments, you can expose the underlying ASGI app and run it with a server like Uvicorn.

**1. Expose the ASGI app in your server file:**
```python
# server.py
from fastmcp import FastMCP

mcp = FastMCP("My ASGI App")
# ... define tools ...

# Expose the app for an ASGI server
http_app = mcp.as_asgi()
```

**2. Run with Uvicorn from the command line:**
```bash
uvicorn server:http_app --host 0.0.0.0 --port 8000
```

## 6. Advanced Features

FastMCP includes a suite of advanced features for production use cases.

- **Proxy Servers**: Create a server that acts as an intermediary for another MCP server using `FastMCP.as_proxy()`.
- **Composing Servers**: Mount multiple `FastMCP` instances onto a parent server using `mcp.mount()` or `mcp.import_server()`.
- **OpenAPI & FastAPI Generation**: Automatically create FastMCP servers from OpenAPI specifications (`FastMCP.from_openapi()`) or FastAPI applications (`FastMCP.from_fastapi()`).
- **Authentication & Security**: Secure servers and authenticate clients using built-in providers.

Refer to the official documentation for detailed guides on these advanced topics.
