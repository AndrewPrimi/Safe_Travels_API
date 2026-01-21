 Pydantic AI Output API (`pydantic_ai.result`)

This document outlines the `StreamedRunResult` class, which is the primary interface for handling outputs from Pydantic AI agent runs, especially when streaming.

---

### `OutputDataT` TypeVar
```python
OutputDataT = TypeVar("OutputDataT", default=str, covariant=True)
A covariant type variable representing the result data type of a run. Defaults to 
str
.

StreamedRunResult dataclass
python
class StreamedRunResult(Generic[AgentDepsT, OutputDataT]):
Represents the result of a streamed run that returns structured data, typically via a tool call. Source code in pydantic_ai_slim/pydantic_ai/result.py

Attributes
is_complete: bool
A boolean flag that becomes True once the entire stream has been received and processed (i.e., after methods like 
stream
, stream_text, or get_output complete).
Message History Methods
all_messages()
python
all_messages(*, output_tool_return_content: str | None = None) -> list[ModelMessage]
Returns the complete history of messages for the run.

Parameters:
output_tool_return_content (str | None): Optionally, you can provide content to set as the return value of the final tool call in the history. This is useful for continuing a conversation.
all_messages_json()
python
all_messages_json(*, output_tool_return_content: str | None = None) -> bytes
Returns the complete message history as JSON bytes.

new_messages()
python
new_messages(*, output_tool_return_content: str | None = None) -> list[ModelMessage]
Returns only the new messages generated during this specific run, excluding any previous history.

new_messages_json()
python
new_messages_json(*, output_tool_return_content: str | None = None) -> bytes
Returns the new messages as JSON bytes.

Streaming Methods
stream()
 (async)
python
async stream(*, debounce_by: float | None = 0.1) -> AsyncIterator[OutputDataT]
Streams the response as an async iterable. For structured data, the Pydantic validator is called in partial mode on each iteration.

Parameters:
debounce_by (float | None): Groups response chunks to reduce validation overhead. Defaults to 0.1 seconds.
stream_text() (async)
python
async stream_text(*, delta: bool = False, debounce_by: float | None = 0.1) -> AsyncIterator[str]
Streams the text result as an async iterable of strings.

Parameters:
delta (bool): If True, yields each text chunk as it arrives. If False (default), yields the accumulated text so far.
debounce_by (float | None): Debounces response chunks.
stream_structured() (async)
python
async stream_structured(*, debounce_by: float | None = 0.1) -> AsyncIterator[tuple[ModelResponse, bool]]
Streams the response as an async iterable of structured ModelResponse messages.

Returns: An async iterator yielding tuples of (ModelResponse, is_last_message_bool).
Utility Methods
get_output() (async)
python
async get_output() -> OutputDataT
Awaits the entire stream, validates the final result, and returns it.

usage()
python
usage() -> Usage
Returns the token usage for the run. This value is only complete after the stream has finished.

timestamp()
python
timestamp() -> datetime
Gets the timestamp of the model's response.

validate_structured_output() (async)
python
async validate_structured_output(message: ModelResponse, *, allow_partial: bool = False) -> OutputDataT
Validates a given ModelResponse message against the expected output schema.