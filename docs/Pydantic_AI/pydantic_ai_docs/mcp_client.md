# Client

PydanticAI can act as an MCP client, connecting to MCP servers to use their tools.

## Install

You need to either install `pydantic-ai`, or `pydantic-ai-slim` with the `mcp` optional group:

### pip

```bash
pip install "pydantic-ai-slim[mcp]"
```

> **Note**  
> MCP integration requires Python 3.10 or higher.

## Usage

PydanticAI comes with two ways to connect to MCP servers:

- `MCPServerHTTP` which connects to an MCP server using the HTTP SSE transport  
- `MCPServerStdio` which runs the server as a subprocess and connects to it using the stdio transport

Examples of both are shown below; `mcp-run-python` is used as the MCP server in both examples.

---

## SSE Client

`MCPServerHTTP` connects over HTTP using the HTTP + Server Sent Events transport to a server.

> **Note**  
> `MCPServerHTTP` requires an MCP server to be running and accepting HTTP connections before calling `agent.run_mcp_servers()`. Running the server is not managed by PydanticAI.

The name "HTTP" is used since this implemented will be adapted in future to use the new Streamable HTTP currently in development.

Before creating the SSE client, we need to run the server ([docs here](#)):

### terminal (run sse server)

```bash
deno run \
  -N -R=node_modules -W=node_modules --node-modules-dir=auto \
  jsr:@pydantic/mcp-run-python sse
```

### mcp_sse_client.py

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP

server = MCPServerHTTP(url='http://localhost:3001/sse')  
agent = Agent('openai:gpt-4o', mcp_servers=[server])  

async def main():
    async with agent.run_mcp_servers():  
        result = await agent.run('How many days between 2000-01-01 and 2025-03-18?')
    print(result.output)
    #> There are 9,208 days between January 1, 2000, and March 18, 2025.
```

> (This example is complete, it can be run "as is" with Python 3.10+ — you'll need to add `asyncio.run(main())` to run `main`)

### What's happening here?

1. The model is receiving the prompt "how many days between 2000-01-01 and 2025-03-18?"
2. The model decides "Oh, I've got this `run_python_code` tool, that will be a good way to answer this question", and writes some python code to calculate the answer.
3. The model returns a tool call  
4. PydanticAI sends the tool call to the MCP server using the SSE transport  
5. The model is called again with the return value of running the code  
6. The model returns the final answer  

You can visualise this clearly, and even see the code that's run by adding three lines of code to instrument the example with logfire:

### mcp_sse_client_logfire.py

```python
import logfire

logfire.configure()
logfire.instrument_pydantic_ai()
```

> Will display as follows:

#### Logfire run python code

---

## MCP "stdio" Server

The other transport offered by MCP is the `stdio` transport where the server is run as a subprocess and communicates with the client over stdin and stdout. In this case, you'd use the `MCPServerStdio` class.

> **Note**  
> When using `MCPServerStdio` servers, the `agent.run_mcp_servers()` context manager is responsible for starting and stopping the server.

### mcp_stdio_client.py

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

server = MCPServerStdio(  
    'deno',
    args=[
        'run',
        '-N',
        '-R=node_modules',
        '-W=node_modules',
        '--node-modules-dir=auto',
        'jsr:@pydantic/mcp-run-python',
        'stdio',
    ]
)
agent = Agent('openai:gpt-4o', mcp_servers=[server])

async def main():
    async with agent.run_mcp_servers():
        result = await agent.run('How many days between 2000-01-01 and 2025-03-18?')
    print(result.output)
    #> There are 9,208 days between January 1, 2000, and March 18, 2025.
```