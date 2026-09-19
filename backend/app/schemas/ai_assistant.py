from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ChatRequest(BaseModel):
    message: str = Field(..., description="User question or query regarding current disaster conditions")
    conversation_history: Optional[List[Dict[str, str]]] = Field(default=[], description="Optional prior message history")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="AI assistant response grounded in verified project data")
    sources: List[str] = Field(..., description="List of project data sources queried for this answer")
    related_data: Dict[str, Any] = Field(default_factory=dict, description="Structured key data points referenced in the answer")
    disclaimer: str = Field(
        default="AI-generated recommendations are decision-support information and should be verified by authorized disaster-management personnel.",
        description="Mandatory verification disclaimer"
    )
