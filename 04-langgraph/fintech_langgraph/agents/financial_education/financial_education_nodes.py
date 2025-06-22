"""
Nodes for the Financial Education Subgraph using RAG.
"""

from typing import Dict, Any, List, Tuple, Union
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
import os
import json
import logging
import torch
from langchain_openai import OpenAIEmbeddings
from fintech_langgraph.agents.financial_education.state import (
    FinancialEducationState,
    FinancialEducationInput,
    RAGResponse,
    LearningPath
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize components
logger.info("Initializing components...")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(temperature=0.7)
logger.info("Components initialized successfully")

def load_knowledge_base() -> Chroma:
    """Load the persisted ChromaDB knowledge base."""
    logger.info("Loading knowledge base from ./chroma_db")
    try:
        vectorstore = Chroma(
            persist_directory="./chroma_db",
            embedding_function=embeddings
        )
        logger.info("Knowledge base loaded successfully")
        return vectorstore
    except Exception as e:
        logger.error(f"Failed to load knowledge base: {str(e)}")
        raise

def retrieve_and_synthesize(input_state: FinancialEducationInput) -> Dict[str, Any]:
    """Retrieve relevant knowledge and synthesize content using RAG."""
    logger.info(f"Starting retrieve_and_synthesize with query: {input_state['user_query']}")
    try:
        # Load the persisted vector store
        logger.info("Loading vector store...")
        vectorstore = load_knowledge_base()
        
        # Create a retriever with specific search parameters
        logger.info("Creating retriever with similarity search...")
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        # Create the RAG chain with a comprehensive prompt
        logger.info("Setting up RAG chain...")
        message = """
        You are a financial education expert. Using the provided context, create a comprehensive educational response.
        
        Format your response as a JSON object with the following structure:
        {{
            "main_concepts": ["concept1", "concept2", ...],
            "detailed_explanation": "Your detailed explanation here...",
            "examples": ["example1", "example2", ...],
            "practical_applications": ["application1", "application2", ...],
            "common_misconceptions": ["misconception1", "misconception2", ...],
            "key_takeaways": ["takeaway1", "takeaway2", ...]
        }}
        
        If the information is not available in the context, respond with:
        {{
            "error": "I don't have enough information to answer this question."
        }}
        
        Question: {input}
        
        Context:
        {context}
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("human", message)
        ])
        
        # Create the document chain
        logger.info("Creating document chain...")
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        
        # Create the RAG chain
        logger.info("Creating RAG chain...")
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        
        # Get response from RAG chain
        logger.info("Invoking RAG chain...")
        response = rag_chain.invoke({"input": input_state["user_query"]})
        logger.debug(f"Raw RAG response: {response}")
        
        # Parse the JSON response
        logger.info("Parsing JSON response...")
        try:
            answer_json = json.loads(response["answer"])
            logger.debug(f"Parsed answer JSON: {answer_json}")
            if "error" in answer_json:
                logger.error(f"Error in answer JSON: {answer_json['error']}")
                raise ValueError(answer_json["error"])
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            raise ValueError("Failed to parse LLM response as JSON")
        
        # Create RAG response object
        logger.info("Creating RAG response object...")
        rag_response = RAGResponse(
            content=answer_json["detailed_explanation"],
            sources=[doc.page_content for doc in response["context"]],
            confidence=1.0  # RAG doesn't provide confidence scores
        )
        logger.debug(f"Created RAG response: {rag_response}")
        
        # Return state updates
        logger.info("Returning successful state updates")
        return {
            "input": input_state,  # Include the input state
            "rag_response": rag_response,
            "status": "content_retrieved_and_synthesized",
            "error": None  # Clear any previous errors
        }
    except Exception as e:
        logger.error(f"Error in retrieve_and_synthesize: {str(e)}", exc_info=True)
        return {
            "input": input_state,  # Include the input state even on error
            "status": "error",
            "error": f"Error in retrieval and synthesis: {str(e)}",
            "rag_response": None  # Clear RAG response on error
        }

def create_learning_path(state: FinancialEducationState) -> Dict[str, Any]:
    """Create a personalized learning path based on the RAG response."""
    logger.info("Starting create_learning_path")
    try:
        # Check if we have a valid RAG response
        logger.info("Checking RAG response validity...")
        rag_response = state.get("rag_response")
        logger.debug(f"RAG response from state: {rag_response}")
        
        if not rag_response or not hasattr(rag_response, "content") or not rag_response.content:
            logger.error("No valid RAG response available")
            return {
                "status": "error",
                "error": "No RAG response available",
                "learning_path": None
            }
        
        # Create prompt for learning path
        logger.info("Creating learning path prompt...")
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a financial education expert. Create a personalized learning path 
            based on the following content. Consider the user's context and create a structured 
            learning journey.
            
            Format your response as a JSON object with the following structure:
            {{
                "topics": ["topic1", "topic2", ...],
                "difficulty_level": "beginner/intermediate/advanced",
                "estimated_duration": "X hours",
                "prerequisites": ["prerequisite1", "prerequisite2", ...],
                "next_steps": ["step1", "step2", ...],
                "learning_sequence": [
                    {{
                        "topic": "topic1",
                        "duration": "X minutes",
                        "key_points": ["point1", "point2", ...],
                        "exercises": ["exercise1", "exercise2", ...]
                    }},
                    ...
                ]
            }}
            
            Ensure the learning path is personalized based on the user's context."""),
            ("user", "Content: {content}\nUser Context: {context}")
        ])
        
        # Get content and context
        logger.info("Getting content and context...")
        content = rag_response.content
        # Get context if available, otherwise use empty dict
        context = state["input"].get("user_context", {})
        logger.debug(f"Content: {content[:100]}...")  # Log first 100 chars of content
        logger.debug(f"Context: {context}")
        
        # Generate learning path
        logger.info("Generating learning path...")
        response = llm.invoke(prompt.format_messages(
            content=content,
            context=str(context)
        ))
        logger.debug(f"Raw learning path response: {response}")
        
        # Parse the JSON response
        logger.info("Parsing learning path JSON...")
        try:
            learning_path_json = json.loads(str(response.content))
            logger.debug(f"Parsed learning path JSON: {learning_path_json}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse learning path response as JSON: {str(e)}")
            raise ValueError("Failed to parse learning path response as JSON")
        
        # Create learning path object
        logger.info("Creating learning path object...")
        learning_path = LearningPath(
            topics=learning_path_json["topics"],
            difficulty_level=learning_path_json["difficulty_level"],
            estimated_duration=learning_path_json["estimated_duration"],
            prerequisites=learning_path_json["prerequisites"],
            next_steps=learning_path_json["next_steps"]
        )
        logger.debug(f"Created learning path: {learning_path}")
        
        # Return state updates
        logger.info("Returning successful state updates")
        return {
            "learning_path": learning_path,
            "status": "completed",
            "error": None  # Clear any previous errors
        }
    except Exception as e:
        logger.error(f"Error in create_learning_path: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": f"Error in learning path creation: {str(e)}",
            "learning_path": None  # Clear learning path on error
        } 