import streamlit as st
import sqlite3
from datetime import datetime
from fintech_langgraph.knowledge_base.chroma_manager import ChromaManager
from fintech_langgraph.utils.file_utils import is_valid_text_file, ensure_directory
import os
from dotenv import load_dotenv
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fintech_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
logger.info("Loading environment variables...")
load_dotenv()
logger.info("Environment variables loaded")

# Initialize session states
logger.info("Initializing session states...")
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
    logger.debug("Initialized user_email session state")
if 'previous_user_type' not in st.session_state:
    st.session_state.previous_user_type = None
    logger.debug("Initialized previous_user_type session state")
if 'chroma_manager' not in st.session_state:
    logger.info("Initializing ChromaManager...")
    st.session_state.chroma_manager = ChromaManager()
    logger.info("ChromaManager initialized")

def verify_user(email):
    """Placeholder function to verify user email in database"""
    logger.info(f"Verifying user email: {email}")
    try:
        conn = sqlite3.connect('fintech.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users WHERE email = ?', (email,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            logger.info(f"User verification successful for email: {email}")
        else:
            logger.warning(f"User verification failed for email: {email}")
        
        return result is not None
    except Exception as e:
        logger.error(f"Error verifying user: {str(e)}", exc_info=True)
        return False

def upload_to_rag(file):
    """Handle file upload to RAG system using LangChain"""
    logger.info(f"Processing file upload: {file.name}")
    
    if not is_valid_text_file(file.name):
        logger.warning(f"Invalid file type attempted: {file.name}")
        return "Error: Only .txt files are supported"
    
    try:
        # Read file content
        logger.info("Reading file content...")
        content = file.getvalue()
        logger.debug(f"File content type: {type(content)}")
        
        # Add document to vector store
        logger.info("Adding document to vector store...")
        result = st.session_state.chroma_manager.add_document(file.name, content)
        logger.info(f"Document added successfully: {result}")
        return result
    
    except Exception as e:
        error_msg = f"Error processing file: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg

# Sidebar
logger.info("Setting up sidebar...")
with st.sidebar:
    st.title("Fintech Assistant")
    
    # User type selection
    user_type = st.radio(
        "Select User Type",
        ["User", "Admin"],
        key="user_type"
    )
    logger.debug(f"Selected user type: {user_type}")
    
    # Clear session state if user type changes
    if st.session_state.previous_user_type != user_type:
        logger.info(f"User type changed from {st.session_state.previous_user_type} to {user_type}")
        st.session_state.user_email = None
        st.session_state.previous_user_type = user_type
    
    if user_type == "User":
        # Email input for users
        email = st.text_input("Enter your email")
        if email and st.button("Login"):
            logger.info(f"Login attempt for email: {email}")
            if verify_user(email):
                st.session_state.user_email = email
                logger.info(f"User logged in successfully: {email}")
                st.success(f"Logged in as {email}")
            else:
                logger.warning(f"Failed login attempt for email: {email}")
                st.error("Invalid email. Please try again.")
    
    elif user_type == "Admin":
        # File upload for admins
        uploaded_file = st.file_uploader("Upload knowledge base file", type=['txt'])
        if uploaded_file is not None:
            logger.info(f"File selected for upload: {uploaded_file.name}")
            if st.button("Process File"):
                logger.info("Processing uploaded file...")
                result = upload_to_rag(uploaded_file)
                logger.info(f"File processing result: {result}")
                st.success(result)
                
                # Show current documents in knowledge base
                st.subheader("Current Knowledge Base Documents")
                try:
                    logger.info("Retrieving unique documents from knowledge base...")
                    unique_docs = st.session_state.chroma_manager.get_unique_documents()
                    logger.info(f"Found {len(unique_docs)} unique documents")
                    
                    for doc in unique_docs:
                        logger.debug(f"Displaying document: {doc['source']}")
                        st.write(f"- {doc['source']} ({doc['chunk_count']} chunks)")
                        with st.expander("Preview first chunk"):
                            st.write(doc['first_chunk'])
                except Exception as e:
                    error_msg = f"Error displaying documents: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    st.error(error_msg)

# Main content area
logger.info("Setting up main content area...")
st.title("Fintech Portfolio Assistant")

if st.session_state.user_email:
    logger.info(f"Displaying main content for user: {st.session_state.user_email}")
    st.write(f"Welcome, {st.session_state.user_email}!")
    
    # Placeholder for portfolio view
    st.subheader("Your Portfolios")
    st.write("Portfolio information will be displayed here")
    
    # Placeholder for market analysis
    st.subheader("Market Analysis")
    st.write("Market analysis will be displayed here")
    
    # Placeholder for investment recommendations
    st.subheader("Investment Recommendations")
    st.write("Recommendations will be displayed here")
else:
    if user_type == "User":
        logger.debug("User not logged in, showing login prompt")
        st.info("Please log in using your email in the sidebar")
    else:
        logger.debug("Admin mode active, showing upload prompt")
        st.info("Admin mode: You can upload knowledge base files in the sidebar") 