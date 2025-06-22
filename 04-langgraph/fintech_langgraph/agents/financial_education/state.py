"""
State management for the Financial Education Subgraph.
"""

from typing import List, Dict, Any, Optional, TypedDict
from pydantic import BaseModel, Field

class RAGResponse(BaseModel):
    """Response from the RAG system."""
    content: str
    sources: List[str] = Field(default_factory=list)
    confidence: float = 0.0

class LearningPath(BaseModel):
    """Represents a personalized learning path."""
    topics: List[str] = Field(default_factory=list)
    difficulty_level: str = "intermediate"
    estimated_duration: str = "1 hour"
    prerequisites: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)

class FinancialEducationInput(TypedDict):
    """Input schema for Financial Education subgraph."""
    user_query: str
    user_knowledge_level: str  # beginner/intermediate/advanced
    topics_of_interest: List[str]
    learning_style: Optional[str]  # theoretical/practical/mixed
    user_context: Optional[Dict[str, Any]]  # Additional user context

class FinancialEducationState(TypedDict):
    """State for the Financial Education Subgraph."""
    input: FinancialEducationInput
    rag_response: Optional[RAGResponse]
    learning_path: Optional[LearningPath]
    error: Optional[str]
    status: str  # pending/processing/completed/error 