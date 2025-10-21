import logging

from openai import AsyncOpenAI

from app.core.config import settings

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
        from datetime import datetime

        # Log the API call details
        timestamp = datetime.now().isoformat()
        user_message = next(
            (msg["content"] for msg in messages if msg["role"] == "user"),
            "No user message found",
        )
        logger.info(
            f"[{timestamp}] Making OpenAI API call - Model: {model}, User message length: {len(user_message)} characters"
        )

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
        )

        # Log successful API response
        response_content: str | None = response.choices[0].message.content
        if response_content is not None:
            logger.info(
                f"[{timestamp}] OpenAI API call successful - Response length: {len(response_content)} characters"
            )
        else:
            logger.warning(
                f"[{timestamp}] OpenAI API call successful but returned no content"
            )

        # Log usage information if available
        if hasattr(response, "usage") and response.usage:
            logger.info(
                f"[{timestamp}] OpenAI API usage - Prompt tokens: {response.usage.prompt_tokens}, "
                f"Completion tokens: {response.usage.completion_tokens}, "
                f"Total tokens: {response.usage.total_tokens}"
            )

        return response_content
    except Exception as e:
        logger.error(f"Error getting chat completion: {str(e)}")
        raise Exception(f"Error getting chat completion: {str(e)}")
