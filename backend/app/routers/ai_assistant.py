"""FastAPI Router for AI Disaster Management Assistant."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas.ai_assistant import ChatRequest, ChatResponse
from backend.app.services.ai_assistant import get_ai_assistant_response

router = APIRouter(
    prefix="/assistant",
    tags=["AI Disaster Assistant"],
)


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with AI Disaster Assistant",
    description="Provides grounded disaster decision support based on actual project database state.",
)
def chat_with_assistant(request: ChatRequest, db: Session = Depends(get_db)):
    """Receives user query and returns grounded answer, data sources, and referenced metrics."""
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message field cannot be empty.",
        )

    try:
        response_data = get_ai_assistant_response(request.message, db)
        return ChatResponse(**response_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Assistant service error: {str(e)}",
        )
