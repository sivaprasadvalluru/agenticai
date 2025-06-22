from typing import List, Dict, Any, Optional, TypedDict,Annotated
import operator

class MarketResearchInput(TypedDict):
    """Input for the Market Research Subgraph"""
    query: str
    sector: Optional[str]
    timeframe: Optional[str]

class MarketResearchState(TypedDict):
    """State for the Market Research Subgraph"""
    input: MarketResearchInput
    market_conditions: Optional[Dict[str, Any]]
    sentiment_analysis: Optional[Dict[str, Any]]
    trend_analysis: Optional[Dict[str, Any]]
    recommendations: Optional[List[Dict[str, Any]]]
    errors: Annotated[list[str], operator.add ] 