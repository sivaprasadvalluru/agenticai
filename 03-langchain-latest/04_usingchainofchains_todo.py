# TODO 1: Import the necessary libraries
from dotenv import load_dotenv
import os
from langchain_openai import OpenAI, ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import  RunnableSequence,RunnablePassthrough,RunnableParallel
from langchain_core.output_parsers import StrOutputParser
import streamlit as st

# TODO 2: Load environment variables and initialize the LLM
# Hint: Use load_dotenv() to load variables from .env file
# Initialize ChatOpenAI as your LLM


# TODO 3: Create a function for financial analysis chain
def create_financial_analysis_chain():
    """
    TODO  Create a financial analysis chain that:
    - Uses a ChatPromptTemplate with system and user messages
    - The system message should establish the AI as a financial advisor in India
    - The user message should include placeholders for financial data and expected output format
    

    Hint: Use ChatPromptTemplate.from_messages() with system and user messages
    Include placeholders like {monthly_income}, {monthly_expenses}, and {current_savings}
    Return the chain using the | operator to connect components
    """

    # TODO: Use the following prompt template for financial analysis
    """
    Financial Analysis Prompt:

    System message:
    "You are an experienced financial advisor in India who specializes in
    personal finance management. Analyze the customer's financial situation and provide
    detailed insights. Present the output in a clean format with clear sections."

    User message:
    "Perform initial financial analysis for the client in india:
    - Monthly Income: {monthly_income}
    - Monthly Expenses: {monthly_expenses}
    - Current Savings: {current_savings}
    Create a comprehensive assessment of their financial health.

    Following is the expected output
    A detailed financial analysis in markdown format including:
    - Current Financial Health Assessment
    - Cash Flow Analysis
    - Savings Potential
    - Risk Capacity Evaluation"
    """

    # TODO Chain the prompt with the LLM and a StrOutputParser and return it. Remove the below "pass"
    pass 


# TODO 4: Create a function for investment recommendation chain
def create_investment_recommendation_chain():
    """
    TODO 4.1: Create an investment recommendation chain that:
    - 
    - Uses a ChatPromptTemplate with system and user messages
    - The system message should establish the AI as an investment advisor in India
    - The user message should include placeholders for risk tolerance, investment timeline, and previous analysis
    - Chain the prompt with the LLM and a StrOutputParser

    Hint: Include placeholders like {risk_tolerance}, {investment_years}, and {financial_analysis}
    Return the chain using the | operator to connect components
    """

    # TODO: Use the following prompt template for investment recommendations
    """
    Investment Recommendation Prompt:

    System message:
    "You are an experienced Indian financial advisor specializing in
    investment planning. Consider Indian investment options like Fixed Deposits,
    Mutual Funds, PPF, and NPS. Present recommendations in a clean format with clear sections."

    User message:
    "Based on the financial analysis,
    recommend investment strategies that can generate minimum 10 to 12%  CAGR  and maximum from 15 to 20% CAGR based on risk tolerance:
    - Match their risk tolerance: {risk_tolerance}
    - Align with their {investment_years} year timeline
    - Maximize potential returns while managing risk
    - you should concentrate on financial retirement in next 15 years . Consider inflation of 7% in india.
    - Consider that annual income increases by 10% per annum
    - Amount after expenses (considering inflation of 7% per annum) can be invested more annually. Calculate how much extra can be invested every month
    - You believe that if u get 4% per annum(after removing inflation) return on your investments will be equal to annual expenses, we have achieved financial independence.
    - create investment plan so that customer can achieve financial independence in next 15 years

    Previous analysis: {financial_analysis}

    Below is the expected output:
    An investment strategy including:
    - Recommended Asset Allocation. Give how much amount to invest in each asset based on current financial state and how much to increment/decrement every year
    - Specific Investment Vehicles with amounts exactly
    - Expected Returns amounts based on current and future investments according plan
    - current monthly income, monthly expenses"
    """

     # TODO Return the chain using the | operator to connect components.  Remove the below "pass"
    pass 


# TODO 5: Create the main chain by combining the financial analysis and investment recommendation chains
# Hint: Use RunnableParallel and/or RunnablePassthrough to:
# - First run the financial analysis chain and preserve the original input
# - Then run the investment recommendation chain using the financial analysis results and original input
# - The final output should contain financial_analysis, investment_recommendation, and original_input


# TODO 6: Create a sample input dictionary for testing
# Hint: Include keys for monthly_income, monthly_expenses, current_savings, risk_tolerance, and investment_years

inputs = {
        "monthly_income": 150000,  # ₹1.5 lakhs per month
        "monthly_expenses": 80000,  # ₹80,000 per month
        "current_savings": 500000,  # ₹5 lakhs
        "risk_tolerance": "Moderate",  # Risk tolerance level
        "investment_years": 15  # Investment timeline in years
    }


# TODO 7: Set up the Streamlit interface
# Hint: Use st.set_page_config() to configure the page
# Add a title to the application


# TODO 8: Create the sidebar for user input
# Hint: Use with st.sidebar: to create a sidebar
# Add number_input fields for financial data
# Add a selectbox for risk tolerance
# Add a slider for investment timeline
# Add a button to trigger the analysis


# TODO 9: Implement the main application logic
# Hint: Check if the analyze button was clicked
# If clicked, create an inputs dictionary with user data
# Invoke the chain with the inputs
# Display results in tabs using st.tabs(). 
# First tab should contain Financial Analysis snd Second tab should contain investment Recommandations
# Handle exceptions with try/except


# TODO 10: Add a default message for when the app first loads
# Hint: Use st.info() to display instructions when the app first loads
