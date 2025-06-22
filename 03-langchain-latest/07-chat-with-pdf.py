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


# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None

def load_pdf_into_vectorstore(uploaded_file):
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            file_path = tmp_file.name

        # Load and process the PDF
        loader = PyPDFLoader(file_path=file_path)
        documents = loader.load()
        
        # Split the documents into chunks
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=30, separator="\n")
        docs = text_splitter.split_documents(documents=documents)
        
        # Create embeddings
        embeddings = HuggingFaceEmbeddings()
        
        # Create and persist vectorstore
        vectorstore = Chroma.from_documents(
            documents, 
            embedding=embeddings,
            persist_directory="chromadb11"
        )
        
        # Clean up the temporary file
        os.unlink(file_path)
        
        # Store vectorstore in session state
        st.session_state.vectorstore = vectorstore
        return True, "Document uploaded and indexed successfully!"
    except Exception as e:
        return False, f"Error processing document: {str(e)}"

def get_response(query: str) -> str:
    try:
        if st.session_state.vectorstore is None:
            return "Please upload a document first."
        
        # Initialize embeddings and load vectorstore
        embeddings = HuggingFaceEmbeddings()
        vectorstore = Chroma(
            persist_directory="chromadb11",
            embedding_function=embeddings
        )
        
        # Create message template
        message = """
        Answer this question using the provided context. If information is not available in the context,
        just respond saying "I don't know"
        
        {input}
        
        Context:
        {context}
        """
        
        # Create prompt and chain
        prompt = ChatPromptTemplate.from_messages([("human", message)])
        llm = ChatOpenAI()
        
        # Create question-answering chain
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(vectorstore.as_retriever(), question_answer_chain)
        
        # Get response
        response = rag_chain.invoke({"input": query})
        return response['answer']
    except Exception as e:
        return f"Error generating response: {str(e)}"

def main():
    st.title("Document Chat Bot")
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("Document Upload")
        uploaded_file = st.file_uploader("Upload your PDF file", type=['pdf'])
        if uploaded_file is not None:
            if st.button("Process Document"):
                with st.spinner("Processing document..."):
                    success, message = load_pdf_into_vectorstore(uploaded_file)
                    if success:
                        st.success(message) 
                    else:
                         st.error(message)
        
        # Add clear chat button to sidebar
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Main chat interface
    st.subheader("Chat with your Document")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your document"):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            response = get_response(prompt)
            st.write(response)
            
        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
