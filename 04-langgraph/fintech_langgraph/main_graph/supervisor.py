import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from fintech_langgraph.main_graph.models import FintechState, AgentType
from fintech_langgraph.agents.portfolio_optimization.portfolio_optimization_subgraph import create_portfolio_optimization_graph
from fintech_langgraph.agents.financial_education.financial_education_subgraph import create_financial_education_subgraph
from fintech_langgraph.agents.market_research.market_research_graph import create_market_research_graph
from fintech_langgraph.agents.fintech_agents import create_portfolio_manager_agent


# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    streaming=True
)

# Component graph creators
COMPONENT_GRAPHS = {
    AgentType.PORTFOLIO_MANAGER: create_portfolio_manager_agent,    
    AgentType.FINANCIAL_EDUCATION: create_financial_education_subgraph,
    AgentType.PORTFOLIO_OPTIMIZATION: create_portfolio_optimization_graph,
    AgentType.MARKET_RESEARCH: create_market_research_graph
}

SUPERVISOR_PROMPT = """You are an expert Financial System Orchestrator that coordinates between different financial experts and subgraphs.

Your Role:
- Analyze user queries and current state to determine the next best action
- Choose the most appropriate component to handle the next step
- Format input data according to component schemas
- Decide when to synthesize a final response

Available Components and Their Input Formats:

1. portfolio_manager (Agent):
   Input should be the user's query as a string. The agent will handle parsing and understanding the query.



2. financial_education (Subgraph):
   Input should be a dictionary with:
   {
       "user_query": "string",                    # Required
       "user_knowledge_level": "beginner/intermediate/advanced",  # Required
       "topics_of_interest": ["string"],          # Required
       "learning_style": "theoretical/practical/mixed",  # Optional
       "user_context": {                          # Optional
           "key": "value"
       }
   }

3. portfolio_optimization (Subgraph):
   Input should be a dictionary with:
   {
       "user_id": "string",                       # Required
       "portfolio_id": "string",                  # Required
       "optimization_goal": "growth/income/balanced",  # Required
       "risk_tolerance": "low/medium/high",       # Required
       "time_horizon": "short/medium/long",       # Required
       "constraints": {                           # Optional
           "min_position": "number",
           "max_position": "number",
           "excluded_sectors": ["string"],
           "required_dividend": "number"
       }
   }

4. market_research (Subgraph):
   Input should be a dictionary with:
   {
       "query": "string",                         # Required
       "sector": "string",                        # Optional
       "timeframe": "string"        this can be 1 month, 3 months, 6 months, 1 year, 5 years, 10 years, etc.               # Optional
   }

Note: For portfolio_manager and market_analyst agents, pass the user's query directly as a string. For other components (subgraphs), format the input as a dictionary according to their schemas.

Output Format:
{
    "next_component": "component_name" or "synthesize" or "end",
    "reasoning": "Explanation of your decision",
    "input_data": {
        // For agents: {"query": "user's query"}
        // For subgraphs: dictionary matching their schema
    }
}

Valid component names are:
- portfolio_manager

- financial_education
- portfolio_optimization
- market_research
- synthesize
- end
"""

def decide_next_step(state: FintechState) -> FintechState:
    """Decide the next step based on current state"""
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=SUPERVISOR_PROMPT),
        HumanMessage(content=f"""Current State:
Step: {state.current_step}
Original Query: {state.user_query}

Previous Responses:
{chr(10).join([f"{response.agent_type.value}: {response.response}" for response in state.agent_responses])}

Current Component States:
{json.dumps({k: v for k, v in state.dict().items() if k.endswith('_state')}, indent=2)}

Please decide the next step and update the state accordingly.""")
    ])
    
    # Get the decision from the LLM
    response = llm.invoke(prompt.format_messages())
    
    try:
        # Parse the response
        decision = json.loads(str(response.content))
        next_component = decision["next_component"]
        reasoning = decision["reasoning"]
        input_data = decision.get("input_data", {})
        
        # Update state
        state.current_step += 1
        state.next_component = next_component
        state.input = input_data
        
        # Print the decision for visibility
        print(f"\n=== Step {state.current_step} Decision ===")
        print(f"Next Component: {next_component}")
        print(f"Reasoning: {reasoning}")
        if input_data:
            print("\nInput Data in decide_next_step:")
            print(json.dumps(input_data, indent=2))
        print("===========================\n")
        print(f"State: {state}")
        return state
    except Exception as e:
        state.error = f"Error making decision: {str(e)}"
        return state 