# Agent User Interaction (AG-UI) Protocol

The **Agent User Interaction (AG-UI) Protocol** is an open standard introduced by the **CopilotKit** team that standardises how frontend applications communicate with AI agents, with support for streaming, frontend tools, shared state, and custom events.

Any **Pydantic AI** agent can be exposed as an **AG-UI** server using the `Agent.to_ag_ui()` convenience method.

> ### Note
> The AG-UI integration was originally built by the team at **Rocket Science** and contributed in collaboration with the **Pydantic AI** and **CopilotKit** teams. Thanks **Rocket Science**!

## Installation

The only dependencies are:

- `ag-ui-protocol`: to provide the AG-UI types and encoder
- `starlette`: to expose the AG-UI server as an ASGI application

You can install **Pydantic AI** with the `ag-ui` extra to ensure you have all the required **AG-UI** dependencies:


### pip / uv

```bash
pip install 'pydantic-ai-slim[ag-ui]'
```

To run the examples you'll also need:

- `uvicorn` or another ASGI compatible server

### pip / uv

```bash
pip install uvicorn
```

## Quick start
To expose a **Pydantic AI** agent as an **AG-UI** server, you can use the `Agent.to_ag_ui()` method:

**agent_to_ag_ui.py**
```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4.1', instructions='Be fun!')
app = agent.to_ag_ui()
```

Since `app` is an ASGI application, it can be used with any ASGI server:

```bash
uvicorn agent_to_ag_ui:app --host 0.0.0.0 --port 9000
```

This will expose the agent as an **AG-UI** server, and your frontend can start sending requests to it.

The `to_ag_ui()` method accepts the same arguments as the `Agent.iter()` method as well as arguments that let you configure the **Starlette-based** ASGI app.

## Design
The **Pydantic AI AG-UI** integration supports all features of the spec:

- Events
- Messages
- State Management
- Tools

The app receives messages in the form of a `RunAgentInput` which describes the details of a request being passed to the agent including messages and state. These are then converted to **Pydantic AI** types and passed to the agent which then process the request.

Events from the agent, including tool calls, are converted to **AG-UI** events and streamed back to the caller as **Server-Sent Events (SSE)**.

A user request may require multiple round trips between client UI and **Pydantic AI** server, depending on the tools and events needed.

## Features

### State management
The adapter provides full support for **AG-UI** state management, which enables real-time synchronization between agents and frontend applications.

In the example below we have document state which is shared between the UI and server using the `StateDeps` which implements the `StateHandler` protocol that can be used to automatically decode state contained in `RunAgentInput.state` when processing requests.

**ag_ui_state.py**
```python
from pydantic import BaseModel

from pydantic_ai import Agent
from pydantic_ai.ag_ui import StateDeps


class DocumentState(BaseModel):
    """State for the document being written."""

    document: str = ''


agent = Agent(
    'openai:gpt-4.1',
    instructions='Be fun!',
    deps_type=StateDeps[DocumentState],
)
app = agent.to_ag_ui(deps=StateDeps(DocumentState()))
```

Since `app` is an ASGI application, it can be used with any ASGI server:

```bash
uvicorn ag_ui_state:app --host 0.0.0.0 --port 9000
```

### Tools
**AG-UI** frontend tools are seamlessly provided to the **Pydantic AI** agent, enabling rich user experiences with frontend user interfaces.

### Events
**Pydantic AI** tools can send **AG-UI** events simply by defining a tool which returns a (subclass of) `BaseEvent`, which allows for custom events and state updates.

**ag_ui_tool_events.py**
```python
from ag_ui.core import CustomEvent, EventType, StateSnapshotEvent
from pydantic import BaseModel

from pydantic_ai import Agent, RunContext
from pydantic_ai.ag_ui import StateDeps


class DocumentState(BaseModel):
    """State for the document being written."""

    document: str = ''


agent = Agent(
    'openai:gpt-4.1',
    instructions='Be fun!',
    deps_type=StateDeps[DocumentState],
)
app = agent.to_ag_ui(deps=StateDeps(DocumentState()))


@agent.tool
async def update_state(ctx: RunContext[StateDeps[DocumentState]]) -> StateSnapshotEvent:
    return StateSnapshotEvent(
        type=EventType.STATE_SNAPSHOT,
        snapshot=ctx.deps.state,
    )


@agent.tool_plain
async def custom_events() -> list[CustomEvent]:
    return [
        CustomEvent(
            type=EventType.CUSTOM,
            name='count',
            value=1,
        ),
        CustomEvent(
            type=EventType.CUSTOM,
            name='count',
            value=2,
        ),
    ]
```

Since `app` is an ASGI application, it can be used with any ASGI server:

```bash
uvicorn ag_ui_tool_events:app --host 0.0.0.0 --port 9000
```

## Examples
For more examples of how to use `to_ag_ui()` see `pydantic_ai_examples.ag_ui`, which includes a server for use with the **AG-UI Dojo**.