import streamlit as st
from langchain_chroma import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
import tempfile
import os


# TODO 1: Initialize session state variables
# HINT: We need to track chat history and the vectorstore across app refreshes
# Create two session state variables:
# - One for storing chat messages between the user and assistant
# - One for storing the  vectorstore


def load_pdf_into_vectorstore(uploaded_file):
    """
    TODO 2: Implement the function to load and process a PDF into a vector store
    
    HINT: Follow these steps:
    1. Create a temporary file to store the uploaded PDF
    2. Load the PDF using PyPDFLoader
    3. Split the documents into smaller chunks using CharacterTextSplitter
       - Consider what chunk size and overlap would be appropriate for PDF content
    4. Create embeddings using HuggingFaceEmbeddings
    5. Create and persist a Chroma vectorstore from the documents
    6. Clean up the temporary file
    7. Save the vectorstore in the session state
    8. Return success status and a message
    
    Don't forget to handle potential errors with try/except!
    """
    try:
        # Your implementation here
        pass
    except Exception as e:
        return False, f"Error processing document: {str(e)}"


def get_response(query: str) :
    """
    TODO 3: Implement the RAG pipeline to answer user queries
    
    HINT: Follow these steps:
    1. Check if vectorstore exists, if not prompt user to upload a document
    2. Initialize embeddings and load the persisted vectorstore
    3. Create a message template that instructs the model how to answer
       - Be sure to include placeholders for the user input and document context
    4. Create a chat prompt template from your message
    5. Initialize the LLM (ChatOpenAI)
    6. Create a document chain using create_stuff_documents_chain
    7. Create a retrieval chain that combines retrieval and response generation
    8. Invoke the chain with the user query and return the answer
    
    Think about: How should the system respond if the answer isn't in the document?
    """
    try:
        # Your implementation here
        pass
    except Exception as e:
        return f"Error generating response: {str(e)}"


def main():
    """
    TODO 4: Implement the main Streamlit interface
    
    HINT: Your interface should have:
    1. A title for your application
    2. A sidebar with:
       - A file uploader for PDF files
       - A button to process the uploaded document
       - A button to clear the chat history
    3. The main chat interface with:
       - A display of chat history (both user and assistant messages)
       - An input box for the user to ask questions
       - Logic to:
           a. Add user messages to the chat history
           b. Display user messages in the chat
           c. Get and display the assistant's response
           d. Add assistant responses to the chat history
    
    Challenge: How would you improve the UI/UX of this application?
    """
    # Your implementation here
    pass


if __name__ == "__main__":
    main() 