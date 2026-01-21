# `pydantic_ai.ag_ui`

Provides an **AG-UI** protocol adapter for the **Pydantic AI** agent.

This package provides seamless integration between `pydantic-ai` agents and `ag-ui` for building interactive AI applications with streaming event-based communication.

---

### `SSE_CONTENT_TYPE` module-attribute

```python
SSE_CONTENT_TYPE: Final[str] = 'text/event-stream'
```
Content type header value for **Server-Sent Events (SSE)**.

---

## `AGUIApp`
**Bases**: `Generic[AgentDepsT, OutputDataT]`, `Starlette`

ASGI application for running **Pydantic AI** agents with **AG-UI** protocol support.

*Source code in `pydantic_ai_slim/pydantic_ai/ag_ui.py`*

### `__init__`

```python
__init__(
    agent: Agent[AgentDepsT, OutputDataT],
    *,
    output_type: OutputSpec[OutputDataT] | None = None,
    model: Model | KnownModelName | str | None = None,
    deps: AgentDepsT = None,
    model_settings: ModelSettings | None = None,
    usage_limits: UsageLimits | None = None,
    usage: Usage | None = None,
    infer_name: bool = True,
    toolsets: Sequence[AbstractToolset[AgentDepsT]] | None = None,
    debug: bool = False,
    routes: Sequence[BaseRoute] | None = None,
    middleware: Sequence[Middleware] | None = None,
    exception_handlers: Mapping[Any, ExceptionHandler] | None = None,
    on_startup: Sequence[Callable[[], Any]] | None = None,
    on_shutdown: Sequence[Callable[[], Any]] | None = None,
    lifespan: Lifespan[AGUIApp[AgentDepsT, OutputDataT]] | None = None
) -> None
```

Initialise the **AG-UI** application.

#### Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| **agent** | `Agent[AgentDepsT, OutputDataT]` | The Pydantic AI Agent to adapt. | *required* |
| **output_type** | `OutputSpec[OutputDataT] | None` | Custom output type to use for this run. | `None` |
| **model** | `Model | KnownModelName | str | None` | Optional model to use for this run. | `None` |
| **deps** | `AgentDepsT` | Optional dependencies to use for this run. | `None` |
| **model_settings** | `ModelSettings | None` | Optional settings for this model's request. | `None` |
| **usage_limits** | `UsageLimits | None` | Optional limits on model request count or token usage. | `None` |
| **usage** | `Usage | None` | Optional usage to start with. | `None` |
| **infer_name** | `bool` | Whether to infer the agent name from the call frame. | `True` |
| **toolsets** | `Sequence[AbstractToolset[AgentDepsT]] | None` | Optional list of toolsets to use. | `None` |
| **debug** | `bool` | Boolean indicating if debug tracebacks should be returned. | `False` |
| **routes** | `Sequence[BaseRoute] | None` | A list of routes to serve requests. | `None` |
| **middleware** | `Sequence[Middleware] | None` | A list of middleware to run for every request. | `None` |
| **exception_handlers** | `Mapping[Any, ExceptionHandler] | None` | A mapping of status codes or exception types to handlers. | `None` |
| **on_startup** | `Sequence[Callable[[], Any]] | None` | A list of callables to run on application startup. | `None` |
| **on_shutdown** | `Sequence[Callable[[], Any]] | None` | A list of callables to run on application shutdown. | `None` |
| **lifespan** | `Lifespan[...] | None` | A lifespan context function for startup/shutdown tasks. | `None` |

*Source code in `pydantic_ai_slim/pydantic_ai/ag_ui.py`*

---

## `StateHandler`
**Bases**: `Protocol`

Protocol for state handlers in agent runs.

*Source code in `pydantic_ai_slim/pydantic_ai/ag_ui.py`*

### `state` property (writable)

```python
state: State
```
Get the current state of the agent run.

---

## `StateDeps`
**Bases**: `Generic[StateT]`

Provides **AG-UI** state management.

This class manages the state of an agent run, allowing the state to be set with a specific model (`BaseModel` subclass). The state is set by the Adapter when the run starts. Implements the `StateHandler` protocol.

*Source code in `pydantic_ai_slim/pydantic_ai/ag_ui.py`*

### `__init__`

```python
__init__(default: StateT) -> None
```
Initialize the state with the provided state type.

*Source code in `pydantic_ai_slim/pydantic_ai/ag_ui.py`*

### `state` property (writable)

```python
state: StateT
```
Get the current state of the agent run.

#### Returns:

| Type | Description |
| --- | --- |
| `StateT` | The current run state. |