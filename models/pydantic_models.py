from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Any, Optional

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the speaker: 'user' or 'assistant'")
    content: str = Field(..., description="Content of the message")

class ChatRequest(BaseModel):
    session_id: str = Field(default="default_session", description="Session identifier for state management")
    question: str = Field(..., description="The query from the user")
    history: List[ChatMessage] = Field(default=[], description="Chat history context")

class Citation(BaseModel):
    source: str = Field(..., description="Source document or database table")
    chunk_text: str = Field(..., description="The snippet of content referenced")
    score: float = Field(..., description="Similarity score or confidence metric")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="Generated answer by the LLM")
    confidence_score: float = Field(..., description="Confidence rating based on retriever overlap")
    citations: List[Citation] = Field(default=[], description="Citations used to formulate the answer")
    query_rewritten: Optional[str] = Field(None, description="The rewritten query used for database search")

class FeedbackRequest(BaseModel):
    user_email: EmailStr = Field(..., description="Email of the user submitting feedback")
    rating: int = Field(..., description="Star rating between 1 and 5", ge=1, le=5)
    comment: Optional[str] = Field(None, description="Verbatim comment")

class FeedbackResponse(BaseModel):
    success: bool = Field(..., description="Indicates if feedback was saved")
    feedback_id: int = Field(..., description="Saved feedback identifier")

class CampusVisitRequest(BaseModel):
    parent_name: str = Field(..., description="Name of the parent/guardian")
    parent_email: EmailStr = Field(..., description="Email of the parent/guardian")
    parent_phone: str = Field(..., description="Phone number")
    visit_date: str = Field(..., description="Date of the visit (YYYY-MM-DD)")
    visit_time: str = Field(..., description="Time of the visit (HH:MM)")
    notes: Optional[str] = Field(None, description="Special requests or notes")

class CampusVisitResponse(BaseModel):
    success: bool = Field(..., description="Indicates if visit was scheduled")
    visit_id: int = Field(..., description="Scheduled visit ID")

class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Status of the application service")
    db_connected: bool = Field(..., description="Connection status to the main SQL database")
    vector_db_size: int = Field(..., description="Total index counts inside the vector store")
