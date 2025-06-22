from typing import Annotated, Sequence, TypedDict, Dict, Any, List, Union
from langgraph.graph import StateGraph, END, START
from langgraph.constants import Send
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import logging
import threading
import json
from fintech_langgraph.agents.market_research.market_research_agents import (
    create_market_conditions_agent,
    create_sentiment_analysis_agent,
    create_trend_analysis_agent
)
from fintech_langgraph.agents.market_research.state import MarketResearchState, MarketResearchInput

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize LLM for supervisor
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    streaming=True
)

def start_research(state: MarketResearchInput) -> Dict[str, Any]:
    """Initiates the market research process with parallel analysis"""
    thread_name = threading.current_thread().name
    logger.info(f"[{thread_name}] Starting market research for query: {state['query']}")
    
    # Set input state once and initiate parallel processing
    return {
        "input": state,
        "next": [
            Send("analyze_market_conditions", state),
            Send("analyze_sentiment", state),
            Send("analyze_trends", state)
        ]
    }

def analyze_market_conditions(state: MarketResearchInput) -> Dict[str, Any]:
    """Analyze current market conditions"""
    thread_name = threading.current_thread().name
    logger.info(f"[{thread_name}] Starting market conditions analysis")
    try:
        agent = create_market_conditions_agent()
        query = f"Analyze current market conditions for {state['sector'] if state['sector'] else 'the market'} over {state['timeframe'] if state['timeframe'] else 'recent period'}. Consider: {state['query']}"
        logger.info(f"[{thread_name}] Executing market conditions query: {query}")
        result = agent.invoke({"input": query})
        # Parse JSON response
        try:
            market_conditions = json.loads(result["output"])
        except json.JSONDecodeError:
            market_conditions = {"error": "Failed to parse market conditions response"}
        logger.info(f"[{thread_name}] Completed market conditions analysis")
        return {"market_conditions": market_conditions}
    except Exception as e:
        error_msg = f"Error in market conditions analysis: {str(e)}"
        logger.error(f"[{thread_name}] {error_msg}")
        return {"error": error_msg}

def analyze_sentiment(state: MarketResearchInput) -> Dict[str, Any]:
    """Analyze market sentiment"""
    thread_name = threading.current_thread().name
    logger.info(f"[{thread_name}] Starting sentiment analysis")
    try:
        agent = create_sentiment_analysis_agent()
        query = f"Analyze market sentiment for {state['sector'] if state['sector'] else 'the market'} over {state['timeframe'] if state['timeframe'] else 'recent period'}. Consider: {state['query']}"
        logger.info(f"[{thread_name}] Executing sentiment analysis query: {query}")
        result = agent.invoke({"input": query})
        # Parse JSON response
        try:
            sentiment_analysis = json.loads(result["output"])
        except json.JSONDecodeError:
            sentiment_analysis = {"error": "Failed to parse sentiment analysis response"}
        logger.info(f"[{thread_name}] Completed sentiment analysis")
        return {"sentiment_analysis": sentiment_analysis}
    except Exception as e:
        error_msg = f"Error in sentiment analysis: {str(e)}"
        logger.error(f"[{thread_name}] {error_msg}")
        return {"error": error_msg}

def analyze_trends(state: MarketResearchInput) -> Dict[str, Any]:
    """Analyze market trends"""
    thread_name = threading.current_thread().name
    logger.info(f"[{thread_name}] Starting trend analysis")
    try:
        agent = create_trend_analysis_agent()
        query = f"Analyze market trends for {state['sector'] if state['sector'] else 'the market'} over {state['timeframe'] if state['timeframe'] else 'recent period'}. Consider: {state['query']}"
        logger.info(f"[{thread_name}] Executing trend analysis query: {query}")
        result = agent.invoke({"input": query})
        # Parse JSON response
        try:
            trend_analysis = json.loads(result["output"])
        except json.JSONDecodeError:
            trend_analysis = {"error": "Failed to parse trend analysis response"}
        logger.info(f"[{thread_name}] Completed trend analysis")
        return {"trend_analysis": trend_analysis}
    except Exception as e:
        error_msg = f"Error in trend analysis: {str(e)}"
        logger.error(f"[{thread_name}] {error_msg}")
        return {"error": error_msg}

def generate_recommendations(state: MarketResearchState) -> Dict[str, Any]:
    """Generate recommendations based on all analyses"""
    thread_name = threading.current_thread().name
    logger.info(f"[{thread_name}] Starting recommendation generation")
    try:
        # Create a comprehensive analysis prompt
        analysis_prompt = f"""Based on the following market research, provide actionable recommendations:

Market Conditions:
{json.dumps(state.get('market_conditions', {}), indent=2)}

Sentiment Analysis:
{json.dumps(state.get('sentiment_analysis', {}), indent=2)}

Trend Analysis:
{json.dumps(state.get('trend_analysis', {}), indent=2)}

Original Query: {state['input']['query']}
Sector: {state['input']['sector'] if state['input']['sector'] else 'General Market'}
Timeframe: {state['input']['timeframe'] if state['input']['timeframe'] else 'Recent Period'}

Provide recommendations in the following format:
{{
    "recommendations": [
        {{
            "action": "Specific action to take",
            "rationale": "Reasoning based on the analysis",
            "risk_level": "Low/Medium/High",
            "timeframe": "Short-term/Long-term"
        }}
    ],
    "summary": "Brief summary of key findings and recommendations"
}}
"""
        logger.info(f"[{thread_name}] Generating recommendations based on analysis")
        response = llm.invoke([HumanMessage(content=analysis_prompt)])
        
        # Parse JSON response
        try:
            if isinstance(response.content, str):
                parsed_response = json.loads(response.content)
                if isinstance(parsed_response, dict) and "recommendations" in parsed_response:
                    return {"recommendations": parsed_response["recommendations"]}
            return {"recommendations": None}
        except json.JSONDecodeError:
            logger.error(f"[{thread_name}] Failed to parse recommendations response")
            return {"recommendations": None}
            
        logger.info(f"[{thread_name}] Completed recommendation generation")
    except Exception as e:
        error_msg = f"Error generating recommendations: {str(e)}"
        logger.error(f"[{thread_name}] {error_msg}")
        return {"error": error_msg}

def should_end(state: MarketResearchState) -> bool:
    """Determine if the graph should end"""
    return bool(state.get("error") or state.get("recommendations"))

def create_market_research_graph():
    """Create the market research graph"""
    logger.info("Creating market research graph")
    
    # Create the graph with MarketResearchInput as input state and MarketResearchState as state_schema
    workflow = StateGraph(input=MarketResearchInput, state_schema=MarketResearchState)

    # Add nodes with unique names that don't conflict with state keys
    workflow.add_node("start_research", start_research)
    workflow.add_node("analyze_market_conditions", analyze_market_conditions)
    workflow.add_node("analyze_sentiment", analyze_sentiment)
    workflow.add_node("analyze_trends", analyze_trends)
    workflow.add_node("generate_recommendations", generate_recommendations)

    # Add edges for parallel processing
    workflow.add_edge(START, "start_research")
    workflow.add_conditional_edges(
        "start_research",
        lambda x: x["next"],
        ["analyze_market_conditions", "analyze_sentiment", "analyze_trends"]
    )
    workflow.add_edge("analyze_market_conditions", "generate_recommendations")
    workflow.add_edge("analyze_sentiment", "generate_recommendations")
    workflow.add_edge("analyze_trends", "generate_recommendations")
    workflow.add_edge("generate_recommendations", END)

    logger.info("Market research graph created successfully")
    return workflow.compile()

# Test the graph
if __name__ == "__main__":
    logger.info("Starting market research graph test")
    
    # Create test input
    test_input = {
        "query": "Analyze the tech sector's performance and provide investment recommendations",
        "sector": "Technology",
        "timeframe": "last 3 months"
    }
    
    # Create and run the graph
    graph = create_market_research_graph()
    logger.info("Executing market research graph with test input")
    result = graph.invoke(test_input)
    
    # Log the results
    logger.info("Market Research Results:")
    logger.info(f"Market Conditions: {json.dumps(result.get('market_conditions'), indent=2)}")
    logger.info(f"Sentiment Analysis: {json.dumps(result.get('sentiment_analysis'), indent=2)}")
    logger.info(f"Trend Analysis: {json.dumps(result.get('trend_analysis'), indent=2)}")
    logger.info(f"Recommendations: {json.dumps(result.get('recommendations'), indent=2)}")
    
    if result.get("error"):
        logger.error(f"Error occurred: {result['error']}") 