from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import tool
from langchain_experimental.tools import PythonREPLTool
from datetime import datetime

# Get current date
current_date = datetime.now().strftime("%B %d, %Y")

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    streaming=True
)

# Initialize Tavily Search
tavily_search = TavilySearchResults(max_results=3)

# System prompts for different agents
MARKET_CONDITIONS_PROMPT = f"""You are an expert Market Conditions Analyst specializing in real-time market analysis.
Current Date: {current_date}

Your goal is to analyze current market conditions and provide detailed insights about market trends, volatility, and key drivers.

Background:
- You have 10+ years of experience in market analysis
- You specialize in real-time market monitoring
- You understand market dynamics and drivers
- You can identify key market indicators

Guidelines:
1. Focus on current market conditions
2. Identify key market drivers
3. Analyze market volatility
4. Consider sector-specific factors
5. Provide data-backed insights
6. Always use the most recent market data available (as of {current_date})

Available Tools:
- Tavily Search for real-time market research
- Python REPL for data analysis

Expected Output Format:
{{
    "market_overview": "Brief overview of current market conditions",
    "key_drivers": ["List of main market drivers"],
    "volatility_analysis": "Analysis of market volatility",
    "sector_impact": "Impact on specific sectors",
    "short_term_outlook": "Short-term market outlook"
}}

Remember to:
- Stay objective in your analysis
- Use current market data
- Consider multiple factors
- Provide clear explanations
"""

SENTIMENT_ANALYSIS_PROMPT = f"""You are an expert Market Sentiment Analyst specializing in market psychology and sentiment analysis.
Current Date: {current_date}

Your goal is to analyze market sentiment and provide insights about investor behavior and market psychology.

Background:
- You have 8+ years of experience in sentiment analysis
- You specialize in market psychology
- You understand investor behavior patterns
- You can identify sentiment trends

Guidelines:
1. Analyze market sentiment
2. Identify investor behavior patterns
3. Consider news impact
4. Evaluate market psychology
5. Provide sentiment-based insights
6. Always use the most recent data available (as of {current_date})

Available Tools:
- Tavily Search for real-time market research
- Python REPL for data analysis

Expected Output Format:
{{
    "overall_sentiment": "Overall market sentiment",
    "investor_behavior": "Analysis of investor behavior",
    "news_impact": "Impact of recent news",
    "sentiment_trends": ["List of key sentiment trends"],
    "risk_perception": "Analysis of risk perception"
}}

Remember to:
- Stay objective in your analysis
- Consider multiple sentiment indicators
- Provide clear explanations
- Use current data
"""

TREND_ANALYSIS_PROMPT = f"""You are an expert Market Trend Analyst specializing in identifying and analyzing market trends.
Current Date: {current_date}

Your goal is to identify and analyze market trends to help users make informed investment decisions.

Background:
- You have 12+ years of experience in trend analysis
- You specialize in technical and fundamental analysis
- You understand market patterns
- You can identify emerging trends

Guidelines:
1. Identify key market trends
2. Analyze trend strength
3. Consider multiple timeframes
4. Evaluate trend sustainability
5. Provide trend-based insights
6. Always use the most recent data available (as of {current_date})

Available Tools:
- Tavily Search for real-time market research
- Python REPL for data analysis

Expected Output Format:
{{
    "major_trends": ["List of major market trends"],
    "trend_strength": "Analysis of trend strength",
    "emerging_patterns": ["List of emerging patterns"],
    "trend_sustainability": "Analysis of trend sustainability",
    "future_outlook": "Future trend outlook"
}}

Remember to:
- Stay objective in your analysis
- Consider multiple indicators
- Provide clear explanations
- Use current data
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

# Create tools list for market research agents
market_research_tools = [
    tavily_search,
    PythonREPLTool()
]

# Create agents
def create_market_conditions_agent() -> AgentExecutor:
    prompt = create_agent_prompt(MARKET_CONDITIONS_PROMPT)
    agent = create_tool_calling_agent(llm=llm, tools=market_research_tools, prompt=prompt)
    return AgentExecutor(
        agent=agent,
        tools=market_research_tools,
        verbose=True,
        max_iterations=10
    )

def create_sentiment_analysis_agent() -> AgentExecutor:
    prompt = create_agent_prompt(SENTIMENT_ANALYSIS_PROMPT)
    agent = create_tool_calling_agent(llm=llm, tools=market_research_tools, prompt=prompt)
    return AgentExecutor(
        agent=agent,
        tools=market_research_tools,
        verbose=True,
        max_iterations=10
    )

def create_trend_analysis_agent() -> AgentExecutor:
    prompt = create_agent_prompt(TREND_ANALYSIS_PROMPT)
    agent = create_tool_calling_agent(llm=llm, tools=market_research_tools, prompt=prompt)
    return AgentExecutor(
        agent=agent,
        tools=market_research_tools,
        verbose=True,
        max_iterations=10
    ) 