OpenAI
Install
To use OpenAI models or OpenAI-compatible APIs, you need to either install pydantic-ai, or install pydantic-ai-slim with the openai optional group:


pip
uv

pip install "pydantic-ai-slim[openai]"

Configuration
To use OpenAIChatModel with the OpenAI API, go to platform.openai.com and follow your nose until you find the place to generate an API key.

Environment variable
Once you have the API key, you can set it as an environment variable:


export OPENAI_API_KEY='your-api-key'
You can then use OpenAIChatModel by name:


from pydantic_ai import Agent

agent = Agent('openai:gpt-4o')
...
Or initialise the model directly with just the model name:


from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel

model = OpenAIChatModel('gpt-4o')
agent = Agent(model)
...
By default, the OpenAIChatModel uses the OpenAIProvider with the base_url set to https://api.openai.com/v1.

Configure the provider
If you want to pass parameters in code to the provider, you can programmatically instantiate the OpenAIProvider and pass it to the model:


from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIChatModel('gpt-4o', provider=OpenAIProvider(api_key='your-api-key'))
agent = Agent(model)
...
Custom OpenAI Client
OpenAIProvider also accepts a custom AsyncOpenAI client via the openai_client parameter, so you can customise the organization, project, base_url etc. as defined in the OpenAI API docs.

custom_openai_client.py

from openai import AsyncOpenAI

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

client = AsyncOpenAI(max_retries=3)
model = OpenAIChatModel('gpt-4o', provider=OpenAIProvider(openai_client=client))
agent = Agent(model)
...
You could also use the AsyncAzureOpenAI client to use the Azure OpenAI API. Note that the AsyncAzureOpenAI is a subclass of AsyncOpenAI.


from openai import AsyncAzureOpenAI

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

client = AsyncAzureOpenAI(
    azure_endpoint='...',
    api_version='2024-07-01-preview',
    api_key='your-api-key',
)

model = OpenAIChatModel(
    'gpt-4o',
    provider=OpenAIProvider(openai_client=client),
)
agent = Agent(model)
...
OpenAI Responses API
Pydantic AI also supports OpenAI's Responses API through the OpenAIResponsesModel class.


from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel

model = OpenAIResponsesModel('gpt-4o')
agent = Agent(model)
...
You can learn more about the differences between the Responses API and Chat Completions API in the OpenAI API docs.

Built-in tools
The Responses API has built-in tools that you can use instead of building your own:

Web search: allow models to search the web for the latest information before generating a response.
Code interpreter: allow models to write and run Python code in a sandboxed environment before generating a response.
File search: allow models to search your files for relevant information before generating a response.
Computer use: allow models to use a computer to perform tasks on your behalf.
Image generation: allow models to generate images based on a text prompt.
Web search and Code interpreter are natively supported through the Built-in tools feature.

Image generation is not currently supported. If you need this feature, please comment on this issue.

File search and Computer use can be enabled by passing an openai.types.responses.FileSearchToolParam or openai.types.responses.ComputerToolParam in the openai_builtin_tools setting on OpenAIResponsesModelSettings. They don't currently generate BuiltinToolCallPart or BuiltinToolReturnPart parts in the message history, or streamed events; please submit an issue if you need native support for these built-in tools.

file_search_tool.py

from openai.types.responses import FileSearchToolParam

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model_settings = OpenAIResponsesModelSettings(
    openai_builtin_tools=[
        FileSearchToolParam(
            type='file_search',
            vector_store_ids=['your-history-book-vector-store-id']
        )
    ],
)
model = OpenAIResponsesModel('gpt-4o')
agent = Agent(model=model, model_settings=model_settings)

result = agent.run_sync('Who was Albert Einstein?')
print(result.output)
#> Albert Einstein was a German-born theoretical physicist.
Referencing earlier responses
The Responses API supports referencing earlier model responses in a new request using a previous_response_id parameter, to ensure the full conversation state including reasoning items are kept in context. This is available through the openai_previous_response_id field in OpenAIResponsesModelSettings.


from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-5')
agent = Agent(model=model)

result = agent.run_sync('The secret is 1234')
model_settings = OpenAIResponsesModelSettings(
    openai_previous_response_id=result.all_messages()[-1].provider_response_id
)
result = agent.run_sync('What is the secret code?', model_settings=model_settings)
print(result.output)
#> 1234
By passing the provider_response_id from an earlier run, you can allow the model to build on its own prior reasoning without needing to resend the full message history.

Automatically referencing earlier responses
When the openai_previous_response_id field is set to 'auto', Pydantic AI will automatically select the most recent provider_response_id from message history and omit messages that came before it, letting the OpenAI API leverage server-side history instead for improved efficiency.


from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-5')
agent = Agent(model=model)

result1 = agent.run_sync('Tell me a joke.')
print(result1.output)
#> Did you hear about the toothpaste scandal? They called it Colgate.

# When set to 'auto', the most recent provider_response_id
# and messages after it are sent as request.
model_settings = OpenAIResponsesModelSettings(openai_previous_response_id='auto')
result2 = agent.run_sync(
    'Explain?',
    message_history=result1.new_messages(),
    model_settings=model_settings
)
print(result2.output)
#> This is an excellent joke invented by Samuel Colvin, it needs no explanation.
OpenAI-compatible Models
Many providers and models are compatible with the OpenAI API, and can be used with OpenAIChatModel in Pydantic AI. Before getting started, check the installation and configuration instructions above.

To use another OpenAI-compatible API, you can make use of the base_url and api_key arguments from OpenAIProvider:


from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIChatModel(
    'model_name',
    provider=OpenAIProvider(
        base_url='https://<openai-compatible-api-endpoint>.com', api_key='your-api-key'
    ),
)
agent = Agent(model)
...
Various providers also have their own provider classes so that you don't need to specify the base URL yourself and you can use the standard <PROVIDER>_API_KEY environment variable to set the API key. When a provider has its own provider class, you can use the Agent("<provider>:<model>") shorthand, e.g. Agent("deepseek:deepseek-chat") or Agent("openrouter:google/gemini-2.5-pro-preview"), instead of building the OpenAIChatModel explicitly. Similarly, you can pass the provider name as a string to the provider argument on OpenAIChatModel instead of building instantiating the provider class explicitly.

Model Profile
Sometimes, the provider or model you're using will have slightly different requirements than OpenAI's API or models, like having different restrictions on JSON schemas for tool definitions, or not supporting tool definitions to be marked as strict.

When using an alternative provider class provided by Pydantic AI, an appropriate model profile is typically selected automatically based on the model name. If the model you're using is not working correctly out of the box, you can tweak various aspects of how model requests are constructed by providing your own ModelProfile (for behaviors shared among all model classes) or OpenAIModelProfile (for behaviors specific to OpenAIChatModel):


from pydantic_ai import Agent, InlineDefsJsonSchemaTransformer
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.profiles.openai import OpenAIModelProfile
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIChatModel(
    'model_name',
    provider=OpenAIProvider(
        base_url='https://<openai-compatible-api-endpoint>.com', api_key='your-api-key'
    ),
    profile=OpenAIModelProfile(
        json_schema_transformer=InlineDefsJsonSchemaTransformer,  # Supported by any model class on a plain ModelProfile
        openai_supports_strict_tool_definition=False  # Supported by OpenAIModel only, requires OpenAIModelProfile
    )
)
agent = Agent(model)
DeepSeek
To use the DeepSeek provider, first create an API key by following the Quick Start guide. Once you have the API key, you can use it with the DeepSeekProvider:


from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.deepseek import DeepSeekProvider

model = OpenAIChatModel(
    'deepseek-chat',
    provider=DeepSeekProvider(api_key='your-deepseek-api-key'),
)
agent = Agent(model)
...
You can also customize any provider with a custom http_client:


from httpx import AsyncClient

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.deepseek import DeepSeekProvider

custom_http_client = AsyncClient(timeout=30)
model = OpenAIChatModel(
    'deepseek-chat',
    provider=DeepSeekProvider(
        api_key='your-deepseek-api-key', http_client=custom_http_client
    ),
)
agent = Agent(model)
...
Ollama
Pydantic AI supports both self-hosted Ollama servers (running locally or remotely) and Ollama Cloud through the OllamaProvider.

The API URL and optional API key can be provided to the OllamaProvider using the base_url and api_key arguments, or the OLLAMA_BASE_URL and OLLAMA_API_KEY environment variables.

For servers running locally, use the http://localhost:11434/v1 base URL. For Ollama Cloud, use https://ollama.com/v1 and ensure an API key is set.


from pydantic import BaseModel

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider


class CityLocation(BaseModel):
    city: str
    country: str


ollama_model = OpenAIChatModel(
    model_name='gpt-oss:20b',
    provider=OllamaProvider(base_url='http://localhost:11434/v1'),  
)
agent = Agent(ollama_model, output_type=CityLocation)

result = agent.run_sync('Where were the olympics held in 2012?')
print(result.output)
#> city='London' country='United Kingdom'
print(result.usage())
#> RunUsage(input_tokens=57, output_tokens=8, requests=1)
Azure AI Foundry
If you want to use Azure AI Foundry as your provider, you can do so by using the AzureProvider class.


from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider

model = OpenAIChatModel(
    'gpt-4o',
    provider=AzureProvider(
        azure_endpoint='your-azure-endpoint',
        api_version='your-api-version',
        api_key='your-api-key',
    ),
)
agent = Agent(model)
...
OpenRouter
To use OpenRouter, first create an API key at openrouter.ai/keys.

Once you have the API key, you can use it with the OpenRouterProvider:


from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

model = OpenAIChatModel(
    'anthropic/claude-3.5-sonnet',
    provider=OpenRouterProvider(api_key='your-openrouter-api-key'),
)
agent = Agent(model)
...
Vercel AI Gateway
To use Vercel's AI Gateway, first follow the documentation instructions on obtaining an API key or OIDC token.

You can set your credentials using one of these environment variables:


export VERCEL_AI_GATEWAY_API_KEY='your-ai-gateway-api-key'
# OR
export VERCEL_OIDC_TOKEN='your-oidc-token'
Once you have set the environment variable, you can use it with the VercelProvider:


from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.vercel import VercelProvider

# Uses environment variable automatically
model = OpenAIChatModel(
    'anthropic/claude-4-sonnet',
    provider=VercelProvider(),
)
agent = Agent(model)

# Or pass the API key directly
model = OpenAIChatModel(
    'anthropic/claude-4-sonnet',
    provider=VercelProvider(api_key='your-vercel-ai-gateway-api-key'),
)
agent = Agent(model)
...
Grok (xAI)
Go to xAI API Console and create an API key. Once you have the API key, you can use it with the GrokProvider:


from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.grok import GrokProvider

model = OpenAIChatModel(
    'grok-2-1212',
    provider=GrokProvider(api_key='your-xai-api-key'),
)
agent = Agent(model)
...
MoonshotAI
Create an API key in the Moonshot Console. With that key you can instantiate the MoonshotAIProvider:


from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.moonshotai import MoonshotAIProvider

model = OpenAIChatModel(
    'kimi-k2-0711-preview',
    provider=MoonshotAIProvider(api_key='your-moonshot-api-key'),
)
agent = Agent(model)
...
GitHub Models
To use GitHub Models, you'll need a GitHub personal access token with the models: read permission.

Once you have the token, you can use it with the GitHubProvider:


from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.github import GitHubProvider

model = OpenAIChatModel(
    'xai/grok-3-mini',  # GitHub Models uses prefixed model names
    provider=GitHubProvider(api_key='your-github-token'),
)
agent = Agent(model)
...
You can also set the GITHUB_API_KEY environment variable:


export GITHUB_API_KEY='your-github-token'
GitHub Models supports various model families with different prefixes. You can see the full list on the GitHub Marketplace or the public catalog endpoint.

Perplexity
Follow the Perplexity getting started guide to create an API key. Then, you can query the Perplexity API with the following:


from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIChatModel(
    'sonar-pro',
    provider=OpenAIProvider(
        base_url='https://api.perplexity.ai',
        api_key='your-perplexity-api-key',
    ),
)
agent = Agent(model)
...
Fireworks AI
Go to Fireworks.AI and create an API key in your account settings. Once you have the API key, you can use it with the FireworksProvider:


from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.fireworks import FireworksProvider

model = OpenAIChatModel(
    'accounts/fireworks/models/qwq-32b',  # model library available at https://fireworks.ai/models
    provider=FireworksProvider(api_key='your-fireworks-api-key'),
)
agent = Agent(model)
...
Together AI
Go to Together.ai and create an API key in your account settings. Once you have the API key, you can use it with the TogetherProvider:


from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.together import TogetherProvider

model = OpenAIChatModel(
    'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free',  # model library available at https://www.together.ai/models
    provider=TogetherProvider(api_key='your-together-api-key'),
)
agent = Agent(model)
...
Heroku AI
To use Heroku AI, you can use the HerokuProvider:


from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.heroku import HerokuProvider

model = OpenAIChatModel(
    'claude-3-7-sonnet',
    provider=HerokuProvider(api_key='your-heroku-inference-key'),
)
agent = Agent(model)
...
You can set the HEROKU_INFERENCE_KEY and HEROKU_INFERENCE_URL environment variables to set the API key and base URL, respectively:


export HEROKU_INFERENCE_KEY='your-heroku-inference-key'
export HEROKU_INFERENCE_URL='https://us.inference.heroku.com'
Cerebras
To use Cerebras, you need to create an API key in the Cerebras Console.

Once you've set the CEREBRAS_API_KEY environment variable, you can run the following:


from pydantic_ai import Agent

agent = Agent('cerebras:llama3.3-70b')
result = agent.run_sync('What is the capital of France?')
print(result.output)
#> The capital of France is Paris.
If you need to configure the provider, you can use the CerebrasProvider class:


from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.cerebras import CerebrasProvider

model = OpenAIChatModel(
    'llama3.3-70b',
    provider=CerebrasProvider(api_key='your-cerebras-api-key'),
)
agent = Agent(model)

result = agent.run_sync('What is the capital of France?')
print(result.output)
#> The capital of France is Paris.
LiteLLM
To use LiteLLM, set the configs as outlined in the doc. In LiteLLMProvider, you can pass api_base and api_key. The value of these configs will depend on your setup. For example, if you are using OpenAI models, then you need to pass https://api.openai.com/v1 as the api_base and your OpenAI API key as the api_key. If you are using a LiteLLM proxy server running on your local machine, then you need to pass http://localhost:<port> as the api_base and your LiteLLM API key (or a placeholder) as the api_key.

To use custom LLMs, use custom/ prefix in the model name.

Once you have the configs, use the LiteLLMProvider as follows:


from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.litellm import LiteLLMProvider

model = OpenAIChatModel(
    'openai/gpt-3.5-turbo',
    provider=LiteLLMProvider(
        api_base='<api-base-url>',
        api_key='<api-key>'
    )
)
agent = Agent(model)

result = agent.run_sync('What is the capital of France?')
print(result.output)
#> The capital of France is Paris.