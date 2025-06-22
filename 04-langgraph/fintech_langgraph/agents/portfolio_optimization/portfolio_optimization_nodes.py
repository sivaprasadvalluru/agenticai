from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_chroma import Chroma
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_openai import OpenAIEmbeddings
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
import yfinance as yf
import threading
from .states import (
    PortfolioOptimizationState, PortfolioOptimizationInput, MarketAnalysis,
    PortfolioAnalysis, KnowledgeBaseAnalysis, OptimizationPlan
)
import logging
import json
import pandas as pd
from functools import lru_cache
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize global LLM and tools
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Initialize database toolkit
db = SQLDatabase.from_uri("sqlite:///fintech.db")
db_toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# Initialize RAG components
embeddings = OpenAIEmbeddings()
vector_store = Chroma(
    collection_name="fintech_knowledge",
    embedding_function=embeddings,
    persist_directory="./data/chroma"
)

def query_knowledge_base(query: str) -> str:
    """
    Query the knowledge base using RAG pattern with improved chain implementation
    
    Args:
        query: The query string to search for in the knowledge base
        
    Returns:
        JSON string containing relevant documents and synthesized information
    """
    logger.info(f"Querying knowledge base with: {query}")
    try:
        # Create retriever from vector store
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        
        # Create prompt template for synthesis
        message = """
        Answer this question using the provided context only.
        If the information is not available in the context, just reply with "I don't know".
        
        Question: {input}
        
        Context:
        {context}
        """
        prompt = ChatPromptTemplate.from_messages([("human", message)])
        
        # Create chains
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        
        # Get response from RAG chain
        response = rag_chain.invoke({"input": query})
        
        # Get relevant documents for metadata
        docs = vector_store.similarity_search(query, k=3)
        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": "high"
            })
        
        # Structure final response
        final_response = {
            "query": query,
            "relevant_documents": results,
            "synthesis": response["answer"]
        }
        
        return json.dumps(final_response)
    except Exception as e:
        logger.error(f"Error querying knowledge base: {str(e)}")
        raise

# Cache for market data
@lru_cache(maxsize=100)
def get_cached_stock_data(symbol: str, data_type: str) -> Dict[str, Any]:
    """Get cached stock data with a 1-hour expiration"""
    try:
        stock = yf.Ticker(symbol)
        if data_type == "basic":
            # Get only essential info
            info = stock.info
            return {
                "symbol": symbol,
                "current_price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
                "market_cap": info.get("marketCap", 0),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "pe_ratio": info.get("trailingPE", 0),
                "dividend_yield": info.get("dividendYield", 0),
                "timestamp": datetime.now().isoformat()
            }
        elif data_type == "performance":
            # Get only recent performance data
            hist = stock.history(period="1mo")
            if not hist.empty:
                return {
                    "symbol": symbol,
                    "monthly_return": ((hist['Close'][-1] / hist['Close'][0]) - 1) * 100,
                    "volatility": hist['Close'].pct_change().std() * 100,
                    "timestamp": datetime.now().isoformat()
                }
        return {}
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
        return {}

def get_stock_info(symbol: str) -> Dict[str, Any]:
    """Get essential stock information"""
    return get_cached_stock_data(symbol, "basic")

def get_stock_performance(symbol: str) -> Dict[str, Any]:
    """Get stock performance metrics"""
    return get_cached_stock_data(symbol, "performance")

def get_market_trends(symbol: str) -> Dict[str, Any]:
    """Get market trends using web search"""
    try:
        stock = yf.Ticker(symbol)
        sector = stock.info.get("sector", "Unknown")
        industry = stock.info.get("industry", "Unknown")
        
        # Use Tavily search for market trends
        search = TavilySearchResults()
        trends = search.run(f"latest market trends {sector} {industry} sector analysis")
        
        return {
            "symbol": symbol,
            "sector": sector,
            "industry": industry,
            "trends": trends,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching market trends for {symbol}: {str(e)}")
        return {}

# Combine all tools
tools = [
    Tool(
        name="get_stock_info",
        func=get_stock_info,
        description="Get essential information about a stock. Input should be a valid stock symbol."
    ),
    Tool(
        name="get_stock_performance",
        func=get_stock_performance,
        description="Get performance metrics for a stock. Input should be a stock symbol."
    ),
    Tool(
        name="get_market_trends",
        func=get_market_trends,
        description="Get market trends and sector analysis for a stock. Input should be a stock symbol."
    ),
    Tool(
        name="tavily_search",
        func=TavilySearchResults().run,
        description="Search the web for market research and financial information."
    ),
    Tool(
        name="query_knowledge_base",
        func=query_knowledge_base,
        description="""Query the financial knowledge base for investment strategies, market insights, and guidelines.
        Input should be a specific query about investment strategies, sector analysis, or risk management.
        Returns relevant documents and synthesized information in JSON format."""
    ),
    *db_toolkit.get_tools()
]

# Create agent with tools
agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert financial analyst AI with access to:
    1. Database tools to query portfolio data
    2. Stock market data tools (get_stock_info, get_stock_performance, get_market_trends)
    3. Web search (tavily_search)
    4. Knowledge base query tool (query_knowledge_base) for investment strategies
    
    Important Instructions:
    1. Format all responses as valid JSON objects
    2. Do NOT include database schema information in your responses
    3. Only include relevant data and analysis in your output
    4. When using database tools, only return the query results, not the schema
    5. Keep responses focused on the specific analysis requested
    6. You MUST use the provided tools to perform the analysis
    7. Do not return generic messages - always perform the requested analysis
    8. Use SQL queries to get portfolio data
    9. Use market data tools to get stock information
    10. Use knowledge base and web search for research
    
    Example SQL queries you can use:
    - SELECT * FROM portfolio_holdings WHERE portfolio_id = {portfolio_id}
    - SELECT * FROM stocks WHERE symbol IN (SELECT symbol FROM portfolio_holdings WHERE portfolio_id = {portfolio_id})
    - SELECT * FROM transactions WHERE portfolio_id = {portfolio_id} ORDER BY transaction_date DESC
    - SELECT * FROM users WHERE user_id = {user_id}
    
    Always perform the complete analysis using these tools before returning results."""),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

agent = create_tool_calling_agent(llm, tools, agent_prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def analyze_market(state: PortfolioOptimizationInput) -> Dict[str, Any]:
    """Analyzes market trends and conditions"""
    thread_name = threading.current_thread().name
    logger.info(f"[Thread: {thread_name}] Starting market analysis for portfolio {state['portfolio_id']}")
    
    try:
        result = executor.invoke({
            "input": f"""Analyze market conditions for portfolio {state['portfolio_id']} following these steps:
            1. First, query the portfolio holdings using SQL:
               SELECT ph.*, s.sector, s.industry 
               FROM portfolio_holdings ph 
               JOIN stocks s ON ph.symbol = s.symbol 
               WHERE ph.portfolio_id = {state['portfolio_id']}
            
            2. For each holding:
               - Use get_stock_info tool to get current stock information
               - Use get_stock_performance tool to get stock performance metrics
               - Use get_market_trends tool to research market trends for the sector
            
            3. Combine all analyses into a JSON with:
               {{
                   "market_conditions": {{
                       "overall_sentiment": "positive/negative/neutral",
                       "volatility_index": "numeric value",
                       "market_momentum": "upward/downward/sideways"
                   }},
                   "trend_analysis": {{
                       "short_term": "bullish/bearish/neutral",
                       "medium_term": "bullish/bearish/neutral",
                       "long_term": "bullish/bearish/neutral"
                   }},
                   "risk_factors": ["risk factor 1", "risk factor 2", "risk factor 3"]
               }}
            
            Note: You MUST use the tools to perform the analysis. Do not return generic messages.""",
            "portfolio_id": state["portfolio_id"],
            "user_id": state["user_id"]
        })
        
        # Parse the output and convert to MarketAnalysis type
        output = result["output"]
        print("=======================In analyze_market=======================")
        print(output)

        if isinstance(output, str):
            # Remove markdown code block if present
            if "```json" in output:
                # Extract JSON string between ```json and ```
                output = output.split("```json")[1].split("```")[0].strip()
            output = json.loads(output)
            
        # Create properly typed market analysis
        market_analysis = MarketAnalysis(
            market_conditions=output.get("market_conditions", {
                "overall_sentiment": "neutral",
                "volatility_index": 0.0,
                "market_momentum": "sideways"
            }),
            trend_analysis=output.get("trend_analysis", {
                "short_term": "neutral",
                "medium_term": "neutral",
                "long_term": "neutral"
            }),
            risk_factors=output.get("risk_factors", [])
        )
        
        logger.info(f"[Thread: {thread_name}] Completed market analysis for portfolio {state['portfolio_id']}")
        return {"market_analysis": market_analysis}
    except Exception as e:
        logger.error(f"[Thread: {thread_name}] Error in market analysis: {str(e)}")
        raise

def analyze_portfolio(state: PortfolioOptimizationInput) -> Dict[str, Any]:
    """Analyzes portfolio composition and risk metrics"""
    thread_name = threading.current_thread().name
    logger.info(f"[Thread: {thread_name}] Starting portfolio analysis for portfolio {state['portfolio_id']}")
    
    try:
        result = executor.invoke({
            "input": f"""Analyze portfolio {state['portfolio_id']} following these steps:
            1. First, query the portfolio data using SQL:
               SELECT ph.*, s.sector, s.industry, p.total_value
               FROM portfolio_holdings ph 
               JOIN stocks s ON ph.symbol = s.symbol 
               JOIN portfolios p ON ph.portfolio_id = p.portfolio_id
               WHERE ph.portfolio_id = {state['portfolio_id']}
            
            2. Query transaction history:
               SELECT * FROM transactions 
               WHERE portfolio_id = {state['portfolio_id']} 
               ORDER BY transaction_date DESC
            
            3. Calculate portfolio metrics and generate rebalancing suggestions
            
            Return a JSON with:
            {{
                "current_allocation": {{
                    "stocks": "percentage as float",
                    "bonds": "percentage as float",
                    "cash": "percentage as float"
                }},
                "performance_metrics": {{
                    "returns_ytd": "float",
                    "volatility": "float",
                    "sharpe_ratio": "float"
                }},
                "risk_assessment": {{
                    "overall_risk": "high/medium/low",
                    "concentration_risk": "high/medium/low",
                    "liquidity_risk": "high/medium/low"
                }}
            }}
            
            Note: You MUST use the tools to perform the analysis. Do not return generic messages.""",
            "portfolio_id": state["portfolio_id"],
            "user_id": state["user_id"]
        })
        
        # Parse the output and convert to PortfolioAnalysis type
        output = result["output"]
        print("=======================In analyze_portfolio=======================")
        print(output)

        if isinstance(output, str):
            # Remove markdown code block if present
            if "```json" in output:
                # Extract JSON string between ```json and ```
                output = output.split("```json")[1].split("```")[0].strip()
            output = json.loads(output)
            
        # Create properly typed portfolio analysis
        portfolio_analysis = PortfolioAnalysis(
            current_allocation=output.get("current_allocation", {
                "stocks": 0.0,
                "bonds": 0.0,
                "cash": 0.0
            }),
            performance_metrics=output.get("performance_metrics", {
                "returns_ytd": 0.0,
                "volatility": 0.0,
                "sharpe_ratio": 0.0
            }),
            risk_assessment=output.get("risk_assessment", {
                "overall_risk": "medium",
                "concentration_risk": "medium",
                "liquidity_risk": "medium"
            })
        )
        
        logger.info(f"[Thread: {thread_name}] Completed portfolio analysis for portfolio {state['portfolio_id']}")
        return {"portfolio_analysis": portfolio_analysis}
    except Exception as e:
        logger.error(f"[Thread: {thread_name}] Error in portfolio analysis: {str(e)}")
        raise

def analyze_knowledge_base(state: PortfolioOptimizationInput) -> Dict[str, Any]:
    """Retrieves relevant knowledge and guidelines"""
    thread_name = threading.current_thread().name
    logger.info(f"[Thread: {thread_name}] Starting knowledge base analysis for portfolio {state['portfolio_id']}")
    
    try:
        result = executor.invoke({
            "input": f"""Analyze investment strategies for portfolio {state['portfolio_id']} following these steps:
            1. First, query the portfolio sectors using SQL:
               SELECT DISTINCT s.sector 
               FROM portfolio_holdings ph 
               JOIN stocks s ON ph.symbol = s.symbol 
               WHERE ph.portfolio_id = {state['portfolio_id']}
            
            2. For each sector:
               - Use query_knowledge_base tool to find relevant investment strategies
               - Use query_knowledge_base tool to find risk management guidelines
               - Use tavily_search for latest market research
            
            Return a JSON with:
            {{
                "relevant_strategies": ["strategy1", "strategy2", "strategy3"],
                "best_practices": ["practice1", "practice2", "practice3"],
                "historical_context": {{
                    "similar_market_conditions": "description",
                    "historical_performance": "description",
                    "lessons_learned": "key lessons"
                }}
            }}
            
            Note: You MUST use the tools to perform the analysis. Do not return generic messages.""",
            "portfolio_id": state["portfolio_id"],
            "user_id": state["user_id"]
        })
        
        # Parse the output and convert to KnowledgeBaseAnalysis type
        output = result["output"]
        print("=======================In analyze_knowledge_base=======================")
        print(output)

        if isinstance(output, str):
            # Remove markdown code block if present
            if "```json" in output:
                # Extract JSON string between ```json and ```
                output = output.split("```json")[1].split("```")[0].strip()
            output = json.loads(output)
            
        # Create properly typed knowledge base analysis
        knowledge_base_analysis = KnowledgeBaseAnalysis(
            relevant_strategies=output.get("relevant_strategies", []),
            best_practices=output.get("best_practices", []),
            historical_context=output.get("historical_context", {
                "similar_market_conditions": "",
                "historical_performance": "",
                "lessons_learned": ""
            })
        )
        
        logger.info(f"[Thread: {thread_name}] Completed knowledge base analysis for portfolio {state['portfolio_id']}")
        return {"knowledge_base_analysis": knowledge_base_analysis}
    except Exception as e:
        logger.error(f"[Thread: {thread_name}] Error in knowledge base analysis: {str(e)}")
        raise

def create_optimization_plan(state: PortfolioOptimizationState) -> Dict[str, Any]:
    """Creates final optimization plan combining all analyses"""
    thread_name = threading.current_thread().name
    logger.info(f"[Thread: {thread_name}] Creating final optimization plan")
    
    try:
        result = executor.invoke({
            "input": f"""Create a comprehensive optimization plan based on:
            Market Analysis: {state['market_analysis']}
            Portfolio Analysis: {state['portfolio_analysis']}
            Knowledge Base Analysis: {state['knowledge_base_analysis']}
            
            Use query_knowledge_base tool to find relevant optimization strategies.
            
            Return a JSON with:
            {{
                "recommended_changes": [
                    {{
                        "asset_class": "asset type",
                        "action": "increase/decrease/hold",
                        "target_allocation": "target percentage as float"
                    }}
                ],
                "expected_outcomes": {{
                    "expected_return": "float",
                    "expected_risk": "float",
                    "expected_sharpe": "float"
                }},
                "implementation_steps": [
                    "step 1 description",
                    "step 2 description",
                    "step 3 description"
                ]
            }}""",
            "portfolio_id": state["portfolio_id"],
            "user_id": state["user_id"]
        })
        
        # Parse the output and convert to OptimizationPlan type
        output = result["output"]
        print("=======================In create_optimization_plan=======================")
        print(output)

        if isinstance(output, str):
            # Remove markdown code block if present
            if "```json" in output:
                # Extract JSON string between ```json and ```
                output = output.split("```json")[1].split("```")[0].strip()
            output = json.loads(output)
            
        # Create properly typed optimization plan
        optimization_plan = OptimizationPlan(
            recommended_changes=output.get("recommended_changes", [
                {
                    "asset_class": "stocks",
                    "action": "hold",
                    "target_allocation": 0.0
                }
            ]),
            expected_outcomes=output.get("expected_outcomes", {
                "expected_return": 0.0,
                "expected_risk": 0.0,
                "expected_sharpe": 0.0
            }),
            implementation_steps=output.get("implementation_steps", [])
        )
        
        logger.info(f"[Thread: {thread_name}] Completed optimization plan creation")
        return {"optimization_plan": optimization_plan}
    except Exception as e:
        logger.error(f"[Thread: {thread_name}] Error creating optimization plan: {str(e)}")
        raise 