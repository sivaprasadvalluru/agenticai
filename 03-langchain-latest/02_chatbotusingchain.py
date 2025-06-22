from dotenv import load_dotenv
import os
from langchain_openai import OpenAI, ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import  RunnableSequence
from langchain_core.output_parsers import StrOutputParser
import streamlit as st
load_dotenv()


def create_financial_chain():

    llm = ChatOpenAI()

    financial_analysis_prompt = ChatPromptTemplate([
        ("system", """You are an experienced financial advisor in India who specializes in
        personal finance management. Analyze the customer's financial situation and provide
        detailed insights. Present the output in a clean format with clear sections."""),
        ("human", """Perform initial financial analysis for the client in india:
        - Monthly Income: {monthly_income}
        - Monthly Expenses: {monthly_expenses}
        - Current Savings: {current_savings}
        Create a comprehensive assessment of their financial health.

        Following is the expected output
        A detailed financial analysis in markdown format including:
        - Current Financial Health Assessment
        - Cash Flow Analysis
        - Savings Potential
        """)
    ])

    return financial_analysis_prompt | llm | StrOutputParser()



inputs = {
        "monthly_income": 150000,  # ₹1.5 lakhs per month
        "monthly_expenses": 80000,  # ₹80,000 per month
        "current_savings": 500000,  # ₹5 lakhs
        "risk_tolerance": "Moderate",  # Risk tolerance level
        "investment_years": 15  # Investment timeline in years
    }


st.set_page_config(
        page_title="Financial Health Analysis",
        page_icon="💰",
        layout="wide"
    )
st.title("Personal Financial Health Analysis")

with st.sidebar:
    st.header("Enter Your Financial Details")
    monthly_income = st.number_input("Monthly Income (₹)", min_value=0, value=150000)
    monthly_expenses = st.number_input("Monthly Expenses (₹)", min_value=0, value=80000)
    current_savings = st.number_input("Current Savings (₹)", min_value=0, value=500000)
    risk_tolerance = st.selectbox("Risk Tolerance", ["Low", "Moderate", "High"])
    investment_years = st.slider("Investment Timeline (Years)", 1, 30, 15)

    analyze_button = st.button("Analyze Financial Health")

if analyze_button:
        try:
            with st.spinner("Analyzing your financial health..."):
                chain = create_financial_chain()
                inputs = {
                    "monthly_income": monthly_income,
                    "monthly_expenses": monthly_expenses,
                    "current_savings": current_savings,
                    "risk_tolerance": risk_tolerance,
                    "investment_years": investment_years
                }

                analysis_result = chain.invoke(inputs)

                st.markdown(analysis_result)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
else:
        st.info("Enter your financial details in the sidebar and click 'Analyze Financial Health' to get started.")
