"""
State models for the Portfolio Optimization Subgraph.
"""

from typing import Dict, Any, TypedDict, List, Optional, Annotated

class PortfolioOptimizationInput(TypedDict):
    """Input schema for portfolio optimization."""
    user_id: str
    portfolio_id: str
    optimization_goal: str
    risk_tolerance: str
    time_horizon: str
    constraints: Optional[Dict[str, Any]]

class MarketAnalysis(TypedDict):
    """Market analysis results."""
    market_conditions: Dict[str, Any]
    trend_analysis: Dict[str, Any]
    risk_factors: List[str]

class PortfolioAnalysis(TypedDict):
    """Portfolio analysis results."""
    current_allocation: Dict[str, float]
    performance_metrics: Dict[str, float]
    risk_assessment: Dict[str, Any]

class KnowledgeBaseAnalysis(TypedDict):
    """Knowledge base analysis results."""
    relevant_strategies: List[str]
    best_practices: List[str]
    historical_context: Dict[str, Any]

class OptimizationPlan(TypedDict):
    """Portfolio optimization plan."""
    recommended_changes: List[Dict[str, Any]]
    expected_outcomes: Dict[str, Any]
    implementation_steps: List[str]

class PortfolioOptimizationState(TypedDict):
    """State model for portfolio optimization."""
    user_id: str
    portfolio_id: str
    market_analysis: Optional[MarketAnalysis]
    portfolio_analysis: Optional[PortfolioAnalysis]
    knowledge_base_analysis: Optional[KnowledgeBaseAnalysis]
    optimization_plan: Optional[OptimizationPlan]
    status: str
    error: Optional[str] 