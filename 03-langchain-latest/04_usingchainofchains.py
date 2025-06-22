from dotenv import load_dotenv
import os
from langchain_openai import OpenAI, ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import  RunnableSequence,RunnablePassthrough,RunnableParallel
from langchain_core.output_parsers import StrOutputParser
import streamlit as st

load_dotenv()
llm = ChatOpenAI()


def create_financial_analysis_chain():


    financial_analysis_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an experienced financial advisor in India who specializes in
        personal finance management. Analyze the customer's financial situation and provide
        detailed insights. Present the output in a clean format with clear sections."""),
        ("user", """Perform initial financial analysis for the client in india:
        - Monthly Income: {monthly_income}
        - Monthly Expenses: {monthly_expenses}
        - Current Savings: {current_savings}
        Create a comprehensive assessment of their financial health.

        Following is the expected output
        A detailed financial analysis in markdown format including:
        - Current Financial Health Assessment
        - Cash Flow Analysis
        - Savings Potential
        - Risk Capacity Evaluation""")
    ])

    return financial_analysis_prompt | llm | StrOutputParser()


def create_investment_recommendation_chain():

    investment_recommendation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an experienced Indian financial advisor specializing in
            investment planning. Consider Indian investment options like Fixed Deposits,
            Mutual Funds, PPF, and NPS. Present recommendations in a clean format with clear sections."""),
            ("user", """Based on the financial analysis,
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
            - current monthly income, monthly expenses""")
        ])
    return investment_recommendation_prompt | llm | StrOutputParser()


chain = RunnableParallel({
                "financial_analysis": create_financial_analysis_chain(),
                "original_input": RunnablePassthrough()
            }) | RunnableParallel({
                "original_input": lambda x: x["original_input"],
                "financial_analysis": lambda x: x["financial_analysis"],
                "investment_recommendation": {
                    "financial_analysis": lambda x: x["financial_analysis"],
                    "risk_tolerance": lambda x: x["original_input"]["risk_tolerance"],
                    "investment_years": lambda x: x["original_input"]["investment_years"]
                } |create_investment_recommendation_chain()
               
            })






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

                inputs = {
                    "monthly_income": monthly_income,
                    "monthly_expenses": monthly_expenses,
                    "current_savings": current_savings,
                    "risk_tolerance": risk_tolerance,
                    "investment_years": investment_years
                }

                result = chain.invoke(inputs)
                tab1, tab2= st.tabs(["Financial Analysis", "Investment Recommendations"])
                with tab1:
                    st.subheader("🔍 Financial Analysis")
                    st.markdown(result["financial_analysis"])

                with tab2:
                    st.subheader("📈 Investment Recommendations")
                    st.markdown(result["investment_recommendation"])


        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
else:
        st.info("Enter your financial details in the sidebar and click 'Analyze Financial Health' to get started.")
