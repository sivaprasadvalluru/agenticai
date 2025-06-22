"""
Portfolio Optimization Subgraph Implementation.

This module implements the Portfolio Optimization Subgraph as described in USECASE.md.
It handles parallel analysis of market conditions, portfolio composition, and knowledge base.
"""

from typing import Dict, Any, TypedDict, Optional, List, Annotated
import operator
from langgraph.graph import StateGraph, END,START
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json
import logging
from fintech_langgraph.agents.portfolio_optimization.states import (
    PortfolioOptimizationState,
    PortfolioOptimizationInput,
    MarketAnalysis,
    PortfolioAnalysis,
    KnowledgeBaseAnalysis,
    OptimizationPlan
)
from fintech_langgraph.agents.portfolio_optimization.portfolio_optimization_nodes import (
    analyze_market,
    analyze_portfolio,
    analyze_knowledge_base,
    create_optimization_plan
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize components
logger.info("Initializing components...")
llm = ChatOpenAI(temperature=0.7)
logger.info("Components initialized successfully")

def create_portfolio_optimization_graph() :
    """Create the Portfolio Optimization Subgraph."""
    logger.info("Creating Portfolio Optimization Subgraph...")
    
    # Create the state graph with annotated list for parallel results
    workflow = StateGraph(
        input=PortfolioOptimizationInput,
        state_schema=PortfolioOptimizationState
    )

   
    
    # Add nodes
    logger.info("Adding nodes to the graph...")
    workflow.add_node("analyze_market", analyze_market)
    workflow.add_node("analyze_portfolio", analyze_portfolio) 
    workflow.add_node("analyze_knowledge_base", analyze_knowledge_base)
    workflow.add_node("create_optimization_plan", create_optimization_plan)

    workflow.add_edge(START, "analyze_market")
    workflow.add_edge(START, "analyze_portfolio")
    workflow.add_edge(START, "analyze_knowledge_base")

    workflow.add_edge("analyze_market", "create_optimization_plan")
    workflow.add_edge("analyze_portfolio", "create_optimization_plan")
    workflow.add_edge("analyze_knowledge_base", "create_optimization_plan")
    
    # Set up parallel execution
    logger.info("Setting up parallel execution...")

    # Add final edge
    workflow.add_edge("create_optimization_plan", END)
    
    # Add conditional edges for error handling
    logger.info("Adding conditional edges...")
    for node in ["analyze_market", "analyze_portfolio", "analyze_knowledge_base", "create_optimization_plan"]:
        workflow.add_conditional_edges(
            node,
            lambda x: "error" if x.get("error") else "END"
        )
    
    logger.info("Portfolio Optimization Subgraph created successfully")
    return workflow.compile()

def run_portfolio_optimization(
    user_id: str,
    portfolio_id: str,
    optimization_goal: str,
    risk_tolerance: str,
    time_horizon: str,
    constraints: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Run the Portfolio Optimization Subgraph with the given input."""
    logger.info(f"Running Portfolio Optimization Subgraph for user {user_id}, portfolio {portfolio_id}")
    
    # Create input data
    input_data = PortfolioOptimizationInput(
        user_id=user_id,
        portfolio_id=portfolio_id,
        optimization_goal=optimization_goal,
        risk_tolerance=risk_tolerance,
        time_horizon=time_horizon,
        constraints=constraints or {}
    )
    
    # Create and run the subgraph
    logger.info("Creating and running subgraph...")
    subgraph = create_portfolio_optimization_graph()
    result = subgraph.invoke(input_data)
    
    # Print results for testing
    if __name__ == "__main__":
        market_analysis = result.get('market_analysis')
        if market_analysis is not None:
            print("\nMarket Analysis:")
            print(f"Market Conditions: {market_analysis['market_conditions']}")
            print(f"Trend Analysis: {market_analysis['trend_analysis']}")
            print(f"Risk Factors: {market_analysis['risk_factors']}")
        
        portfolio_analysis = result.get('portfolio_analysis')
        if portfolio_analysis is not None:
            print("\nPortfolio Analysis:")
            print(f"Current Allocation: {portfolio_analysis['current_allocation']}")
            print(f"Performance Metrics: {portfolio_analysis['performance_metrics']}")
            print(f"Risk Assessment: {portfolio_analysis['risk_assessment']}")
        
        knowledge_base_analysis = result.get('knowledge_base_analysis')
        if knowledge_base_analysis is not None:
            print("\nKnowledge Base Analysis:")
            print(f"Relevant Strategies: {knowledge_base_analysis['relevant_strategies']}")
            print(f"Best Practices: {knowledge_base_analysis['best_practices']}")
            print(f"Historical Context: {knowledge_base_analysis['historical_context']}")
        
        optimization_plan = result.get('optimization_plan')
        if optimization_plan is not None:
            print("\nOptimization Plan:")
            print(f"Recommended Changes: {optimization_plan['recommended_changes']}")
            print(f"Expected Outcomes: {optimization_plan['expected_outcomes']}")
            print(f"Implementation Steps: {optimization_plan['implementation_steps']}")
        
        print(f"\nStatus: {result.get('status')}")
        if result.get('error'):
            print(f"Error: {result.get('error')}")
    
    return result

if __name__ == "__main__":
    # Test the subgraph
    test_user_id = "2"
    test_portfolio_id = "2"
    test_optimization_goal = "maximize_returns"
    test_risk_tolerance = "moderate"
    test_time_horizon = "long_term"
    test_constraints = {
        "max_sector_exposure": 0.3,
        "min_diversification": 0.7,
        "liquidity_requirements": "high"
    }
    
    result = run_portfolio_optimization(
        user_id=test_user_id,
        portfolio_id=test_portfolio_id,
        optimization_goal=test_optimization_goal,
        risk_tolerance=test_risk_tolerance,
        time_horizon=test_time_horizon,
        constraints=test_constraints
    ) 