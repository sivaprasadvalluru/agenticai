"""
Financial Education Subgraph Implementation.

This module implements the Financial Education Subgraph as described in USECASE.md.
It handles knowledge retrieval, content synthesis, and personalized learning paths.
"""

from typing import Dict, Any, TypedDict, Optional
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json
import logging
from fintech_langgraph.agents.financial_education.state import (
    FinancialEducationState,
    FinancialEducationInput,
    RAGResponse,
    LearningPath
)
from fintech_langgraph.agents.financial_education.financial_education_nodes import retrieve_and_synthesize, create_learning_path

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

def create_financial_education_subgraph() :
    """Create the Financial Education Subgraph."""
    logger.info("Creating Financial Education Subgraph...")
    
    # Create the state graph
    workflow = StateGraph(
        input=FinancialEducationInput,
        state_schema=FinancialEducationState
    )
    
    # Add nodes
    logger.info("Adding nodes to the graph...")
    workflow.add_node("retrieve_and_synthesize", retrieve_and_synthesize)
    workflow.add_node("create_learning_path", create_learning_path)
    
    # Add edges
    logger.info("Adding edges to the graph...")
    workflow.add_edge("retrieve_and_synthesize", "create_learning_path")
    workflow.add_edge("create_learning_path", END)
    
    # Set entry point
    logger.info("Setting entry point...")
    workflow.set_entry_point("retrieve_and_synthesize")
    
    # Add conditional edges for error handling
    logger.info("Adding conditional edges...")
    workflow.add_conditional_edges(
        "retrieve_and_synthesize",
        lambda x: "error" if x.get("error") else "create_learning_path"
    )
    workflow.add_conditional_edges(
        "create_learning_path",
        lambda x: "error" if x.get("error") else END
    )
    
    logger.info("Financial Education Subgraph created successfully")
    return workflow.compile()

def run_financial_education(
    query: str,
    user_context: Dict[str, Any],
    user_knowledge_level: str = "beginner",
    topics_of_interest: Optional[list[str]] = None,
    learning_style: Optional[str] = None
) -> Dict[str, Any]:
    """Run the Financial Education Subgraph with the given input."""
    logger.info(f"Running Financial Education Subgraph with query: {query}")
    
    # Create input data
    input_data = FinancialEducationInput(
        user_query=query,
        user_knowledge_level=user_knowledge_level,
        topics_of_interest=topics_of_interest or [],
        learning_style=learning_style or "visual",
        user_context=user_context
    )
    
    # Create and run the subgraph
    logger.info("Creating and running subgraph...")
    subgraph = create_financial_education_subgraph()
    result = subgraph.invoke(input_data)
    
    # Print results for testing
    if __name__ == "__main__":
        rag_response = result.get('rag_response')
        if rag_response is not None:
            print("\nRAG Response:")
            print(f"Content: {rag_response.content[:200]}...")
            print(f"Sources: {len(rag_response.sources)} documents")
            print(f"Confidence: {rag_response.confidence}")
        
        learning_path = result.get('learning_path')
        if learning_path is not None:
            print("\nLearning Path:")
            print(f"Topics: {learning_path.topics}")
            print(f"Difficulty: {learning_path.difficulty_level}")
            print(f"Duration: {learning_path.estimated_duration}")
            print(f"Prerequisites: {learning_path.prerequisites}")
            print(f"Next Steps: {learning_path.next_steps}")
        
        print(f"\nStatus: {result.get('status')}")
        if result.get('error'):
            print(f"Error: {result.get('error')}")
    
    return result

if __name__ == "__main__":
    # Test the subgraph
    test_query = "What is compound interest and how does it work?"
    test_context = {
        "user_id": "test_user",
        "experience_level": "beginner",
        "interests": ["investing", "saving"],
        "learning_style": "visual"
    }
    
    result = run_financial_education(
        query=test_query,
        user_context=test_context
    ) 