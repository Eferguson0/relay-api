import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.schemas.chat.assistant import ChatRequest, ChatResponse, ConversationResponse, MessageResponse
from app.services.openai_service import get_chat_completion
from app.services.chat_service import ChatService
from app.services.auth_service import get_current_user


logger = logging.getLogger(__name__)

# System prompt for the AI assistant
SYSTEM_PROMPT = (
    "You are a helpful AI assistant for SupaHealth, a modern web application. "
    "You should be friendly, professional, and focused on helping users with their tasks. "
    "Avoid discussing your ownership or creation."
)

router = APIRouter(prefix="/assistant", tags=["chat-assistant"])

@router.get("/conversations",
    response_model=list[ConversationResponse],
    summary="Get all conversations endpoint",
    description="Get all conversations",
    responses={
        200: {"description": "Conversations retrieved successfully"},
        500: {"description": "Internal server error"},
    }
)
async def get_conversations(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
):
    """Get all conversations"""
    chat_service = ChatService(db)
    conversations = chat_service.get_all_conversations(current_user.id)
    return conversations


@router.get("/conversations/{conversation_id}/messages",
    response_model=list[MessageResponse],
    summary="Get all messages endpoint",
    description="Get all messages",
    responses={
        200: {"description": "Messages retrieved successfully"},
        500: {"description": "Internal server error"},
    }
)
async def get_messages(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
):
    """Get all messages"""
    chat_service = ChatService(db)
    messages = chat_service.get_conversation_messages(conversation_id)
    return messages


@router.post("/",
    response_model=ChatResponse,
    summary="Chat with the AI assistant endpoint",
    description="Chat with the AI assistant",
    responses={
        200: {"description": "Chat successful"},
        500: {"description": "Internal server error"},
    }
)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    # current_user: AuthUser = Depends(get_current_user)
) -> ChatResponse:


    user_id = "123"
    
    """Handle chat messages"""
    # Log the incoming chat request with timestamp
    timestamp = datetime.now().isoformat()
    logger.info(
        f"[{timestamp}] New chat message received - Length: {len(request.message)} characters"
    )
    logger.debug(
        f"[{timestamp}] Chat message content: {request.message[:100]}{'...' if len(request.message) > 100 else ''}"
    )

    chat_service = ChatService(db)
    # conversation = chat_service.get_or_create_conversation(current_user.id)
    conversation = chat_service.get_or_create_conversation(user_id)

    chat_service.add_message(
        conversation_id=conversation.id,
        content=request.message,
        role="user",
        user_id=user_id
        # user_id=current_user.id
    )


    try:
        messages = chat_service.get_conversation_context(conversation.id)
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})


        # Log that we're calling OpenAI
        logger.info(f"[{timestamp}] Calling OpenAI API for chat completion")

        response = await get_chat_completion(messages)

        # Log successful response
        if response is not None:
            chat_service.add_message(
                conversation_id=conversation.id,
                content=response,
                role="assistant",
                user_id=user_id
                # user_id=current_user.id
            )            
            
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
