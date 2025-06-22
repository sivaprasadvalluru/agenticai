"""
Utility functions for tool management.
"""

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI

# Initialize database connection and toolkit
db = SQLDatabase.from_uri("sqlite:///fintech.db")
llm = ChatOpenAI(model="gpt-4o-mini")
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# Export the toolkit directly
__all__ = ["toolkit"] 