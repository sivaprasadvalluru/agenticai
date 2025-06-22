from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from typing import List, Dict, Any, Union
import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ChromaManager:
    def __init__(self):
        logger.info("Initializing ChromaManager...")
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
           
        )
        self.vectorstore = Chroma(
            persist_directory="./chroma_db",
            embedding_function=self.embeddings
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        logger.info("ChromaManager initialized successfully")
    
    def add_document(self, filename: str, content: Union[str, bytes]) -> str:
        """
        Add a document to the vector store.
        
        Args:
            filename (str): Name of the file
            content (Union[str, bytes]): Content of the file, can be string or bytes
            
        Returns:
            str: Success message
        """
        try:
            logger.info(f"Processing document: {filename}")
            
            # Convert bytes to string if necessary
            if isinstance(content, bytes):
                logger.debug("Converting bytes content to string")
                content = content.decode('utf-8')
            
            # Split text into chunks
            logger.info("Splitting text into chunks...")
            chunks = self.text_splitter.split_text(content)
            logger.info(f"Created {len(chunks)} chunks")
            
            # Create documents with metadata
            logger.info("Creating document objects...")
            documents = [
                Document(
                    page_content=chunk,
                    metadata={"source": filename}
                )
                for chunk in chunks
            ]
            
            # Add documents to vector store
            logger.info("Adding documents to vector store...")
            self.vectorstore.add_documents(documents)
            logger.info(f"Successfully added {len(chunks)} chunks from {filename}")
            
            return f"Successfully added {len(chunks)} chunks from {filename}"
            
        except Exception as e:
            error_msg = f"Error adding document: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)
    
    def search_documents(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant documents."""
        try:
            logger.info(f"Searching documents with query: {query}")
            results = self.vectorstore.similarity_search_with_score(query, k=n_results)
            logger.info(f"Found {len(results)} results")
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score
                }
                for doc, score in results
            ]
        except Exception as e:
            error_msg = f"Error searching documents: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return []
            
    def get_unique_documents(self) -> List[Dict[str, Any]]:
        """Get a list of unique documents in the knowledge base."""
        try:
            logger.info("Retrieving unique documents...")
            # Get all documents
            all_docs = self.vectorstore.get()
            
            # Group by source
            sources = {}
            for doc, metadata in zip(all_docs['documents'], all_docs['metadatas']):
                source = metadata.get('source', 'unknown')
                if source not in sources:
                    sources[source] = {
                        'source': source,
                        'chunk_count': 0,
                        'first_chunk': doc
                    }
                sources[source]['chunk_count'] += 1
            
            logger.info(f"Found {len(sources)} unique documents")
            return list(sources.values())
            
        except Exception as e:
            error_msg = f"Error getting unique documents: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return [] 