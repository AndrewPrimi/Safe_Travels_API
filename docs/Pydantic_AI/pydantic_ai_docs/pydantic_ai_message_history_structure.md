# PydanticAI Message History Structure - Complete Documentation

## Overview

The PydanticAI message history is a structured representation of the conversation between users, the AI agent, and tools. Understanding this structure is critical for building a summarization agent that maintains 1:1 compatibility with the expected format. This document provides exhaustive documentation of every aspect of the message format.

## Core Message Type Hierarchy

```
ModelMessage (Union)
├── ModelRequest
│   └── parts: list[ModelRequestPart]
│       ├── SystemPromptPart
│       ├── UserPromptPart
│       ├── ToolReturnPart
│       └── RetryPromptPart
└── ModelResponse
    └── parts: list[ModelResponsePart]
        ├── TextPart
        ├── ToolCallPart
        └── ThinkingPart
```

## Message Structure Details

### 1. ModelRequest

A request sent to the model containing a list of parts. Each request has the following structure:

```json
{
  "parts": [/* array of ModelRequestPart objects */],
  "instructions": null,  // Optional field, typically null
  "kind": "request"      // Literal identifier
}
```

#### 1.1 SystemPromptPart

Contains system-level instructions that guide the model's behavior.

```json
{
  "content": "string",           // The system prompt text
  "timestamp": "2025-06-26T18:10:48.672781Z",  // ISO format with microseconds
  "dynamic_ref": null,          // Reference to dynamic prompt function (usually null)
  "part_kind": "system-prompt"  // Literal identifier
}
```

**Key characteristics:**
- Always appears first in the initial ModelRequest
- `timestamp` uses ISO 8601 format with UTC timezone (Z suffix)
- Microsecond precision is preserved in timestamps

#### 1.2 UserPromptPart

Contains the user's input message.

```json
{
  "content": "string or array",  // User input (can be multimodal)
  "timestamp": "2025-06-26T18:10:48.672785Z",
  "part_kind": "user-prompt"
}
```

**Important notes:**
- `content` can be a string or array of UserContent objects for multimodal input
- Multiple UserPromptParts can exist in a single ModelRequest

#### 1.3 ToolReturnPart

Contains the result from a tool execution.

```json
{
  "tool_name": "deep_research",
  "content": ["array of strings"] or object,  // Tool output
  "tool_call_id": "tool_0_deep_research",     // Unique identifier
  "timestamp": "2025-06-26T18:11:05.464382Z",
  "part_kind": "tool-return"
}
```

**Critical details:**
- `content` format varies by tool (array for deep_research, objects for others)
- `tool_call_id` must match the corresponding ToolCallPart
- Tool returns are what need summarization while preserving structure

#### 1.4 RetryPromptPart

Used when the model needs to retry after an error.

```json
{
  "content": "string or array",  // Error details
  "tool_name": "optional_string",
  "tool_call_id": "string",
  "timestamp": "2025-06-26T18:11:05.464382Z",
  "part_kind": "retry-prompt"
}
```

### 2. ModelResponse

A response from the model containing its generated content.

```json
{
  "parts": [/* array of ModelResponsePart objects */],
  "usage": {
    "requests": 1,
    "request_tokens": 3516,
    "response_tokens": 923,
    "total_tokens": 4439,
    "details": {}
  },
  "model_name": "google/gemini-2.5-pro",
  "timestamp": "2025-06-26T18:10:48Z",
  "kind": "response",
  "vendor_details": null,
  "vendor_id": "gen-1750961448-uXAbqwVOdf0VWnGjScMT"
}
```

#### 2.1 TextPart

Plain text response from the model.

```json
{
  "content": "string",
  "part_kind": "text"
}
```

**Notes:**
- Can be empty string
- Multiple TextParts may exist in a single response

#### 2.2 ToolCallPart

Represents the model's request to execute a tool.

```json
{
  "tool_name": "deep_research",
  "args": "{\"date_filter\":true,\"start_date\":\"2025-01-01\",\"prompt\":\"most active threat actor groups\"}",
  "tool_call_id": "tool_0_deep_research",
  "part_kind": "tool-call"
}
```

**Critical details:**
- `args` is a JSON string (not object) - must be string-encoded
- `tool_call_id` follows pattern: `tool_{index}_{tool_name}`
- Multiple tool calls can exist in a single response

#### 2.3 ThinkingPart

Contains the model's reasoning process (primarily for o1-style models).

```json
{
  "content": "string",
  "id": "optional_string",
  "signature": "optional_string",  // Anthropic models only
  "part_kind": "thinking"
}
```

## Message Ordering and Relationships

### Typical Conversation Flow

1. **Initial Request**:
   - SystemPromptPart (first message only)
   - UserPromptPart

2. **Model Response**:
   - TextPart (optional introduction)
   - ToolCallPart(s) (if tools needed)
   - TextPart (if direct response)

3. **Tool Results** (new ModelRequest):
   - ToolReturnPart(s) matching previous ToolCallParts

4. **Final Response**:
   - TextPart with synthesized information

### Example Message Sequence from Real Output

```json
[
  {
    "parts": [
      {"part_kind": "system-prompt", ...},
      {"part_kind": "user-prompt", ...}
    ],
    "kind": "request"
  },
  {
    "parts": [
      {"part_kind": "text", "content": "I'll help with that..."},
      {"part_kind": "tool-call", "tool_name": "deep_research", ...},
      {"part_kind": "tool-call", "tool_name": "deep_research", ...}
    ],
    "kind": "response"
  },
  {
    "parts": [
      {"part_kind": "tool-return", "tool_name": "deep_research", ...},
      {"part_kind": "tool-return", "tool_name": "deep_research", ...}
    ],
    "kind": "request"
  },
  {
    "parts": [
      {"part_kind": "text", "content": "Based on my research..."}
    ],
    "kind": "response"
  }
]
```

## Serialization Requirements

### JSON Conversion

When converting to JSON using `to_jsonable_python`:
- All datetime objects become ISO 8601 strings
- All objects become dictionaries
- Enums/literals become their string values
- None values are preserved as null

### Required Field Preservation

**NEVER modify or omit these fields:**
- All `part_kind` identifiers
- All `tool_call_id` values (must maintain exact matching)
- All `timestamp` values (including microsecond precision)
- The `kind` field on messages
- Model usage statistics structure

## Validation Rules

### Structural Validation

1. **Message Alternation**: 
   - Messages should alternate between "request" and "response"
   - Exception: Consecutive requests can occur with tool returns

2. **Part Type Constraints**:
   - ModelRequest can only contain: SystemPromptPart, UserPromptPart, ToolReturnPart, RetryPromptPart
   - ModelResponse can only contain: TextPart, ToolCallPart, ThinkingPart

3. **Tool Call/Return Matching**:
   - Every ToolCallPart must have a corresponding ToolReturnPart
   - `tool_call_id` must match exactly between call and return
   - Tool name must match between call and return

### Content Validation

1. **Tool Arguments**:
   - Must be valid JSON when parsed
   - Must match expected schema for the tool

2. **Timestamps**:
   - Must be valid ISO 8601 format
   - Must include timezone (Z for UTC)
   - Should preserve microsecond precision

## Special Considerations for Summarization

### What Must Be Preserved Exactly

1. **Message Structure**:
   - The alternating request/response pattern
   - All part_kind values
   - All metadata fields

2. **Tool Relationships**:
   - tool_call_id matching between calls and returns
   - Tool names
   - Argument structure (even if content is summarized)

3. **Non-Tool Content**:
   - System prompts (never modify)
   - User prompts (never modify)
   - Assistant text responses (never modify)
   - All model metadata and usage statistics

### What Can Be Summarized

Only the `content` field of ToolReturnPart objects can be summarized, with these constraints:

1. **Maintain Type Consistency**:
   - If original is array, summary must be array
   - If original is object, summary must be object

2. **Preserve Referenced Information**:
   - Any data mentioned in subsequent TextPart responses
   - Key identifiers (IPs, domains, threat actor names)
   - Critical findings (high-risk indicators, active threats)

3. **Structure Preservation**:
   - For arrays: Can reduce number of elements but maintain array structure
   - For objects: Must maintain all keys present, can summarize values

## Undocumented Fields Discovered

### Additional ModelRequest Fields
- `dynamic_ref`: Present in all message parts, always `null` in observed data

### Additional ModelResponse Fields  
- `vendor_details`: Always `null` in observed data
- `vendor_id`: Unique identifier for each response (e.g., `"gen-1753814230-2KAVjzOkzr1bmp4Ccfdb"`)

## Tool Call ID Generation Pattern

The `tool_call_id` follows a strict pattern:
- Format: `tool_{index}_{tool_name}`
- Index starts at 0 and increments for each tool call in the response
- Examples from actual data:
  - `tool_0_explore`
  - `tool_1_get_indicator_details`
  - `tool_2_get_indicator_details`
  - `tool_20_deep_research` (when many parallel calls)

## Example: Tool Return Summarization

### Original Tool Return
```json
{
  "tool_name": "deep_research",
  "content": [
    "Long article about APT28 activities including...", 
    "Another article with redundant information...",
    "Third article with minor details...",
    // ... 10 more entries
  ],
  "tool_call_id": "tool_0_deep_research",
  "timestamp": "2025-06-26T18:11:05.464382Z",
  "part_kind": "tool-return"
}
```

### Summarized Version
```json
{
  "tool_name": "deep_research",
  "content": [
    "APT28 (Fancy Bear) remains highly active in 2025, targeting NATO states with HATVIBE malware and ClickFix attacks. Key findings: [consolidated information from all articles]"
  ],
  "tool_call_id": "tool_0_deep_research",
  "timestamp": "2025-06-26T18:11:05.464382Z",
  "part_kind": "tool-return"
}
```

## Error Handling Patterns

### ModelRetry Structure
When errors occur, the system adds a RetryPromptPart:
```json
{
  "parts": [
    {
      "content": "Error details or retry instructions",
      "tool_name": "get_indicator_details",
      "tool_call_id": "tool_0_get_indicator_details", 
      "timestamp": "2025-06-26T18:11:05.464382Z",
      "part_kind": "retry-prompt"
    }
  ],
  "kind": "request"
}
```

## Implementation Guidelines

1. **Parser Requirements**:
   - Must handle both string and array content types
   - Must preserve all metadata exactly
   - Must maintain message ordering

2. **Serialization Requirements**:
   - Use `to_jsonable_python` for conversion
   - Maintain exact field names (including underscores)
   - Preserve null vs missing field distinction

3. **Validation Steps**:
   - Verify message type alternation
   - Check tool call/return ID matching
   - Ensure all required fields present
   - Validate timestamp formats

## Common Pitfalls to Avoid

Based on actual test data analysis:

1. **Timestamp Format Mismatch**
   - Message parts use microsecond precision with 'Z' suffix
   - Response messages use second precision with 'Z' suffix
   - Never mix formats or lose precision

2. **Tool Call ID Misalignment**
   - IDs must match EXACTLY between call and return
   - Index must increment properly (0, 1, 2...)
   - Format must be `tool_{index}_{tool_name}`

3. **Content Type Violations**
   - If original is array, summary MUST be array
   - If original is object, summary MUST be object
   - Never change the fundamental data type

4. **Missing Required Fields**
   - Every field shown in examples is required
   - `null` values must be preserved as `null`
   - Empty arrays/objects are valid and must be preserved

5. **Message Ordering Errors**
   - Tool returns must follow tool calls
   - Cannot have response without request
   - System prompt only in first message

## Validation Checklist

Before deploying summarized message history:

- [ ] All `part_kind` values are valid literals
- [ ] All `kind` values are either "request" or "response"
- [ ] Tool call IDs match between calls and returns
- [ ] Timestamps maintain original precision
- [ ] Content types match original structure
- [ ] Message alternation pattern is preserved
- [ ] All required fields are present
- [ ] No additional fields have been added
- [ ] JSON is valid and properly escaped

## PydanticAI Integration Requirements

The summarization agent must:
1. Use PydanticAI's `to_jsonable_python()` for serialization
2. Maintain exact field names (including underscores)
3. Preserve the Union type structure of ModelMessage
4. Ensure all datetime objects follow ISO 8601 format
5. Maintain the exact nesting structure

This structure MUST be maintained exactly for PydanticAI compatibility. Any deviation will break the agent's ability to process the message history.