from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum

class AgentType(str, Enum):
    """Types of agents in the fintech system"""
   # SUPERVISOR = "supervisor"
    PORTFOLIO_MANAGER = "portfolio_manager"
    FINANCIAL_EDUCATION = "financial_education"
    PORTFOLIO_OPTIMIZATION = "portfolio_optimization"
    MARKET_RESEARCH = "market_research"

class AgentResponse(BaseModel):
    """Response from an agent or subgraph"""
    agent_type: AgentType
    response: str

class FintechState(BaseModel):
    """State for the main fintech graph"""
    # Core state fields
    user_query: str
    current_step: int = Field(default=0)
    final_response: Optional[str] = None
    error: Optional[str] = None
    agent_responses: List[AgentResponse] = Field(default_factory=list)
    
    # Input fields - can be either string (for agents) or dict (for subgraphs)
    input: Union[str, Dict[str, Any]] = Field(default="")
    
    # Component states
    portfolio_manager_state: Dict[str, Any] = Field(default_factory=dict)
    
    financial_education_state: Dict[str, Any] = Field(default_factory=dict)
    portfolio_optimization_state: Dict[str, Any] = Field(default_factory=dict)
    market_research_state: Dict[str, Any] = Field(default_factory=dict)
    
    # Minimal context for routing
    next_component: Optional[str] = None 