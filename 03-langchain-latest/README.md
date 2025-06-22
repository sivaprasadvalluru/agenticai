# Personal Finance Assistant

A Streamlit-based LLM application that helps users manage their finances, investments, and make informed financial decisions.

## Features

- **Conversational Interface**: Chat with the finance assistant about your investments, spending patterns, and financial questions
- **SQL Database Integration**: Stores and analyzes transaction history and investment portfolio
- **Tool-based Agent**: Uses multiple LangChain tools to perform various financial tasks
- **Real-time Market Data**: Fetches current stock prices using the yfinance API
- **Tavily Search**: Searches the web for latest financial news and market information
- **Python Code Execution**: Performs financial calculations and generates visualizations
- **Conversational RAG**: Provides financial advice based on embedded knowledge
- **Memory**: Maintains conversation history across multiple sessions

## Technologies Used

- LangChain
- OpenAI API
- Streamlit
- SQLite
- FAISS Vector Store
- Tavily Search API
- Python REPL Tool

## Getting Started

1. Clone this repository
2. Install the dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```
4. Run the application: `streamlit run fintech_assistant.py`

## Sample Queries

- "What's my current spending by category?"
- "What's the price of AAPL stock?"
- "How should I start investing with $1000?"
- "Calculate a monthly mortgage payment for $300,000"
- "What are the latest news about interest rates?"
- "Show me my investment portfolio performance"

## Project Structure

- `fintech_assistant.py`: Main application file
- `requirements.txt`: Dependencies
- `finance_data.db`: SQLite database (created on first run)

## Notes for Students

This project demonstrates:
1. Building a complex LLM application with multiple integrated components
2. Using SQL databases with LangChain
3. Implementing tool-calling agents
4. Using RAG for domain-specific knowledge
5. Maintaining conversation memory
6. Building a user-friendly interface with Streamlit 