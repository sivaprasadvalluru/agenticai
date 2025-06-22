import streamlit as st
import os
import uuid
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import yfinance as yf
from io import StringIO

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import ConfigurableFieldSpec
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.tools import Tool
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_experimental.tools import PythonREPLTool

from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure page
st.set_page_config(page_title="Personal Finance Assistant", page_icon="💰", layout="wide")

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# Set up SQLite database for transaction history
def setup_database():
    conn = sqlite3.connect('finance_data.db')
    c = conn.cursor()
    
    # Create transactions table
    c.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        amount REAL,
        category TEXT,
        description TEXT
    )
    ''')
    
    # Create investment portfolio table
    c.execute('''
    CREATE TABLE IF NOT EXISTS portfolio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        shares REAL,
        purchase_price REAL,
        purchase_date TEXT
    )
    ''')
    
    # Insert some sample data if tables are empty
    c.execute("SELECT COUNT(*) FROM transactions")
    if c.fetchone()[0] == 0:
        sample_transactions = [
            ('2023-01-15', 1200.00, 'Income', 'Salary'),
            ('2023-01-20', -45.50, 'Food', 'Grocery shopping'),
            ('2023-01-25', -120.00, 'Utilities', 'Electricity bill'),
            ('2023-02-15', 1200.00, 'Income', 'Salary'),
            ('2023-02-22', -60.25, 'Transportation', 'Gas'),
            ('2023-03-01', -200.00, 'Housing', 'Rent'),
            ('2023-03-15', 1200.00, 'Income', 'Salary'),
            ('2023-03-18', -35.99, 'Entertainment', 'Streaming service'),
            ('2023-03-25', -80.00, 'Food', 'Restaurant')
        ]
        c.executemany('INSERT INTO transactions (date, amount, category, description) VALUES (?, ?, ?, ?)', 
                      sample_transactions)
    
    c.execute("SELECT COUNT(*) FROM portfolio")
    if c.fetchone()[0] == 0:
        sample_portfolio = [
            ('AAPL', 10, 150.75, '2023-01-10'),
            ('MSFT', 5, 280.50, '2023-02-15'),
            ('GOOGL', 3, 2200.00, '2023-03-20')
        ]
        c.executemany('INSERT INTO portfolio (symbol, shares, purchase_price, purchase_date) VALUES (?, ?, ?, ?)',
                      sample_portfolio)
    
    conn.commit()
    conn.close()
    
    return SQLDatabase.from_uri("sqlite:///finance_data.db")

# Set up RAG with financial knowledge
def setup_rag():
    # Sample financial advice documents
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
    
    # Create documents
    from langchain_core.documents import Document
    documents = [Document(page_content=doc, metadata={"source": "financial_advice"}) for doc in financial_docs]
    
    # Create vector store
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents=documents, embedding=embeddings)
    retriever = vectorstore.as_retriever()
    
    # Create RAG chain
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a financial advisor. Answer the question based on the context provided."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        ("human", "Context: {context}")
    ])
    
    document_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, document_chain)
    
    return rag_chain

# Define tools
def setup_tools(db):
    # SQL Tool
    def run_sql_query(query):
        """Execute a SQL query on the finance database."""
        try:
            conn = sqlite3.connect('finance_data.db')
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df.to_markdown()
        except Exception as e:
            return f"Error executing SQL query: {str(e)}"
    
    # Market Data Tool
    def get_stock_price(ticker):
        """Get the latest price for a stock ticker."""
        try:
            stock = yf.Ticker(ticker)
            price = stock.history(period="1d")['Close'].iloc[-1]
            return f"The current price of {ticker} is ${price:.2f}"
        except Exception as e:
            return f"Error fetching stock price: {str(e)}"
    
    # Transaction Analysis Tool
    def analyze_spending(category=None):
        """Analyze spending patterns, optionally filtering by category."""
        try:
            conn = sqlite3.connect('finance_data.db')
            if category:
                query = f"SELECT category, SUM(amount) as total FROM transactions WHERE category = '{category}' AND amount < 0 GROUP BY category"
            else:
                query = "SELECT category, SUM(amount) as total FROM transactions WHERE amount < 0 GROUP BY category"
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                return "No transaction data available for analysis."
            
            return df.to_markdown()
        except Exception as e:
            return f"Error analyzing spending: {str(e)}"
    
    # Python REPL Tool for data analysis
    python_repl = PythonREPLTool()
    
    # Tavily Search Tool for market research
    tavily_search = TavilySearchResults(max_results=3)
    
    # Create the tools list
    tools = [
        Tool(
            name="run_sql_query",
            func=run_sql_query,
            description="Useful for when you need to query the financial database. Input should be a valid SQL query."
        ),
        Tool(
            name="get_stock_price",
            func=get_stock_price,
            description="Get the current price of a stock. Input should be a valid stock ticker symbol (e.g., AAPL, MSFT)."
        ),
        Tool(
            name="analyze_spending",
            func=analyze_spending,
            description="Analyze spending patterns by category. Input can be a specific category or empty for all categories."
        ),
        Tool(
            name="python_calculator",
            func=python_repl.run,
            description="Useful for performing calculations, data analysis, or generating visualizations. Input should be Python code."
        ),
        Tool(
            name="market_research",
            func=tavily_search.invoke,
            description="Search the web for financial news, market analysis, or investment advice. Input should be a search query."
        )
    ]
    
    return tools

# Create Agent with memory and tools
def setup_agent(tools, rag_chain):
    # Define agent prompt
    system_message = """You are a Personal Finance Assistant that helps users manage their money, investments, and financial decisions.
    
    You have access to the following tools:
    1. SQL database containing transaction history and investment portfolio
    2. Stock market data
    3. Spending analysis tools
    4. Python calculator for financial calculations
    5. Web search for financial news and information
    
    Always be helpful, clear, and educational in your responses. Explain financial concepts simply.
    When providing investment advice, always include disclaimers about risk.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    # Create the agent
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    # Combine agent with RAG chain
    def process_query(query):
        if "advice" in query.lower() or "best practices" in query.lower() or "should I" in query.lower():
            return rag_chain.invoke({"input": query, "chat_history": []})
        else:
            return agent_executor.invoke({"input": query})
    
    # Create a combined runnable with message history
    combined_chain = RunnableWithMessageHistory(
        lambda x: {"output": process_query(x["input"])["answer"] if "answer" in process_query(x["input"]) else process_query(x["input"])["output"]},
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        history_factory_config=[
            ConfigurableFieldSpec(
                id="user_id",
                annotation=str,
                name="User ID",
            ),
            ConfigurableFieldSpec(
                id="conversation_id",
                annotation=str,
                name="Conversation ID",
            ),
        ],
    )
    
    return combined_chain

# Chat message history management
def get_session_history(user_id: str, conversation_id: str) -> ChatMessageHistory:
    if (user_id, conversation_id) not in st.session_state.store:
        st.session_state.store[(user_id, conversation_id)] = ChatMessageHistory()
    return st.session_state.store[(user_id, conversation_id)]

def create_new_conversation():
    st.session_state.conversation_counter += 1
    new_conv_id = str(uuid.uuid4())
    st.session_state.conversations[new_conv_id] = {
        "number": st.session_state.conversation_counter,
        "messages": []
    }
    st.session_state.current_conversation_id = new_conv_id

def switch_conversation(conv_id):
    st.session_state.current_conversation_id = conv_id

def handle_chat_input(prompt, combined_chain):
    current_conv = st.session_state.conversations[st.session_state.current_conversation_id]
    current_conv["messages"].append({"role": "user", "content": prompt})

    config = {
        "configurable": {
            "user_id": st.session_state.user_id,
            "conversation_id": st.session_state.current_conversation_id
        }
    }
    
    with st.chat_message("assistant", avatar="💰"):
        response_container = st.empty()
        response_container.markdown("Thinking...")
        
        try:
            result = combined_chain.invoke(
                {"input": prompt},
                config=config,
            )
            
            response_container.markdown(result["output"])
            current_conv["messages"].append({"role": "assistant", "content": result["output"]})
        except Exception as e:
            response_container.markdown(f"Error: {str(e)}")
            current_conv["messages"].append({"role": "assistant", "content": f"Error: {str(e)}"})

# Main app
def main():
    st.title("💰 Personal Finance Assistant")
    
    # Initialize session state
    if "store" not in st.session_state:
        st.session_state.store = {}

    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())

    if "conversations" not in st.session_state:
        st.session_state.conversations = {}

    if "conversation_counter" not in st.session_state:
        st.session_state.conversation_counter = 1

    if "current_conversation_id" not in st.session_state:
        new_conv_id = str(uuid.uuid4())
        st.session_state.conversations[new_conv_id] = {
            "number": st.session_state.conversation_counter,
            "messages": []
        }
        st.session_state.current_conversation_id = new_conv_id
    
    # Set up components
    db = setup_database()
    rag_chain = setup_rag()
    tools = setup_tools(db)
    combined_chain = setup_agent(tools, rag_chain)
    
    # Sidebar for conversation management
    with st.sidebar:
        st.subheader("Conversations")

        # Button to create new conversation
        if st.button("New Conversation", key="new_conv"):
            create_new_conversation()

        # Display and select conversations
        conversations_list = [(conv_id, f"Conversation {conv_data['number']}")
                             for conv_id, conv_data in st.session_state.conversations.items()]

        if conversations_list:
            selected_conv = st.selectbox(
                "Select Conversation:",
                options=[conv[0] for conv in conversations_list],
                format_func=lambda x: [conv[1] for conv in conversations_list if conv[0] == x][0],
                index=list(st.session_state.conversations.keys()).index(st.session_state.current_conversation_id)
            )

            if selected_conv != st.session_state.current_conversation_id:
                switch_conversation(selected_conv)
        
        st.divider()
        st.subheader("Sample Questions")
        st.markdown("""
        - What's my current spending by category?
        - What's the price of AAPL stock?
        - How should I start investing with $1000?
        - Calculate a monthly mortgage payment for $300,000
        - What are the latest news about interest rates?
        - Show me my investment portfolio performance
        """)
    
    # Main chat interface
    current_conv = st.session_state.conversations[st.session_state.current_conversation_id]

    # Display chat messages for current conversation
    for message in current_conv["messages"]:
        with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "💰"):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about your finances..."):
        handle_chat_input(prompt, combined_chain)

if __name__ == "__main__":
    main() 