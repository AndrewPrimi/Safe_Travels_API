# pydantic_ai.models.openai

## Setup

For details on how to set up authentication with this model, see [model configuration for OpenAI](https://ai.pydantic.dev/models/openai/).

---

## OpenAIModelName (module-attribute)

```python
OpenAIModelName = str | AllModels
```

**Possible OpenAI model names.**

Since OpenAI supports a variety of date-stamped models, we explicitly list the latest models but allow any name in the type hints. See the [OpenAI docs](https://platform.openai.com/docs/models) for a full list.

Using this more broad type for the model name instead of the `ChatModel` definition allows this model to be used more easily with other model types (ie, Ollama, Deepseek).

---

## OpenAIChatModelSettings

**Bases:** `ModelSettings`

Settings used for an OpenAI model request.

**Source code:** `pydantic_ai_slim/pydantic_ai/models/openai.py`

### Instance Attributes

#### `openai_reasoning_effort`

```python
openai_reasoning_effort: ReasoningEffort
```
Constrains effort on reasoning for reasoning models.

Currently supported values are `low`, `medium`, and `high`. Reducing reasoning effort can result in faster responses and fewer tokens used on reasoning in a response.

#### `openai_logprobs`

```python
openai_logprobs: bool
```
Include log probabilities in the response.

#### `openai_top_logprobs`

```python
openai_top_logprobs: int
```
Include log probabilities of the top n tokens in the response.

#### `openai_user`

```python
openai_user: str
```
A unique identifier representing the end-user, which can help OpenAI monitor and detect abuse.

See [OpenAI's safety best practices](https://platform.openai.com/docs/guides/safety-best-practices) for more details.

#### `openai_service_tier`

```python
openai_service_tier: Literal["auto", "default", "flex", "priority"]
```

The service tier to use for the model request.

Currently supported values are `auto`, `default`, `flex`, and `priority`. For more information, see [OpenAI's service tiers documentation](https://platform.openai.com/docs/guides/rate-limits).

#### `openai_prediction`

```python
openai_prediction: ChatCompletionPredictionContentParam
```

Enables predictive outputs.

This feature is currently only supported for some OpenAI models.

---

## OpenAIModelSettings (deprecated)

**Bases:** `OpenAIChatModelSettings`

> **Deprecated:** Use `OpenAIChatModelSettings` instead.

Deprecated alias for `OpenAIChatModelSettings`.

**Source code:** `pydantic_ai_slim/pydantic_ai/models/openai.py`

---
## OpenAIResponsesModelSettings

**Bases:** `OpenAIChatModelSettings`

Settings used for an OpenAI Responses model request.

> **Note:** ALL FIELDS MUST BE `openai_` PREFIXED SO YOU CAN MERGE THEM WITH OTHER MODELS.

**Source code:** `pydantic_ai_slim/pydantic_ai/models/openai.py`

### Instance Attributes
#### `openai_builtin_tools`

```python
openai_builtin_tools: Sequence[
    FileSearchToolParam
    | WebSearchToolParam
    | ComputerToolParam
]
```

The provided OpenAI built-in tools to use.

See [OpenAI's built-in tools](https://platform.openai.com/docs/guides/function-calling) for more details.

#### `openai_reasoning_generate_summary` (deprecated)

```python
openai_reasoning_generate_summary: Literal["detailed", "concise"]
```

> **Deprecated:** Use `openai_reasoning_summary` instead.

#### `openai_reasoning_summary`

```python
openai_reasoning_summary: Literal['detailed', 'concise']
```

A summary of the reasoning performed by the model.

This can be useful for debugging and understanding the model's reasoning process. One of `concise` or `detailed`.

Check the [OpenAI Reasoning documentation](https://platform.openai.com/docs/guides/reasoning) for more details.

#### `openai_send_reasoning_ids`

```python
openai_send_reasoning_ids: bool
```

Whether to send the unique IDs of reasoning, text, and function call parts from the message history to the model. Enabled by default for reasoning models.

This can result in errors like `"Item 'rs_123' of type 'reasoning' was provided without its required following item."` if the message history you're sending does not match exactly what was received from the Responses API in a previous response, for example if you're using a history processor. In that case, you'll want to disable this.

#### `openai_truncation`

```python
openai_truncation: Literal['disabled', 'auto']
```

The truncation strategy to use for the model response.

It can be either:
- **`disabled`** (default): If a model response will exceed the context window size for a model, the request will fail with a 400 error.
- **`auto`**: If the context of this response and previous ones exceeds the model's context window size, the model will truncate the response to fit the context window by dropping input items in the middle of the conversation.

#### `openai_text_verbosity`

```python
openai_text_verbosity: Literal['low', 'medium', 'high']
```

Constrains the verbosity of the model's text response.

Lower values will result in more concise responses, while higher values will result in more verbose responses. Currently supported values are `low`, `medium`, and `high`.

#### `openai_previous_response_id`

```python
openai_previous_response_id: Literal['auto'] | str
```

The ID of a previous response from the model to use as the starting point for a continued conversation.

When set to `'auto'`, the request automatically uses the most recent `provider_response_id` from the message history and omits earlier messages.

This enables the model to use server-side conversation state and faithfully reference previous reasoning. See the [OpenAI Responses API documentation](https://platform.openai.com/docs/api-reference/responses) for more information.

#### `openai_include_code_execution_outputs`

```python
openai_include_code_execution_outputs: bool
```

Whether to include the code execution results in the response.

Corresponds to the `code_interpreter_call.outputs` value of the `include` parameter in the Responses API.

#### `openai_include_web_search_sources`

```python
openai_include_web_search_sources: bool
```

Whether to include the web search results in the response.

Corresponds to the `web_search_call.action.sources` value of the `include` parameter in the Responses API.

---

## OpenAIChatModel (dataclass)

**Bases:** `Model`

A model that uses the OpenAI API.

Internally, this uses the [OpenAI Python client](https://github.com/openai/openai-python) to interact with the API.

Apart from `__init__`, all methods are private or match those of the base class.

**Source code:** `pydantic_ai_slim/pydantic_ai/models/openai.py`

### `__init__`

```python
__init__(
    model_name: OpenAIModelName,
    *,
    provider: (
        Literal[
            "azure",
            "deepseek",
            "cerebras",
            "fireworks",
            "github",
            "grok",
            "heroku",
            "moonshotai",
            "ollama",
            "openai",
            "openai-chat",
            "openrouter",
            "together",
            "vercel",
            "litellm",
        ]
        | Provider[AsyncOpenAI]
    ) = "openai",
    profile: ModelProfileSpec | None = None,
    system_prompt_role: OpenAISystemPromptRole | None = None,
    settings: ModelSettings | None = None
) -> None
```

**Initialize an OpenAI model.**

#### Parameters

| Name | Type | Description | Default |
|------|------|-------------|---------|
| `model_name` | `OpenAIModelName` | The name of the OpenAI model to use. List of model names available [here](https://platform.openai.com/docs/models) (Unfortunately, despite being asked to do so, OpenAI do not provide .inv files for their API). | required |
| `provider` | `Literal['azure', 'deepseek', 'cerebras', 'fireworks', 'github', 'grok', 'heroku', 'moonshotai', 'ollama', 'openai', 'openai-chat', 'openrouter', 'together', 'vercel', 'litellm'] \| Provider[AsyncOpenAI]` | The provider to use. Defaults to `'openai'`. | `'openai'` |
| `profile` | `ModelProfileSpec \| None` | The model profile to use. Defaults to a profile picked by the provider based on the model name. | `None` |
| `system_prompt_role` | `OpenAISystemPromptRole \| None` | The role to use for the system prompt message. If not provided, defaults to `'system'`. In the future, this may be inferred from the model name. | `None` |
| `settings` | `ModelSettings \| None` | Default model settings for this model instance. | `None` |

**Source code:** `pydantic_ai_slim/pydantic_ai/models/openai.py`

### Properties

#### `model_name`

```python
model_name: OpenAIModelName
```

The model name.

#### `system`

```python
system: str
```

The model provider.

---

## OpenAIModel (dataclass, deprecated)

**Bases:** `OpenAIChatModel`

> **Deprecated:** `OpenAIModel` was renamed to `OpenAIChatModel` to clearly distinguish it from `OpenAIResponsesModel` which uses OpenAI's newer Responses API. Use that unless you're using an OpenAI Chat Completions-compatible API, or require a feature that the Responses API doesn't support yet like audio.

Deprecated alias for `OpenAIChatModel`.

**Source code:** `pydantic_ai_slim/pydantic_ai/models/openai.py`

---

## OpenAIResponsesModel (dataclass)

**Bases:** `Model`

A model that uses the OpenAI Responses API.

The OpenAI Responses API is the new API for OpenAI models.

If you are interested in the differences between the Responses API and the Chat Completions API, see the [OpenAI API docs](https://platform.openai.com/docs/api-reference/responses).

**Source code:** `pydantic_ai_slim/pydantic_ai/models/openai.py`

### `__init__`

```python
__init__(
    model_name: OpenAIModelName,
    *,
    provider: (
        Literal[
            "openai",
            "deepseek",
            "azure",
            "openrouter",
            "grok",
            "fireworks",
            "together",
        ]
        | Provider[AsyncOpenAI]
    ) = "openai",
    profile: ModelProfileSpec | None = None,
    settings: ModelSettings | None = None
)
```

**Initialize an OpenAI Responses model.**

#### Parameters

| Name | Type | Description | Default |
|------|------|-------------|---------|
| `model_name` | `OpenAIModelName` | The name of the OpenAI model to use. | required |
| `provider` | `Literal['openai', 'deepseek', 'azure', 'openrouter', 'grok', 'fireworks', 'together'] \| Provider[AsyncOpenAI]` | The provider to use. Defaults to `'openai'`. | `'openai'` |
| `profile` | `ModelProfileSpec \| None` | The model profile to use. Defaults to a profile picked by the provider based on the model name. | `None` |
| `settings` | `ModelSettings \| None` | Default model settings for this model instance. | `None` |

**Source code:** `pydantic_ai_slim/pydantic_ai/models/openai.py`

### Properties

#### `model_name`

```python
model_name: OpenAIModelName
```

The model name.

#### `system`

```python
system: str
```

The model provider.