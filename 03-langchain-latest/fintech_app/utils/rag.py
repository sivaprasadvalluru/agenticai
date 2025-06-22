import os
import pathlib
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_openai import ChatOpenAI
from langchain.chains import create_history_aware_retriever

class RAGManager:
    def __init__(self, persist_directory="fintech_app/data/chroma_db"):
        """Initialize the RAG manager with a vector store.
        
        Args:
            persist_directory: Directory where Chroma will persist the vector store data.
                              When this is provided, Chroma automatically persists data.
        """
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(persist_directory), exist_ok=True)
        
        # Initialize vector store
        # Note: When persist_directory is provided, Chroma automatically persists data
        # without needing to call .persist() method (which was removed in Chroma 0.4.x)
        self.vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )
        
        # Set up retriever
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
        
    def add_document_from_file(self, file_path):
        """Load a document from a file and add it to the vector store.
        
        Supports both PDF and TXT files.
        
        Args:
            file_path: Path to the file (PDF or TXT)
            
        Returns:
            str: Success or error message
        """
        try:
            # Determine file type and use appropriate loader
            file_extension = pathlib.Path(file_path).suffix.lower()
            
            if file_extension == '.pdf':
                loader = PyPDFLoader(file_path)
            elif file_extension == '.txt':
                loader = TextLoader(file_path)
            else:
                return f"Unsupported file type: {file_extension}. Please use PDF or TXT files."
            
            # Load the document
            documents = loader.load()
            
            # Split the document into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=100
            )
            splits = text_splitter.split_documents(documents)
            
            # Add to vector store
            # Data is automatically persisted when using persist_directory
            self.vector_store.add_documents(splits)
            
            return f"Successfully added {len(splits)} chunks from {file_path}"
        except Exception as e:
            return f"Error adding document: {str(e)}"
            
    def add_text(self, text, metadata=None):
        """Add a text string directly to the vector store."""
        try:
            # Create a document from the text
            if metadata is None:
                metadata = {"source": "user_input"}
            
            document = Document(page_content=text, metadata=metadata)
            
            # Split the document
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=100
            )
            splits = text_splitter.split_documents([document])
            
            # Add to vector store
            # Data is automatically persisted when using persist_directory
            self.vector_store.add_documents(splits)
            
            return f"Successfully added text ({len(splits)} chunks)"
        except Exception as e:
            return f"Error adding text: {str(e)}"
    
    def create_rag_chain(self):
        """Create a RAG chain for answering financial questions with conversation history support."""
        # Create prompt for contextualizing questions based on chat history
        contextualize_q_prompt = """Given above chat history and the below latest user question
            which might reference context in the chat history,
            formulate a standalone question which can be understood
            without the chat history. Do NOT answer the question,
            just reformulate it if needed and otherwise return it as is.
            Below is the latest question:

            {input}
            """
        
        contextualize_q_prompt_template = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", contextualize_q_prompt),
        ])
        
        # Create history-aware retriever
        history_aware_retriever = create_history_aware_retriever(
            self.llm, 
            self.retriever, 
            contextualize_q_prompt_template
        )
        
        # Create the final response prompt
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a financial advisor. Answer the question based on the context provided. If you don't know the answer, just say 'I don't know'."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            ("human", "Context: {context}")
        ])
        
        # Create document chain
        document_chain = create_stuff_documents_chain(self.llm, qa_prompt)
        
        # Create retrieval chain with history-aware retriever
        rag_chain = create_retrieval_chain(history_aware_retriever, document_chain)
        
        return rag_chain
    
    def add_default_knowledge(self):
        """Add default financial knowledge to the vector store."""
        financial_docs = [
            "When investing, diversification is key to reducing risk. Spread investments across different asset classes.",
            "Emergency funds should cover 3-6 months of expenses and be kept in liquid accounts.",
            "Tax-advantaged accounts like 401(k)s and IRAs offer significant benefits for retirement planning.",
            "Dollar-cost averaging involves investing a fixed amount regularly regardless of market conditions.",
            "Pay off high-interest debt before investing aggressively in the market.",
            "Index funds offer low-cost exposure to broad market segments with minimal fees.",
            "Rebalancing your portfolio periodically helps maintain your desired asset allocation.",
            "The rule of 72 can estimate how long it takes to double your money. Divide 72 by the annual rate of return.",
            "Time in the market beats timing the market. Long-term investing typically outperforms short-term trading.",
            "Consider your risk tolerance and time horizon when choosing investments."
        ]
        
        documents = [Document(page_content=doc, metadata={"source": "default_knowledge"}) for doc in financial_docs]
        # Data is automatically persisted when using persist_directory
        self.vector_store.add_documents(documents)
        
        return "Added default financial knowledge to the vector store."
    
    def get_conversational_rag_chain(self):
        """
        Creates a conversational RAG chain with automatic message history management.
        
        Returns:
            A runnable chain that can be used with session IDs to maintain conversation history.
        """
        from langchain_community.chat_message_histories import ChatMessageHistory
        from langchain_core.chat_history import BaseChatMessageHistory
        from langchain_core.runnables.history import RunnableWithMessageHistory
        
        # Create a store to keep track of conversation histories
        store = {}
        
        # Function to get or create a new chat history for a session
        def get_session_history(session_id: str) -> BaseChatMessageHistory:
            if session_id not in store:
                store[session_id] = ChatMessageHistory()
            return store[session_id]
        
        # Create the basic RAG chain
        rag_chain = self.create_rag_chain()
        
        # Wrap it with message history management
        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
        
        return conversational_rag_chain
    
    