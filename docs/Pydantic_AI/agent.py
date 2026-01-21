import os
import asyncio
from pydantic_ai import Agent
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIChatModel
from dotenv import load_dotenv
from pydantic_ai.mcp import MCPServerStreamableHTTP
# Load .env file from the same directory as this script
load_dotenv()

api_key = os.getenv('OPEN_ROUTER_API_KEY')
llm_model = os.getenv('LLM_MODEL', 'openai/gpt-3.5-turbo')  # Default model

if not api_key:
    print("ERROR: OPEN_ROUTER_API_KEY not found in environment variables!")
    print("Please create a .env file with your API key:")
    print("OPEN_ROUTER_API_KEY=your-api-key-here")
    print("LLM_MODEL=openai/gpt-3.5-turbo")
    exit(1)

model = OpenAIChatModel(
    llm_model,
    provider=OpenAIProvider(
        base_url='https://openrouter.ai/api/v1',
        api_key=api_key,
    ),
)

excel_mcp=MCPServerStreamableHTTP('http://localhost:8000/mcp')

example_agent = Agent(
    model=model,
    toolsets=excel_mcp
    system_prompt="you are a helpful excel agent...."
    "you have acess"
)


async def chat_loop():
    message_history = []
    
    print("Chat with the agent (type 'exit' to quit)")
    print("-" * 40)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Run the agent with message history
            if message_history:
                result = await example_agent.run(user_input, message_history=message_history)
            else:
                result = await example_agent.run(user_input)
            
            # Print the agent's response
            print(f"\nAgent: {result.output}")
            
            # Add new messages to history
            message_history.extend(result.new_messages())
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(chat_loop())