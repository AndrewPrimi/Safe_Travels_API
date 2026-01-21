# agent_zero.py

import os
import logging
import json
import httpx
from pydantic_core import to_jsonable_python
from pydantic_ai.messages import ModelMessagesTypeAdapter

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.mcp import MCPServerStreamableHTTP
from pydantic_ai.messages import ModelRequest, ToolReturnPart


import logfire
import asyncio

# -----------------------------------------------------------------------------
# Setup: Load environment variables and configure logging
# -----------------------------------------------------------------------------
load_dotenv()

# Configure logfire only if not disabled
logfire_token = os.getenv('LOGFIRE', '').lower()
if logfire_token != 'disabled':
    logfire.configure(scrubbing=False)
    logfire.instrument_openai()

# Configure a logger for this module
logger = logging.getLogger(__name__)

# Access environment variables
llm_model = os.getenv('LLM_MODEL')
api_key = os.getenv('OPEN_ROUTER_API_KEY')
dr_mcp_url = os.getenv('DR_MCP_URL')

# Validate required environment variables
if not llm_model:
    raise ValueError("LLM_MODEL environment variable is required")
if not api_key:
    raise ValueError("OPEN_ROUTER_API_KEY environment variable is required")

# Create an OpenAIModel instance
model = OpenAIModel(
    llm_model,
    provider=OpenAIProvider(
        base_url='https://openrouter.ai/api/v1',
        api_key=api_key,
    ),
)

# Configure HTTP clients for the MCP servers
# These servers are started and managed by the api_server.py lifespan manager.
dr_server = MCPServerStreamableHTTP(
    url=dr_mcp_url
)


# -----------------------------------------------------------------------------
# Define the Agent with a detailed system prompt.
# -----------------------------------------------------------------------------
agent = Agent(
    model=model,
    system_prompt=(
        """
        
        """
    ),
    retries=2,
    mcp_servers=[dr_server, pulse_dive_server]
)

# -----------------------------------------------------------------------------
# Main Loop for the CTI Analyst Agent
# -----------------------------------------------------------------------------
async def get_agent_response(user_input, message_history=None):
    """Runs the agent with optional message history and returns the result object.
    This function follows the same pattern as the Streamlit implementation.
    """
    logger.info(f"Running agent for input: {user_input}")
    try:
        # Use run with message history if provided
        if message_history:
            result = await agent.run(user_input, message_history=message_history)
        else:
            result = await agent.run(user_input)
        logger.info("Agent run completed.")
        return result  # Return the full result object
    except Exception as e:
        logger.exception("Error during agent run")
        print(f"Error interacting with agent: {e}")
        return None

class AgentZero:
    """
    AgentZero CTI Analyst - A callable interface for the threat intelligence agent.
    
    This class wraps the existing agent functionality to provide a clean API
    while preserving all existing logic for message filtering and processing.
    """
    
    def __init__(self):
        # All the module-level setup is already done above
        # This class just provides a clean interface
        pass
    
    async def query(self, prompt: str, message_history: list = None):
        """
        Process a CTI query with optional message history.
        
        Args:
            prompt: The user's query/prompt
            message_history: List of previous messages in PydanticAI format
            
        Returns:
            dict: {
                'output': str,              # The agent's response
                'filtered_messages': list,   # Updated message history minus tool returns (summarized)
                'unfiltered_messages': list, # Original message history before summarization
                'usage': dict               # Token usage information
            }
        """
        try:
            # Use existing agent.run_mcp_servers() context
            async with agent.run_mcp_servers():
                result = await get_agent_response(prompt, message_history)
                
                if result is None:
                    return {'error': 'Agent processing failed'}
                
                # Keep full conversation history (previous messages)
                filtered_messages = message_history or []
                new_messages_from_run = result.new_messages()
                
                # Store the new messages for API response
                unfiltered_new_messages = new_messages_from_run.copy()  # Store original new messages for API response
                
                # Call summarization API if configured - ONLY process new messages
                summarization_url = os.getenv('SUMMARIZATION_URL')
                summarized_new_messages = new_messages_from_run.copy()  # Default to original if no summarization
                
                if summarization_url and new_messages_from_run:  # Only process if we have new messages
                    try:
                        logger.info(f"Sending {len(new_messages_from_run)} NEW messages to summarization API")
                        
                        # Convert NEW messages to JSON for API call (not full history)
                        messages_json = to_jsonable_python(new_messages_from_run)
                        
                        # Debug: Log message types being sent
                        tool_return_count = 0
                        for msg in messages_json:
                            if msg.get('parts'):
                                for part in msg['parts']:
                                    if part.get('part_kind') == 'tool-return':
                                        tool_return_count += 1
                        
                        logger.info(f"Sending {tool_return_count} tool returns for summarization")
                        
                        # Call summarization API asynchronously
                        async with httpx.AsyncClient(timeout=30.0) as client:
                            response = await client.post(
                                f"{summarization_url}/summarize_message_history",
                                json={"message_history": messages_json},
                                headers={"Authorization": f"Bearer {os.getenv('API_BEARER_TOKEN')}"}
                            )
                            
                        if response.status_code == 200:
                            result_data = response.json()
                            if result_data["success"]:
                                # Convert back to ModelMessage objects
                                summarized_new_messages = ModelMessagesTypeAdapter.validate_python(
                                    result_data["summarized_history"]
                                )
                                logger.info("Message history summarization completed successfully")
                            else:
                                logger.warning(f"Summarization failed: {result_data.get('error', 'Unknown error')}")
                        else:
                            logger.warning(f"Summarization API returned {response.status_code}: {response.text}")
                    except Exception as e:
                        logger.warning(f"Summarization API call failed: {str(e)}")
                        # Continue with original messages on failure
                
                # Add summarized new messages directly to full conversation history
                filtered_messages.extend(summarized_new_messages)
                
                return {
                    'output': str(result.output),
                    'filtered_messages': filtered_messages,  # Full conversation with summarized new messages
                    'new_messages_summarized': summarized_new_messages,  # NEW: Only the new messages (summarized)
                    'new_messages_unfiltered': unfiltered_new_messages,  # NEW: Only the new messages (original)
                    'usage': result.usage() if result.usage() else {}
                }
        except Exception as e:
            logger.exception(f"Error in AgentZero.query: {str(e)}")
            return {'error': f'Agent processing failed: {str(e)}'}
