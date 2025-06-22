from dotenv import load_dotenv
import os
from langchain_openai import OpenAI, ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser
import streamlit as st

# TODO 1: Load environment variables
# This is important to securely access your API keys
# Hint: Use the load_dotenv() function
# Your code here:


def create_financial_chain():
    """
    This function creates and returns a LangChain chain for financial analysis.
    The chain will take financial information as input and return a detailed analysis.
    """

    # TODO 2: Initialize the language model
    # Hint: Use ChatOpenAI() to create an instance of the language model
    # Your code here:


    # TODO 3: Create a ChatPromptTemplate with system and human messages
    # The system message should define the AI's role as a financial advisor
    # The human message should include the financial analysis request with placeholders
    # for the user's financial information
    #
    # Use this system message:
    # "You are an experienced financial advisor in India who specializes in
    # personal finance management. Analyze the customer's financial situation and provide
    # detailed insights. Present the output in a clean format with clear sections."
    #
    # Use this human message:
    # "Perform initial financial analysis for the client in india:
    # - Monthly Income: {monthly_income}
    # - Monthly Expenses: {monthly_expenses}
    # - Current Savings: {current_savings}
    # Create a comprehensive assessment of their financial health.
    #
    # Following is the expected output
    # A detailed financial analysis in markdown format including:
    # - Current Financial Health Assessment
    # - Cash Flow Analysis
    # - Savings Potential"
    #
    # Hint: Use ChatPromptTemplate([("system", "..."), ("human", "...")])
    # Your code here:


    # TODO 4: Create and return a chain by combining the prompt, LLM, and output parser
    # Hint: Use the | operator to connect components: prompt | llm | StrOutputParser()
    # Your code here:


    # Remove this placeholder return statement when you implement the function
    pass


# Main application code
def main():
    """Main function to run the Streamlit application."""

    # TODO 5: Set up the Streamlit page configuration
    # Hint: Use st.set_page_config() to customize the page title, icon, and layout
    # Set the page title to "Financial Health Analysis", icon to "💰", and layout to "wide"
    # Your code here:


    # TODO 6: Create the main title for your application
    # Hint: Use st.title() to add a title to your app
    # Set the title to "Personal Financial Health Analysis"
    # Your code here:


    # TODO 7: Create a sidebar with input fields for financial information
    # Create the following inputs in the sidebar:
    # - Header: "Enter Your Financial Details"
    # - Monthly Income: number_input with min_value=0, default value=150000
    # - Monthly Expenses: number_input with min_value=0, default value=80000
    # - Current Savings: number_input with min_value=0, default value=500000
    # - Risk Tolerance: selectbox with options ["Low", "Moderate", "High"]
    # - Investment Timeline: slider from 1 to 30 years, default=15

    # Hint: Use "with st.sidebar:" to create a sidebar section
    # Your code here:


    # TODO 8: Create a button to trigger the financial analysis
    # Hint: Use st.button("Analyze Financial Health") to create a button in the sidebar
    # Your code here:


    # TODO 9: Implement the logic to process the financial analysis when the button is clicked
    # If the button is clicked:
    # 1. Create a try-except block to handle errors
    # 2. Show a spinner while analyzing with message "Analyzing your financial health..."
    # 3. Create the chain using create_financial_chain()
    # 4. Prepare inputs dictionary with all the user inputs
    # 5. Invoke the chain with the inputs
    # 6. Display the result using st.markdown()
    # 7. Handle any exceptions and show error message
    # Your code here:


    # TODO 10: Add a default message for when the app first loads or when the button hasn't been clicked
    # Hint: Use st.info() to display an informational message
    # Display a message guiding users to enter details and click the analyze button
    # Your code here:


if __name__ == "__main__":
    main()
