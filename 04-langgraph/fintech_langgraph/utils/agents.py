"""
Utility functions for agent management.
"""

from typing import Dict, Any, List, Type
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool
from langchain_core.runnables import Runnable

def get_agent_executor(tools: List[BaseTool]) -> AgentExecutor:
    """Get an agent executor with the specified tools."""
    
    # Create the LLM
    llm: BaseChatModel = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the agent
    agent: Runnable = create_tool_calling_agent(llm, tools, prompt)
    
    # Create the executor
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True
    ) 