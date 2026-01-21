from pydantic_settings import BaseSettings, SettingsConfigDict

# Base API URL - replace with your actual API endpoint
BASE_URL = "https://api.example.com/v1"  # Example: "https://api.brave.com/res/v1"

class ExampleMCPSettings(BaseSettings):
    """Settings for the Example MCP Server.
    
    This class automatically loads configuration from environment variables.
    You can set these in a .env file or as system environment variables.
    
    Example .env file:
        EXAMPLE_API_KEY=your-api-key-here
    """
    model_config = SettingsConfigDict(
        env_file=".env",            # Load from .env file if it exists
        env_file_encoding="utf-8",   # Use UTF-8 encoding
        case_sensitive=False,        # API_KEY or api_key both work
        extra='ignore'               # Ignore extra fields in .env
    )
    
    # Your API key - loaded from EXAMPLE_API_KEY environment variable
    # To use a different variable name, use Field with alias:
    # example_api_key: str = Field(alias="MY_CUSTOM_API_KEY")
    EXAMPLE_API_KEY: str