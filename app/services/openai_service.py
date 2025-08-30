from openai import AsyncOpenAI
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
try:
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    logger.info("Successfully initialized OpenAI client")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    raise

async def get_chat_completion(messages: list, model: str = "gpt-3.5-turbo"):
    """
    Get a completion from ChatGPT
    
    Args:
        messages (list): List of message dictionaries with 'role' and 'content'
        model (str): The model to use for completion
    
    Returns:
        str: The completion text
    """
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error getting chat completion: {str(e)}")
        raise Exception(f"Error getting chat completion: {str(e)}") 