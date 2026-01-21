# MCP Explained: A Beginner's Guide

## What is an MCP Server?

Think of an MCP (Model Context Protocol) server as a **tool box** that AI agents can use. Just like how you might have different tools in a toolbox (hammer, screwdriver, etc.), an MCP server provides different tools that an AI can use to help you.

**Key Idea**: MCP creates a universal standard - like having universal electrical outlets that work with any plug. Any AI agent that supports MCP can use ANY MCP server's tools without special setup!

## Why Use MCP?

Imagine you want your AI assistant to:
- Search the web for you
- Read your emails
- Update your calendar
- Check the weather

Instead of building these features into every AI, MCP lets you create separate "tool servers" that ANY AI can connect to and use!

## Understanding the MCP Server Structure

Let's explore our example MCP server step by step. Think of it like building a house - each part has a specific purpose.

### 📁 Project Structure Overview

```
Search_MCP/
├── pyproject.toml           # The "recipe" for building your server
├── src/                     # Your source code folder
│   └── Example_MCP/         # Your server's main folder
│       ├── __main__.py      # The "start button" for your server
│       ├── config.py        # Settings and configuration
│       ├── functions.py     # The actual work your tools do
│       └── server.py        # The main server logic
└── docs/                    # Documentation
```

## Breaking Down Each File

### 1. 📄 pyproject.toml - Your Server's Recipe

This file tells Python how to build and install your server. Think of it like a recipe card that lists:
- The name of your dish (server name)
- Ingredients needed (dependencies like `fastmcp`, `httpx`)
- Cooking instructions (how to build)

**Key parts:**
- `name`: Your server's name
- `dependencies`: Other packages your server needs to work
- `[project.scripts]`: Creates a command to run your server

### 2. 📄 __main__.py - The Start Button

The double underscores (`__`) are special in Python - they make this folder act like a program you can run!

This file is super simple - it just:
1. Imports the server
2. Starts it when you run the program
3. Handles shutting down gracefully (when you press Ctrl+C)

**Think of it as**: The power button on your computer - it starts everything up!

### 3. 📄 config.py - Your Settings Manager

This is where you store important settings like:
- API keys (passwords to use external services)
- URLs for external services
- Any other configuration

**What are Environment Variables (.env)?**
- These are like secret notes you don't want in your code
- Example: Your API key is like your house key - you don't tape it to your front door!
- You create a `.env` file that looks like:
  ```
  EXAMPLE_API_KEY=your-secret-key-here
  ```
- Your code reads this file but you NEVER share it with others

**Why use config.py?**
- Keeps secrets safe
- Makes it easy to change settings without changing code
- Different environments (testing vs production) can use different settings

### 4. 📄 functions.py - Where the Magic Happens

This file contains the actual work your tools do. For example:
- If you have a "search" tool, the search logic goes here
- If you have a "calculate" tool, the math goes here

**Think of it as**: The engine in a car - it's where the actual work happens!

In our example, `simple_search` function:
1. Takes a search query
2. Calls an external API
3. Returns the results

### 5. 📄 server.py - The Control Center

This is the most important file! It:

#### Sets up the Lifecycle Manager
```python
@asynccontextmanager
async def lifespan(mcp: FastMCP):
    # This runs when server starts
    http_client = httpx.AsyncClient()  # Create a web client
    
    yield  # Server runs here
    
    # This runs when server stops
    await http_client.aclose()  # Clean up
```

**Think of it as**: Opening a shop in the morning (startup), keeping it open all day (yield), then closing and cleaning up at night (shutdown).

#### Creates the MCP Server
```python
mcp = FastMCP(
    name="example-mcp",
    instructions="What this server does"
)
```

#### Defines Tools with Decorators
```python
@mcp.tool(description="Search for information")
async def search(query: str) -> str:
    """
    This docstring is SUPER IMPORTANT!
    The AI reads this to understand how to use your tool.
    """
```

**Important**: The description and docstring tell the AI:
- What the tool does
- What parameters it needs
- What it returns

#### Runs the Server
The server listens on `http://0.0.0.0:8000/mcp` - like opening a shop at a specific address!

## How to Install and Run Your MCP Server

### Step 1: Install Your Server

1. Open your terminal/command prompt
2. Navigate to your MCP folder:
   ```bash
   cd Search_MCP
   ```
3. Install the server:
   ```bash
   pip install -e .
   ```

**What does `pip install -e .` mean?**
- `pip install`: Python's way of installing packages
- `-e`: "Editable" mode - changes you make take effect immediately
- `.`: Install from the current directory

This command:
- Reads your `pyproject.toml`
- Installs all dependencies
- Makes your server available as a command

### Step 2: Run Your Server

From the Search_MCP directory(so already inside of Search_MCP), run:
```bash
python -m Example_MCP
```

**What this means:**
- `python`: Use Python to run something
- `-m`: Run a module (a Python package)
- `Example_MCP`: The name of your module

Your server will start and show:
```
--- Brave Search MCP Server --- (Press Ctrl+C to exit)
Starting MCP server 'example-mcp' on port 8000...
```

### Step 3: Connect Your AI to the Server

1. Add this to your `.env` file:
   ```
   MCP_SERVER_URL=http://127.0.0.1:8000/mcp
   ```

2. Your AI agent can now connect to this URL and use your tools!

## Common Beginner Questions

**Q: What's the difference between 0.0.0.0 and 127.0.0.1?**
- `0.0.0.0`: Your server listens on ALL network interfaces
- `127.0.0.1`: How you connect to it locally (also called "localhost")

**Q: Why do we need all these files?**
- Each file has ONE job - this makes it easier to understand and fix problems
- Like a restaurant: kitchen (functions), waiter (server), menu (config)

**Q: What if I get errors?**
- Check your `.env` file exists and has the right keys
- Make sure you ran `pip install -e .`
- Look at the error message - it usually tells you what's wrong!

## Quick Summary

1. **MCP Server** = A toolbox for AI agents
2. **Structure** = Multiple files, each with a specific job
3. **Config** = Keep secrets in `.env` files
4. **Functions** = Where your actual tool logic lives
5. **Server** = Manages everything and defines tools
6. **Running** = Install with pip, run with python -m

Remember: Start simple! Get one tool working before adding more. You're building something that ANY AI can use - that's powerful!