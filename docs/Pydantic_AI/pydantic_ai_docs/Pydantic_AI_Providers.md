pydantic_ai.providers
Bases: ABC, Generic[InterfaceClient]

Abstract class for a provider.

The provider is in charge of providing an authenticated client to the API.

Each provider only supports a specific interface. A interface can be supported by multiple providers.

For example, the OpenAIChatModel interface can be supported by the OpenAIProvider and the DeepSeekProvider.

Source code in pydantic_ai_slim/pydantic_ai/providers/__init__.py
name abstractmethod property

name: str
The provider name.

base_url abstractmethod property

base_url: str
The base URL for the provider API.

client abstractmethod property

client: InterfaceClient
The client for the provider.

model_profile

model_profile(model_name: str) -> ModelProfile | None
The model profile for the named model, if available.

Source code in pydantic_ai_slim/pydantic_ai/providers/__init__.py
GoogleProvider
Bases: Provider[Client]

Provider for Google.

Source code in pydantic_ai_slim/pydantic_ai/providers/google.py
__init__

__init__(*, api_key: str) -> None

__init__(
    *,
    credentials: Credentials | None = None,
    project: str | None = None,
    location: (
        VertexAILocation | Literal["global"] | None
    ) = None
) -> None

__init__(*, client: Client) -> None

__init__(*, vertexai: bool = False) -> None

__init__(
    *,
    api_key: str | None = None,
    credentials: Credentials | None = None,
    project: str | None = None,
    location: (
        VertexAILocation | Literal["global"] | None
    ) = None,
    client: Client | None = None,
    vertexai: bool | None = None
) -> None
Create a new Google provider.

Parameters:

Name	Type	Description	Default
api_key	str | None	The API key <https://ai.google.dev/gemini-api/docs/api-key>_ to use for authentication. It can also be set via the GOOGLE_API_KEY environment variable. Applies to the Gemini Developer API only.	None
credentials	Credentials | None	The credentials to use for authentication when calling the Vertex AI APIs. Credentials can be obtained from environment variables and default credentials. For more information, see Set up Application Default Credentials. Applies to the Vertex AI API only.	None
project	str | None	The Google Cloud project ID to use for quota. Can be obtained from environment variables (for example, GOOGLE_CLOUD_PROJECT). Applies to the Vertex AI API only.	None
location	VertexAILocation | Literal['global'] | None	The location to send API requests to (for example, us-central1). Can be obtained from environment variables. Applies to the Vertex AI API only.	None
client	Client | None	A pre-initialized client to use.	None
vertexai	bool | None	Force the use of the Vertex AI API. If False, the Google Generative Language API will be used. Defaults to False.	None
Source code in pydantic_ai_slim/pydantic_ai/providers/google.py
VertexAILocation module-attribute

VertexAILocation = Literal[
    "asia-east1",
    "asia-east2",
    "asia-northeast1",
    "asia-northeast3",
    "asia-south1",
    "asia-southeast1",
    "australia-southeast1",
    "europe-central2",
    "europe-north1",
    "europe-southwest1",
    "europe-west1",
    "europe-west2",
    "europe-west3",
    "europe-west4",
    "europe-west6",
    "europe-west8",
    "europe-west9",
    "me-central1",
    "me-central2",
    "me-west1",
    "northamerica-northeast1",
    "southamerica-east1",
    "us-central1",
    "us-east1",
    "us-east4",
    "us-east5",
    "us-south1",
    "us-west1",
    "us-west4",
]
Regions available for Vertex AI. More details here.

OpenAIProvider
Bases: Provider[AsyncOpenAI]

Provider for OpenAI API.

Source code in pydantic_ai_slim/pydantic_ai/providers/openai.py
__init__

__init__(*, openai_client: AsyncOpenAI) -> None

__init__(
    base_url: str | None = None,
    api_key: str | None = None,
    openai_client: None = None,
    http_client: AsyncClient | None = None,
) -> None

__init__(
    base_url: str | None = None,
    api_key: str | None = None,
    openai_client: AsyncOpenAI | None = None,
    http_client: AsyncClient | None = None,
) -> None
Create a new OpenAI provider.

Parameters:

Name	Type	Description	Default
base_url	str | None	The base url for the OpenAI requests. If not provided, the OPENAI_BASE_URL environment variable will be used if available. Otherwise, defaults to OpenAI's base url.	None
api_key	str | None	The API key to use for authentication, if not provided, the OPENAI_API_KEY environment variable will be used if available.	None
openai_client	AsyncOpenAI | None	An existing AsyncOpenAI client to use. If provided, base_url, api_key, and http_client must be None.	None
http_client	AsyncClient | None	An existing httpx.AsyncClient to use for making HTTP requests.	None
Source code in pydantic_ai_slim/pydantic_ai/providers/openai.py
DeepSeekProvider
Bases: Provider[AsyncOpenAI]

Provider for DeepSeek API.

Source code in pydantic_ai_slim/pydantic_ai/providers/deepseek.py
BedrockModelProfile dataclass
Bases: ModelProfile

Profile for models used with BedrockModel.

ALL FIELDS MUST BE bedrock_ PREFIXED SO YOU CAN MERGE THEM WITH OTHER MODELS.

Source code in pydantic_ai_slim/pydantic_ai/providers/bedrock.py
bedrock_amazon_model_profile

bedrock_amazon_model_profile(
    model_name: str,
) -> ModelProfile | None
Get the model profile for an Amazon model used via Bedrock.

Source code in pydantic_ai_slim/pydantic_ai/providers/bedrock.py
bedrock_deepseek_model_profile

bedrock_deepseek_model_profile(
    model_name: str,
) -> ModelProfile | None
Get the model profile for a DeepSeek model used via Bedrock.

Source code in pydantic_ai_slim/pydantic_ai/providers/bedrock.py
BedrockProvider
Bases: Provider[BaseClient]

Provider for AWS Bedrock.

Source code in pydantic_ai_slim/pydantic_ai/providers/bedrock.py
__init__

__init__(*, bedrock_client: BaseClient) -> None

__init__(
    *,
    region_name: str | None = None,
    aws_access_key_id: str | None = None,
    aws_secret_access_key: str | None = None,
    aws_session_token: str | None = None,
    profile_name: str | None = None,
    aws_read_timeout: float | None = None,
    aws_connect_timeout: float | None = None
) -> None

__init__(
    *,
    bedrock_client: BaseClient | None = None,
    region_name: str | None = None,
    aws_access_key_id: str | None = None,
    aws_secret_access_key: str | None = None,
    aws_session_token: str | None = None,
    profile_name: str | None = None,
    aws_read_timeout: float | None = None,
    aws_connect_timeout: float | None = None
) -> None
Initialize the Bedrock provider.

Parameters:

Name	Type	Description	Default
bedrock_client	BaseClient | None	A boto3 client for Bedrock Runtime. If provided, other arguments are ignored.	None
region_name	str | None	The AWS region name.	None
aws_access_key_id	str | None	The AWS access key ID.	None
aws_secret_access_key	str | None	The AWS secret access key.	None
aws_session_token	str | None	The AWS session token.	None
profile_name	str | None	The AWS profile name.	None
aws_read_timeout	float | None	The read timeout for Bedrock client.	None
aws_connect_timeout	float | None	The connect timeout for Bedrock client.	None
Source code in pydantic_ai_slim/pydantic_ai/providers/bedrock.py
groq_moonshotai_model_profile

groq_moonshotai_model_profile(
    model_name: str,
) -> ModelProfile | None
Get the model profile for an MoonshotAI model used with the Groq provider.

Source code in pydantic_ai_slim/pydantic_ai/providers/groq.py
meta_groq_model_profile

meta_groq_model_profile(
    model_name: str,
) -> ModelProfile | None
Get the model profile for a Meta model used with the Groq provider.

Source code in pydantic_ai_slim/pydantic_ai/providers/groq.py
GroqProvider
Bases: Provider[AsyncGroq]

Provider for Groq API.

Source code in pydantic_ai_slim/pydantic_ai/providers/groq.py
__init__

__init__(*, groq_client: AsyncGroq | None = None) -> None

__init__(
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    http_client: AsyncClient | None = None
) -> None

__init__(
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    groq_client: AsyncGroq | None = None,
    http_client: AsyncClient | None = None
) -> None
Create a new Groq provider.

Parameters:

Name	Type	Description	Default
api_key	str | None	The API key to use for authentication, if not provided, the GROQ_API_KEY environment variable will be used if available.	None
base_url	str | None	The base url for the Groq requests. If not provided, the GROQ_BASE_URL environment variable will be used if available. Otherwise, defaults to Groq's base url.	None
groq_client	AsyncGroq | None	An existing AsyncGroq client to use. If provided, api_key and http_client must be None.	None
http_client	AsyncClient | None	An existing AsyncHTTPClient to use for making HTTP requests.	None
Source code in pydantic_ai_slim/pydantic_ai/providers/groq.py
AzureProvider
Bases: Provider[AsyncOpenAI]

Provider for Azure OpenAI API.

See https://azure.microsoft.com/en-us/products/ai-foundry for more information.

Source code in pydantic_ai_slim/pydantic_ai/providers/azure.py
__init__

__init__(*, openai_client: AsyncAzureOpenAI) -> None

__init__(
    *,
    azure_endpoint: str | None = None,
    api_version: str | None = None,
    api_key: str | None = None,
    http_client: AsyncClient | None = None
) -> None

__init__(
    *,
    azure_endpoint: str | None = None,
    api_version: str | None = None,
    api_key: str | None = None,
    openai_client: AsyncAzureOpenAI | None = None,
    http_client: AsyncClient | None = None
) -> None
Create a new Azure provider.

Parameters:

Name	Type	Description	Default
azure_endpoint	str | None	The Azure endpoint to use for authentication, if not provided, the AZURE_OPENAI_ENDPOINT environment variable will be used if available.	None
api_version	str | None	The API version to use for authentication, if not provided, the OPENAI_API_VERSION environment variable will be used if available.	None
api_key	str | None	The API key to use for authentication, if not provided, the AZURE_OPENAI_API_KEY environment variable will be used if available.	None
openai_client	AsyncAzureOpenAI | None	An existing AsyncAzureOpenAI client to use. If provided, base_url, api_key, and http_client must be None.	None
http_client	AsyncClient | None	An existing httpx.AsyncClient to use for making HTTP requests.	None
Source code in pydantic_ai_slim/pydantic_ai/providers/azure.py
CohereProvider
Bases: Provider[AsyncClientV2]

Provider for Cohere API.

Source code in pydantic_ai_slim/pydantic_ai/providers/cohere.py
__init__

__init__(
    *,
    api_key: str | None = None,
    cohere_client: AsyncClientV2 | None = None,
    http_client: AsyncClient | None = None
) -> None
Create a new Cohere provider.

Parameters:

Name	Type	Description	Default
api_key	str | None	The API key to use for authentication, if not provided, the CO_API_KEY environment variable will be used if available.	None
cohere_client	AsyncClientV2 | None	An existing AsyncClientV2 client to use. If provided, api_key and http_client must be None.	None
http_client	AsyncClient | None	An existing httpx.AsyncClient to use for making HTTP requests.	None
Source code in pydantic_ai_slim/pydantic_ai/providers/cohere.py
Bases: Provider[AsyncOpenAI]

Provider for Cerebras API.

Source code in pydantic_ai_slim/pydantic_ai/providers/cerebras.py
Bases: Provider[Mistral]

Provider for Mistral API.

Source code in pydantic_ai_slim/pydantic_ai/providers/mistral.py
__init__

__init__(*, mistral_client: Mistral | None = None) -> None

__init__(
    *,
    api_key: str | None = None,
    http_client: AsyncClient | None = None
) -> None

__init__(
    *,
    api_key: str | None = None,
    mistral_client: Mistral | None = None,
    base_url: str | None = None,
    http_client: AsyncClient | None = None
) -> None
Create a new Mistral provider.

Parameters:

Name	Type	Description	Default
api_key	str | None	The API key to use for authentication, if not provided, the MISTRAL_API_KEY environment variable will be used if available.	None
mistral_client	Mistral | None	An existing Mistral client to use, if provided, api_key and http_client must be None.	None
base_url	str | None	The base url for the Mistral requests.	None
http_client	AsyncClient | None	An existing async client to use for making HTTP requests.	None
Source code in pydantic_ai_slim/pydantic_ai/providers/mistral.py
Bases: Provider[AsyncOpenAI]

Provider for Fireworks AI API.

Source code in pydantic_ai_slim/pydantic_ai/providers/fireworks.py
Bases: Provider[AsyncOpenAI]

Provider for Grok API.

Source code in pydantic_ai_slim/pydantic_ai/providers/grok.py
Bases: Provider[AsyncOpenAI]

Provider for Together AI API.

Source code in pydantic_ai_slim/pydantic_ai/providers/together.py
Bases: Provider[AsyncOpenAI]

Provider for Heroku API.

Source code in pydantic_ai_slim/pydantic_ai/providers/heroku.py
Bases: Provider[AsyncOpenAI]

Provider for GitHub Models API.

GitHub Models provides access to various AI models through an OpenAI-compatible API. See https://docs.github.com/en/github-models for more information.

Source code in pydantic_ai_slim/pydantic_ai/providers/github.py
__init__

__init__() -> None

__init__(*, api_key: str) -> None

__init__(*, api_key: str, http_client: AsyncClient) -> None

__init__(
    *, openai_client: AsyncOpenAI | None = None
) -> None

__init__(
    *,
    api_key: str | None = None,
    openai_client: AsyncOpenAI | None = None,
    http_client: AsyncClient | None = None
) -> None
Create a new GitHub Models provider.

Parameters:

Name	Type	Description	Default
api_key	str | None	The GitHub token to use for authentication. If not provided, the GITHUB_API_KEY environment variable will be used if available.	None
openai_client	AsyncOpenAI | None	An existing AsyncOpenAI client to use. If provided, api_key and http_client must be None.	None
http_client	AsyncClient | None	An existing httpx.AsyncClient to use for making HTTP requests.	None
Source code in pydantic_ai_slim/pydantic_ai/providers/github.py
Bases: Provider[AsyncOpenAI]

Provider for OpenRouter API.

Source code in pydantic_ai_slim/pydantic_ai/providers/openrouter.py
Bases: Provider[AsyncOpenAI]

Provider for Vercel AI Gateway API.

Source code in pydantic_ai_slim/pydantic_ai/providers/vercel.py
Bases: Provider[AsyncInferenceClient]

Provider for Hugging Face.

Source code in pydantic_ai_slim/pydantic_ai/providers/huggingface.py
__init__

__init__(
    *, base_url: str, api_key: str | None = None
) -> None

__init__(
    *, provider_name: str, api_key: str | None = None
) -> None

__init__(
    *,
    hf_client: AsyncInferenceClient,
    api_key: str | None = None
) -> None

__init__(
    *,
    hf_client: AsyncInferenceClient,
    base_url: str,
    api_key: str | None = None
) -> None

__init__(
    *,
    hf_client: AsyncInferenceClient,
    provider_name: str,
    api_key: str | None = None
) -> None

__init__(*, api_key: str | None = None) -> None

__init__(
    base_url: str | None = None,
    api_key: str | None = None,
    hf_client: AsyncInferenceClient | None = None,
    http_client: AsyncClient | None = None,
    provider_name: str | None = None,
) -> None
Create a new Hugging Face provider.

Parameters:

Name	Type	Description	Default
base_url	str | None	The base url for the Hugging Face requests.	None
api_key	str | None	The API key to use for authentication, if not provided, the HF_TOKEN environment variable will be used if available.	None
hf_client	AsyncInferenceClient | None	An existing AsyncInferenceClient client to use. If not provided, a new instance will be created.	None
http_client	AsyncClient | None	(currently ignored) An existing httpx.AsyncClient to use for making HTTP requests.	None
provider_name		Name of the provider to use for inference. available providers can be found in the HF Inference Providers documentation. defaults to "auto", which will select the first available provider for the model, the first of the providers available for the model, sorted by the user's order in https://hf.co/settings/inference-providers. If base_url is passed, then provider_name is not used.	None
Source code in pydantic_ai_slim/pydantic_ai/providers/huggingface.py
Bases: Provider[AsyncOpenAI]

Provider for MoonshotAI platform (Kimi models).

Source code in pydantic_ai_slim/pydantic_ai/providers/moonshotai.py
Bases: Provider[AsyncOpenAI]

Provider for local or remote Ollama API.

Source code in pydantic_ai_slim/pydantic_ai/providers/ollama.py
__init__

__init__(
    base_url: str | None = None,
    api_key: str | None = None,
    openai_client: AsyncOpenAI | None = None,
    http_client: AsyncClient | None = None,
) -> None
Create a new Ollama provider.

Parameters:

Name	Type	Description	Default
base_url	str | None	The base url for the Ollama requests. If not provided, the OLLAMA_BASE_URL environment variable will be used if available.	None
api_key	str | None	The API key to use for authentication, if not provided, the OLLAMA_API_KEY environment variable will be used if available.	None
openai_client	AsyncOpenAI | None	An existing AsyncOpenAI client to use. If provided, base_url, api_key, and http_client must be None.	None
http_client	AsyncClient | None	An existing httpx.AsyncClient to use for making HTTP requests.	None
Source code in pydantic_ai_slim/pydantic_ai/providers/ollama.py
Bases: Provider[AsyncOpenAI]

Provider for LiteLLM API.

Source code in pydantic_ai_slim/pydantic_ai/providers/litellm.py
__init__

__init__(
    *,
    api_key: str | None = None,
    api_base: str | None = None
) -> None

__init__(
    *,
    api_key: str | None = None,
    api_base: str | None = None,
    http_client: AsyncClient
) -> None

__init__(*, openai_client: AsyncOpenAI) -> None

__init__(
    *,
    api_key: str | None = None,
    api_base: str | None = None,
    openai_client: AsyncOpenAI | None = None,
    http_client: AsyncClient | None = None
) -> None
Initialize a LiteLLM provider.

Parameters:

Name	Type	Description	Default
api_key	str | None	API key for the model provider. If None, LiteLLM will try to get it from environment variables.	None
api_base	str | None	Base URL for the model provider. Use this for custom endpoints or self-hosted models.	None
openai_client	AsyncOpenAI | None	Pre-configured OpenAI client. If provided, other parameters are ignored.	None
http_client	AsyncClient | None	Custom HTTP client to use.	None
Source code in pydantic_ai_slim/pydantic_ai/providers/litellm.py