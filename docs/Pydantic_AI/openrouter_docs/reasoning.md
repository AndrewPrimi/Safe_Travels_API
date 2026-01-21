# Reasoning Tokens

For models that support it, the OpenRouter API can return Reasoning Tokens, also known as thinking tokens. OpenRouter normalizes the different ways of customizing the amount of reasoning tokens that the model will use, providing a unified interface across different providers.

Reasoning tokens provide a transparent look into the reasoning steps taken by a model. Reasoning tokens are considered output tokens and charged accordingly.

Reasoning tokens are included in the response by default if the model decides to output them. Reasoning tokens will appear in the `reasoning` field of each message, unless you decide to exclude them.

> **Some reasoning models do not return their reasoning tokens**
> While most models and providers make reasoning tokens available in the response, some (like the OpenAI o-series and Gemini Flash Thinking) do not.

## Controlling Reasoning Tokens

You can control reasoning tokens in your requests using the `reasoning` parameter:

```json
{
  "model": "your-model",
  "messages": [],
  "reasoning": {
    // One of the following (not both):
    "effort": "high", // Can be "high", "medium", "low", "minimal" or "none" (OpenAI-style)
    "max_tokens": 2000, // Specific token limit (Anthropic-style)
    // Optional: Default is false. All models support this.
    "exclude": false, // Set to true to exclude reasoning tokens from response
    // Or enable reasoning with the default parameters:
    "enabled": true // Default: inferred from `effort` or `max_tokens`
  }
}
```

The `reasoning` config object consolidates settings for controlling reasoning strength across different models. See the Note for each option below to see which models are supported and how other models will behave.

### Max Tokens for Reasoning

**Supported models:**
*   Gemini thinking models
*   Anthropic reasoning models (by using the `reasoning.max_tokens` parameter)
*   Some Alibaba Qwen thinking models (mapped to `thinking_budget`)

> For Alibaba, support varies by model — please check the individual model descriptions to confirm whether `reasoning.max_tokens` (via `thinking_budget`) is available.

For models that support reasoning token allocation, you can control it like this:

*   `"max_tokens": 2000` - Directly specifies the maximum number of tokens to use for reasoning

For models that only support `reasoning.effort` (see below), the `max_tokens` value will be used to determine the effort level.

### Reasoning Effort Level

**Supported models:**
*   OpenAI reasoning models (o1 series, o3 series, GPT-5 series)
*   Grok models

*   `"effort": "high"` - Allocates a large portion of tokens for reasoning (approximately 80% of `max_tokens`)
*   `"effort": "medium"` - Allocates a moderate portion of tokens (approximately 50% of `max_tokens`)
*   `"effort": "low"` - Allocates a smaller portion of tokens (approximately 20% of `max_tokens`)
*   `"effort": "minimal"` - Allocates an even smaller portion of tokens (approximately 10% of `max_tokens`)
*   `"effort": "none"` - Disables reasoning entirely

For models that only support `reasoning.max_tokens`, the effort level will be set based on the percentages above.

### Excluding Reasoning Tokens

If you want the model to use reasoning internally but not include it in the response:

*   `"exclude": true` - The model will still use reasoning, but it won’t be returned in the response

Reasoning tokens will appear in the `reasoning` field of each message.

### Enable Reasoning with Default Config

To enable reasoning with the default parameters:

*   `"enabled": true` - Enables reasoning at the “medium” effort level with no exclusions.

### Legacy Parameters

For backward compatibility, OpenRouter still supports the following legacy parameters:

*   `include_reasoning: true` - Equivalent to `reasoning: {}`
*   `include_reasoning: false` - Equivalent to `reasoning: { exclude: true }`

However, we recommend using the new unified `reasoning` parameter for better control and future compatibility.

## Examples

### Basic Usage with Reasoning Tokens

**TypeScript SDK**

```typescript
import { OpenRouter } from '@openrouter/sdk';
const openRouter = new OpenRouter({
  apiKey: '<OPENROUTER_API_KEY>',
});
const response = await openRouter.chat.send({
  model: 'openai/o3-mini',
  messages: [
    {
      role: 'user',
      content: "How would you build the world's tallest skyscraper?",
    },
  ],
  reasoning: {
    effort: 'high',
  },
  stream: false,
});
console.log('REASONING:', response.choices[0].message.reasoning);
console.log('CONTENT:', response.choices[0].message.content);
```

### Using Max Tokens for Reasoning

For models that support direct token allocation (like Anthropic models), you can specify the exact number of tokens to use for reasoning:

**Python**

```python
from openai import OpenAI
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="<OPENROUTER_API_KEY>",
)
response = client.chat.completions.create(
    model="anthropic/claude-3.7-sonnet",
    messages=[
        {"role": "user", "content": "What's the most efficient algorithm for sorting a large dataset?"}
    ],
    extra_body={
        "reasoning": {
            "max_tokens": 2000
        }
    },
)
msg = response.choices[0].message
print(getattr(msg, "reasoning", None))
print(getattr(msg, "content", None))
```

### Excluding Reasoning Tokens from Response

If you want the model to use reasoning internally but not include it in the response:

**Python**

```python
from openai import OpenAI
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="<OPENROUTER_API_KEY>",
)
response = client.chat.completions.create(
    model="deepseek/deepseek-r1",
    messages=[
        {"role": "user", "content": "Explain quantum computing in simple terms."}
    ],
    extra_body={
        "reasoning": {
            "effort": "high",
            "exclude": True
        }
    },
)
msg = response.choices[0].message
print(getattr(msg, "content", None))
```

### Advanced Usage: Reasoning Chain-of-Thought

This example shows how to use reasoning tokens in a more complex workflow. It injects one model’s reasoning into another model to improve its response quality:

**Python**

```python
from openai import OpenAI
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="<OPENROUTER_API_KEY>",
)
question = "Which is bigger: 9.11 or 9.9?"
def do_req(model: str, content: str, reasoning_config: dict | None = None):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "stop": "</think>",
    }
    if reasoning_config:
        payload.update(reasoning_config)
    return client.chat.completions.create(**payload)
# Get reasoning from a capable model
content = f"{question} Please think this through, but don't output an answer"
reasoning_response = do_req("deepseek/deepseek-r1", content)
reasoning = getattr(reasoning_response.choices[0].message, "reasoning", "")
# Let's test! Here's the naive response:
simple_response = do_req("openai/gpt-4o-mini", question)
print(getattr(simple_response.choices[0].message, "content", None))
# Here's the response with the reasoning token injected:
content = f"{question}. Here is some context to help you: {reasoning}"
smart_response = do_req("openai/gpt-4o-mini", content)
print(getattr(smart_response.choices[0].message, "content", None))
```

### Provider-Specific Reasoning Implementation

#### Anthropic Models with Reasoning Tokens

The latest Claude models, such as `anthropic/claude-3.7-sonnet`, support working with and returning reasoning tokens.

You can enable reasoning on Anthropic models only using the unified `reasoning` parameter with either `effort` or `max_tokens`.

> **Note:** The `:thinking` variant is no longer supported for Anthropic models. Use the `reasoning` parameter instead.

#### Reasoning Max Tokens for Anthropic Models

When using Anthropic models with reasoning:

*   When using the `reasoning.max_tokens` parameter, that value is used directly with a minimum of 1024 tokens.
*   When using the `reasoning.effort` parameter, the `budget_tokens` are calculated based on the `max_tokens` value.
*   The reasoning token allocation is capped at 32,000 tokens maximum and 1024 tokens minimum. The formula for calculating the `budget_tokens` is: `budget_tokens = max(min(max_tokens * {effort_ratio}, 32000), 1024)`
*   `effort_ratio` is 0.8 for high effort, 0.5 for medium effort, 0.2 for low effort, and 0.1 for minimal effort.

> **Important:** `max_tokens` must be strictly higher than the reasoning budget to ensure there are tokens available for the final response after thinking.

#### Token Usage and Billing

Please note that reasoning tokens are counted as output tokens for billing purposes. Using reasoning tokens will increase your token usage but can significantly improve the quality of model responses.

#### Examples with Anthropic Models

**Example 1: Streaming mode with reasoning tokens**

**Python**

```python
from openai import OpenAI
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="<OPENROUTER_API_KEY>",
)
def chat_completion_with_reasoning(messages):
    response = client.chat.completions.create(
        model="anthropic/claude-3.7-sonnet",
        messages=messages,
        max_tokens=10000,
        extra_body={
            "reasoning": {
                "max_tokens": 8000
            }
        },
        stream=True
    )
    return response
for chunk in chat_completion_with_reasoning([
    {"role": "user", "content": "What's bigger, 9.9 or 9.11?"}
]):
    if hasattr(chunk.choices[0].delta, 'reasoning_details') and chunk.choices[0].delta.reasoning_details:
        print(f"REASONING_DETAILS: {chunk.choices[0].delta.reasoning_details}")
    elif getattr(chunk.choices[0].delta, 'content', None):
        print(f"CONTENT: {chunk.choices[0].delta.content}")
```

### Preserving Reasoning Blocks

#### Model Support

Preserving reasoning with `reasoning_details` is currently supported by:

*   All OpenAI reasoning models (o1 series, o3 series, GPT-5 series)
*   All Anthropic reasoning models (Claude 3.7, Claude 4, and Claude 4.1 series)
*   All Gemini Reasoning models
*   All xAI reasoning models
*   MiniMax M2
*   Kimi K2 Thinking
*   INTELLECT-3

The `reasoning_details` functionality works identically across all supported reasoning models. You can easily switch between OpenAI reasoning models (like `openai/gpt-5-mini`) and Anthropic reasoning models (like `anthropic/claude-sonnet-4`) without changing your code structure.

If you want to pass reasoning back in context, you must pass reasoning blocks back to the API. This is useful for maintaining the model’s reasoning flow and conversation integrity.

Preserving reasoning blocks is useful specifically for tool calling. When models like Claude invoke tools, it is pausing its construction of a response to await external information. When tool results are returned, the model will continue building that existing response. This necessitates preserving reasoning blocks during tool use, for a couple of reasons:

*   **Reasoning continuity:** The reasoning blocks capture the model’s step-by-step reasoning that led to tool requests. When you post tool results, including the original reasoning ensures the model can continue its reasoning from where it left off.
*   **Context maintenance:** While tool results appear as user messages in the API structure, they’re part of a continuous reasoning flow. Preserving reasoning blocks maintains this conceptual flow across multiple API calls.

#### Important for Reasoning Models

When providing `reasoning_details` blocks, the entire sequence of consecutive reasoning blocks must match the outputs generated by the model during the original request; you cannot rearrange or modify the sequence of these blocks.

#### Example: Preserving Reasoning Blocks with OpenRouter and Claude

**Python**

```python
from openai import OpenAI
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="<OPENROUTER_API_KEY>",
)
# Define tools once and reuse
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        }
    }
}]
# First API call with tools
# Note: You can use 'openai/gpt-5-mini' instead of 'anthropic/claude-sonnet-4' - they're completely interchangeable
response = client.chat.completions.create(
    model="anthropic/claude-sonnet-4",
    messages=[
        {"role": "user", "content": "What's the weather like in Boston? Then recommend what to wear."}
    ],
    tools=tools,
    extra_body={"reasoning": {"max_tokens": 2000}}
)
# Extract the assistant message with reasoning_details
message = response.choices[0].message
# Preserve the complete reasoning_details when passing back
messages = [
    {"role": "user", "content": "What's the weather like in Boston? Then recommend what to wear."},
    {
        "role": "assistant",
        "content": message.content,
        "tool_calls": message.tool_calls,
        "reasoning_details": message.reasoning_details  # Pass back unmodified
    },
    {
        "role": "tool",
        "tool_call_id": message.tool_calls[0].id,
        "content": '{"temperature": 45, "condition": "rainy", "humidity": 85}'
    }
]
# Second API call - Claude continues reasoning from where it left off
response2 = client.chat.completions.create(
    model="anthropic/claude-sonnet-4",
    messages=messages,  # Includes preserved thinking blocks
    tools=tools
)
```

For more detailed information about thinking encryption, redacted blocks, and advanced use cases, see Anthropic’s documentation on extended thinking.

For more information about OpenAI reasoning models, see OpenAI’s reasoning documentation.

### Responses API Shape

When reasoning models generate responses, the reasoning information is structured in a standardized format through the `reasoning_details` array. This section documents the API response structure for reasoning details in both streaming and non-streaming responses.

#### reasoning_details Array Structure

The `reasoning_details` field contains an array of reasoning detail objects. Each object in the array represents a specific piece of reasoning information and follows one of three possible types. The location of this array differs between streaming and non-streaming responses:

*   **Non-streaming responses:** `reasoning_details` appears in `choices[].message.reasoning_details`
*   **Streaming responses:** `reasoning_details` appears in `choices[].delta.reasoning_details` for each chunk

#### Common Fields

All reasoning detail objects share these common fields:

*   `id` (string | null): Unique identifier for the reasoning detail
*   `format` (string): The format of the reasoning detail, with possible values:
    *   `"unknown"` - Format is not specified
    *   `"openai-responses-v1"` - OpenAI responses format version 1
    *   `"xai-responses-v1"` - xAI responses format version 1
    *   `"anthropic-claude-v1"` - Anthropic Claude format version 1 (default)
*   `index` (number, optional): Sequential index of the reasoning detail

#### Reasoning Detail Types

**1. Summary Type (`reasoning.summary`)**

Contains a high-level summary of the reasoning process:

```json
{
  "type": "reasoning.summary",
  "summary": "The model analyzed the problem by first identifying key constraints, then evaluating possible solutions...",
  "id": "reasoning-summary-1",
  "format": "anthropic-claude-v1",
  "index": 0
}
```

**2. Encrypted Type (`reasoning.encrypted`)**

Contains encrypted reasoning data that may be redacted or protected:

```json
{
  "type": "reasoning.encrypted",
  "data": "eyJlbmNyeXB0ZWQiOiJ0cnVlIiwiY29udGVudCI6IltSRURBQ1RFRF0ifQ==",
  "id": "reasoning-encrypted-1",
  "format": "anthropic-claude-v1",
  "index": 1
}
```

**3. Text Type (`reasoning.text`)**

Contains raw text reasoning with optional signature verification:

```json
{
  "type": "reasoning.text",
  "text": "Let me think through this step by step:\n1. First, I need to understand the user's question...",
  "signature": "sha256:abc123def456...",
  "id": "reasoning-text-1",
  "format": "anthropic-claude-v1",
  "index": 2
}
```

#### Response Examples

**Non-Streaming Response**

In non-streaming responses, `reasoning_details` appears in the message:

```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Based on my analysis, I recommend the following approach...",
        "reasoning_details": [
          {
            "type": "reasoning.summary",
            "summary": "Analyzed the problem by breaking it into components",
            "id": "reasoning-summary-1",
            "format": "anthropic-claude-v1",
            "index": 0
          },
          {
            "type": "reasoning.text",
            "text": "Let me work through this systematically:\n1. First consideration...\n2. Second consideration...",
            "signature": null,
            "id": "reasoning-text-1",
            "format": "anthropic-claude-v1",
            "index": 1
          }
        ]
      }
    }
  ]
}
```

**Streaming Response**

In streaming responses, `reasoning_details` appears in delta chunks as the reasoning is generated:

```json
{
  "choices": [
    {
      "delta": {
        "reasoning_details": [
          {
            "type": "reasoning.text",
            "text": "Let me think about this step by step...",
            "signature": null,
            "id": "reasoning-text-1",
            "format": "anthropic-claude-v1",
            "index": 0
          }
        ]
      }
    }
  ]
}
```

**Streaming Behavior Notes:**

*   Each reasoning detail chunk is sent as it becomes available
*   The `reasoning_details` array in each chunk may contain one or more reasoning objects
*   For encrypted reasoning, the content may appear as `[REDACTED]` in streaming responses
*   The complete reasoning sequence is built by concatenating all chunks in order
