from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain.tools import tool
from langchain_experimental.tools import PythonREPLTool
from langchain_community.tools.tavily_search import TavilySearchResults

from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from fintech_langgraph.knowledge_base.chroma_manager import ChromaManager
import yfinance as yf # type: ignore
from datetime import datetime

# Load environment variables
load_dotenv()

# Get current date
current_date = datetime.now().strftime("%B %d, %Y")

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    streaming=True
)

# Initialize SQL Database
db = SQLDatabase.from_uri("sqlite:///fintech.db")
sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# Initialize Tavily Search
tavily_search = TavilySearchResults(max_results=3)



# RAG Tool
@tool
def search_knowledge_base(query: str) -> str:
    """Search the knowledge base for relevant information about financial topics.
    Use this tool when you need to provide educational content or context about financial concepts.
    """
    chroma_manager = ChromaManager()
    results = chroma_manager.search_documents(query, n_results=3)
    if not results:
        return "No relevant information found in the knowledge base."
    return "\n\n".join([f"Content: {r['content']}\nSource: {r['metadata'].get('source', 'Unknown')}" for r in results])

@tool
def get_stock_price(symbol: str) -> str:
    """Get real-time stock price and basic information for a given symbol.
    Use this tool when you need current market data for specific stocks.
    """
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return f"""
Symbol: {symbol}
Current Price: ${info.get('currentPrice', 'N/A')}
Previous Close: ${info.get('previousClose', 'N/A')}
Day Range: ${info.get('dayLow', 'N/A')} - ${info.get('dayHigh', 'N/A')}
52 Week Range: ${info.get('fiftyTwoWeekLow', 'N/A')} - ${info.get('fiftyTwoWeekHigh', 'N/A')}
Market Cap: ${info.get('marketCap', 'N/A'):,.2f}
Volume: {info.get('volume', 'N/A'):,}
"""
    except Exception as e:
        return f"Error fetching stock data for {symbol}: {str(e)}"

# Create tools list for portfolio manager
portfolio_tools = [
    *sql_toolkit.get_tools(),
    search_knowledge_base,
    PythonREPLTool(),
    tavily_search,

    get_stock_price
]


# System prompts for different agents
PORTFOLIO_MANAGER_PROMPT = f"""You are an expert Portfolio Manager Agent with extensive experience in financial markets and portfolio optimization.
Current Date: {current_date}

Your goal is to help users manage their investment portfolios effectively and make informed investment decisions.

Background:
- You have 15+ years of experience in portfolio management
- You specialize in risk management and portfolio optimization
- You understand both traditional and modern portfolio theory
- You can analyze portfolio performance and suggest improvements

Guidelines:
1. Always consider risk tolerance when making recommendations
2. Provide clear explanations for your suggestions
3. Use data-driven analysis to support your recommendations
4. Consider market conditions and economic factors
5. Maintain a professional and educational tone
6. Always use the most current market data available (as of {current_date})
7. Consider recent market events and news in your analysis

Available Tools:
- SQL Database tools for portfolio data
- Knowledge Base search for financial education
- Python REPL for data analysis
- Tavily Search for real-time market research
- Stock Price Tool for real-time stock data

Remember to:
- Use appropriate tools for each task
- Provide context for your recommendations
- Consider both short-term and long-term implications
- Explain complex concepts in simple terms
- Always check real-time market data before making recommendations
- Consider news and market sentiment in your analysis
- Verify that your information is current as of {current_date}
"""



# Create agent prompts
def create_agent_prompt(system_prompt: str) -> ChatPromptTemplate:
    return ChatPromptTemplate(
        messages=[
            SystemMessage(content=system_prompt),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ]
    )

# Create agents
def create_portfolio_manager_agent() -> AgentExecutor:
    prompt = create_agent_prompt(PORTFOLIO_MANAGER_PROMPT)
    agent = create_tool_calling_agent(llm=llm, tools=portfolio_tools, prompt=prompt)
    return AgentExecutor(
        agent=agent,
        tools=portfolio_tools,
        verbose=True,
        max_iterations=20
    )

