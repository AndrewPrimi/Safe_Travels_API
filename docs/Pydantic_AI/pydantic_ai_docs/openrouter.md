pydantic_ai.models.openrouter
Setup
For details on how to set up authentication with this model, see model configuration for OpenRouter.

KnownOpenRouterProviders module-attribute

KnownOpenRouterProviders = Literal[
    "z-ai",
    "cerebras",
    "venice",
    "moonshotai",
    "morph",
    "stealth",
    "wandb",
    "klusterai",
    "openai",
    "sambanova",
    "amazon-bedrock",
    "mistral",
    "nextbit",
    "atoma",
    "ai21",
    "minimax",
    "baseten",
    "anthropic",
    "featherless",
    "groq",
    "lambda",
    "azure",
    "ncompass",
    "deepseek",
    "hyperbolic",
    "crusoe",
    "cohere",
    "mancer",
    "avian",
    "perplexity",
    "novita",
    "siliconflow",
    "switchpoint",
    "xai",
    "inflection",
    "fireworks",
    "deepinfra",
    "inference-net",
    "inception",
    "atlas-cloud",
    "nvidia",
    "alibaba",
    "friendli",
    "infermatic",
    "targon",
    "ubicloud",
    "aion-labs",
    "liquid",
    "nineteen",
    "cloudflare",
    "nebius",
    "chutes",
    "enfer",
    "crofai",
    "open-inference",
    "phala",
    "gmicloud",
    "meta",
    "relace",
    "parasail",
    "together",
    "google-ai-studio",
    "google-vertex",
]
Known providers in the OpenRouter marketplace

OpenRouterProviderName module-attribute

OpenRouterProviderName = str | KnownOpenRouterProviders
Possible OpenRouter provider names.

Since OpenRouter is constantly updating their list of providers, we explicitly list some known providers but allow any name in the type hints. See the OpenRouter API for a full list.

OpenRouterTransforms module-attribute

OpenRouterTransforms = Literal['middle-out']
Available messages transforms for OpenRouter models with limited token windows.

Currently only supports 'middle-out', but is expected to grow in the future.

OpenRouterProviderConfig
Bases: TypedDict

Represents the 'Provider' object from the OpenRouter API.

Source code in pydantic_ai_slim/pydantic_ai/models/openrouter.py
order instance-attribute

order: list[OpenRouterProviderName]
List of provider slugs to try in order (e.g. ["anthropic", "openai"]). See details

allow_fallbacks instance-attribute

allow_fallbacks: bool
Whether to allow backup providers when the primary is unavailable. See details

require_parameters instance-attribute

require_parameters: bool
Only use providers that support all parameters in your request.

data_collection instance-attribute

data_collection: Literal['allow', 'deny']
Control whether to use providers that may store data. See details

zdr instance-attribute

zdr: bool
Restrict routing to only ZDR (Zero Data Retention) endpoints. See details

only instance-attribute

only: list[OpenRouterProviderName]
List of provider slugs to allow for this request. See details

ignore instance-attribute

ignore: list[str]
List of provider slugs to skip for this request. See details

quantizations instance-attribute

quantizations: list[
    Literal[
        "int4",
        "int8",
        "fp4",
        "fp6",
        "fp8",
        "fp16",
        "bf16",
        "fp32",
        "unknown",
    ]
]
List of quantization levels to filter by (e.g. ["int4", "int8"]). See details

sort instance-attribute

sort: Literal['price', 'throughput', 'latency']
Sort providers by price or throughput. (e.g. "price" or "throughput"). See details

max_price instance-attribute

max_price: _OpenRouterMaxPrice
The maximum pricing you want to pay for this request. See details

OpenRouterReasoning
Bases: TypedDict

Configuration for reasoning tokens in OpenRouter requests.

Reasoning tokens allow models to show their step-by-step thinking process. You can configure this using either OpenAI-style effort levels or Anthropic-style token limits, but not both simultaneously.

Source code in pydantic_ai_slim/pydantic_ai/models/openrouter.py
effort instance-attribute

effort: Literal['high', 'medium', 'low']
OpenAI-style reasoning effort level. Cannot be used with max_tokens.

max_tokens instance-attribute

max_tokens: int
Anthropic-style specific token limit for reasoning. Cannot be used with effort.

exclude instance-attribute

exclude: bool
Whether to exclude reasoning tokens from the response. Default is False. All models support this.

enabled instance-attribute

enabled: bool
Whether to enable reasoning with default parameters. Default is inferred from effort or max_tokens.

OpenRouterUsageConfig
Bases: TypedDict

Configuration for OpenRouter usage.

Source code in pydantic_ai_slim/pydantic_ai/models/openrouter.py
OpenRouterModelSettings
Bases: ModelSettings

Settings used for an OpenRouter model request.

Source code in pydantic_ai_slim/pydantic_ai/models/openrouter.py
openrouter_models instance-attribute

openrouter_models: list[str]
A list of fallback models.

These models will be tried, in order, if the main model returns an error. See details

openrouter_provider instance-attribute

openrouter_provider: OpenRouterProviderConfig
OpenRouter routes requests to the best available providers for your model. By default, requests are load balanced across the top providers to maximize uptime.

You can customize how your requests are routed using the provider object. See more

openrouter_preset instance-attribute

openrouter_preset: str
Presets allow you to separate your LLM configuration from your code.

Create and manage presets through the OpenRouter web application to control provider routing, model selection, system prompts, and other parameters, then reference them in OpenRouter API requests. See more

openrouter_transforms instance-attribute

openrouter_transforms: list[OpenRouterTransforms]
To help with prompts that exceed the maximum context size of a model.

Transforms work by removing or truncating messages from the middle of the prompt, until the prompt fits within the model's context window. See more

openrouter_reasoning instance-attribute

openrouter_reasoning: OpenRouterReasoning
To control the reasoning tokens in the request.

The reasoning config object consolidates settings for controlling reasoning strength across different models. See more

openrouter_usage instance-attribute

openrouter_usage: OpenRouterUsageConfig
To control the usage of the model.

The usage config object consolidates settings for enabling detailed usage information. See more

OpenRouterModel
Bases: OpenAIChatModel

Extends OpenAIModel to capture extra metadata for Openrouter.

Source code in pydantic_ai_slim/pydantic_ai/models/openrouter.py
__init__

__init__(
    model_name: str,
    *,
    provider: (
        Literal["openrouter"] | Provider[AsyncOpenAI]
    ) = "openrouter",
    profile: ModelProfileSpec | None = None,
    settings: ModelSettings | None = None
)
Initialize an OpenRouter model.

Parameters:

Name	Type	Description	Default
model_name	str	The name of the model to use.	required
provider	Literal['openrouter'] | Provider[AsyncOpenAI]	The provider to use for authentication and API access. If not provided, a new provider will be created with the default settings.	'openrouter'
profile	ModelProfileSpec | None	The model profile to use. Defaults to a profile picked by the provider based on the model name.	None
settings	ModelSettings | None	Model-specific settings that will be used as defaults for this model.	None
Source code in pydantic_ai_slim/pydantic_ai/models/openrouter.py
OpenRouterStreamedResponse dataclass
Bases: OpenAIStreamedResponse

Implementation of StreamedResponse for OpenRouter models.

Source code in pydantic_ai_slim/pydantic_ai/models/openrouter.py