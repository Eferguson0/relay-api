import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.openai_service import get_chat_completion

logger = logging.getLogger(__name__)

# System prompt for the AI assistant
SYSTEM_PROMPT = (
    "You are a helpful AI assistant for SupaHealth, a modern web application. "
    "You should be friendly, professional, and focused on helping users with their tasks. "
    "Avoid discussing your ownership or creation."
)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


@router.post("/assistant")
async def chat(request: ChatRequest):
    """Handle chat messages"""
    # Log the incoming chat request with timestamp
    timestamp = datetime.now().isoformat()
    logger.info(
        f"[{timestamp}] New chat message received - Length: {len(request.message)} characters"
    )
    logger.debug(
        f"[{timestamp}] Chat message content: {request.message[:100]}{'...' if len(request.message) > 100 else ''}"
    )

    try:
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {"role": "user", "content": request.message},
        ]

        # Log that we're calling OpenAI
        logger.info(f"[{timestamp}] Calling OpenAI API for chat completion")

        response = await get_chat_completion(messages)

        # Log successful response
        logger.info(
            f"[{timestamp}] Chat response generated successfully - Length: {len(response)} characters"
        )
        logger.debug(
            f"[{timestamp}] Chat response content: {response[:100]}{'...' if len(response) > 100 else ''}"
        )

        return {"response": response}
    except Exception as e:
        logger.error(f"[{timestamp}] Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}",
        )
