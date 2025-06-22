"""
Main graph implementation for the fintech application.

This module implements the main graph that coordinates between different
agents and subgraphs using LangGraph.
"""
from dotenv import load_dotenv
load_dotenv()
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from fintech_langgraph.main_graph.models import FintechState, AgentType, AgentResponse
from fintech_langgraph.main_graph.supervisor import decide_next_step, COMPONENT_GRAPHS
import json
import asyncio


def synthesize_responses(state: FintechState) -> FintechState:
    """
    Synthesize responses from different components into a final response.
    
    Args:
        state: Current state
        
    Returns:
        Updated state with synthesized response
    """
    try:
        # Combine all agent responses into a coherent final response
        final_response = "Synthesized Response:\n\n"
        for response in state.agent_responses:
            final_response += f"From {response.agent_type.value}:\n{response.response}\n\n"
        
        # Add the synthesized response to agent_responses
        state.agent_responses.append(AgentResponse(
            agent_type=AgentType.PORTFOLIO_MANAGER,  # Using an existing agent type since SUPERVISOR is not defined
            response=final_response
        ))
        
        return state
    except Exception as e:
        state.error = f"Error synthesizing responses: {str(e)}"
        return state

def create_main_graph():
    """
    Create the main graph for the fintech application.
    
    Returns:
        The configured and compiled main graph
    """
    # Create the graph
    workflow = StateGraph(FintechState)
    
    # Add the supervisor node
    workflow.add_node("supervisor", decide_next_step)
    
    # Add component nodes
    for agent_type in AgentType:
        workflow.add_node(agent_type.value, lambda state, agent_type=agent_type: handle_component(state, agent_type))
    
    # Add synthesize node
    workflow.add_node("synthesize", synthesize_responses)
    
    # Add edges from supervisor to components
    for agent_type in AgentType:
        #workflow.add_edge("supervisor", agent_type.value)
        workflow.add_edge(agent_type.value, "supervisor")
    
    # Add edge from synthesize to end
    workflow.add_edge("synthesize", END)
    
    # Add conditional edges for synthesize and end
    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state.next_component or "end",
        {
            "synthesize": "synthesize",
            "end": END,
            "portfolio_manager": "portfolio_manager",            
            "financial_education": "financial_education",
            "portfolio_optimization": "portfolio_optimization",
            "market_research": "market_research"
        }
    )
    
    # Set the entry point
    workflow.set_entry_point("supervisor")
    
    return workflow.compile()

def handle_component(state: FintechState, agent_type: AgentType) -> FintechState:
    """
    Handle component execution.
    
    Args:
        state: Current state
        agent_type: Type of agent to execute
        
    Returns:
        Updated state
    """
    try:
        print(f"\nHandling component: {agent_type.value}")
        # Get component graph
        graph_creator = COMPONENT_GRAPHS.get(agent_type)
        if graph_creator:
            print(f"Graph creator found: {graph_creator}")
            # Create the component
            component = graph_creator()
            
            # Handle input based on component type
            if agent_type in [AgentType.PORTFOLIO_MANAGER]:
                # For agents, pass the user query directly
                print(f"Agent input: {state.user_query}")
                result = component.invoke({"input": state.user_query})
            else:
                # For subgraphs, pass input dict directly
                print(f"Subgraph input: {state.input}")
                result = component.invoke(state.input)
            
            print(f"Component result: {result}")
            
            # Update state with result
            setattr(state, f"{agent_type.value}_state", result)
            
            # Add response to agent_responses
            state.agent_responses.append(AgentResponse(
                agent_type=agent_type,
                response=str(result)
            ))
        else:
            # Handle case where component is not implemented
            error_msg = f"Component {agent_type.value} is not implemented yet"
            print(f"Error: {error_msg}")
            setattr(state, f"{agent_type.value}_state", {"error": error_msg})
            state.agent_responses.append(AgentResponse(
                agent_type=agent_type,
                response=error_msg
            ))
            state.error = error_msg
        
        return state
    except Exception as e:
        error_msg = f"Error in {agent_type.value}: {str(e)}"
        print(f"Exception: {error_msg}")
        setattr(state, f"{agent_type.value}_state", {"error": error_msg})
        state.agent_responses.append(AgentResponse(
            agent_type=agent_type,
            response=error_msg
        ))
        state.error = error_msg
        return state

def run_main_graph(
    user_query: str,
    initial_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Run the main graph with the given user query.
    
    Args:
        user_query: The user's query
        initial_context: Optional initial context
        
    Returns:
        Dict containing the final state
    """
    # Create the graph
    graph = create_main_graph()
    
    # Prepare initial state
    initial_state = FintechState(
        user_query=user_query,
        input=initial_context or {}
    )
    
    # Run the graph
    result = graph.invoke(initial_state)
    
    return result 

async def run_all_use_cases():
    """
    Run the main graph for all 5 use cases to demonstrate different scenarios.
    """
    use_cases = [
        # Use Case 1: Portfolio Manager
        # {
        #     "name": "Portfolio Performance Analysis",
        #     "query": "What is the current performance of my portfolio with ID 1?",
        #     "initial_context": None
        # },
  
        # Use Case 2: Financial Education
        # {
        #     "name": "Investment Learning Path",
        #     "query": "I want to learn about value investing strategies. I'm a beginner investor with about 1 year of experience, and I prefer practical, step-by-step learning approaches.",
        #     "initial_context": None
        # },
        # # Use Case 3: Portfolio Optimization
        {
            "name": "Portfolio Rebalancing",
            "query": "I need to rebalance my portfolio (ID: 1) for better long-term growth. I'm comfortable with medium risk and want to avoid cryptocurrency investments. I also prefer stocks that pay at least 2% dividend yield.",
            "initial_context": None
        }
        # # Use Case 4: Market Research
        # {
        #     "name": "Sector Research",
        #     "query": "I'm interested in understanding the growth potential of the renewable energy sector over the next 5 years. Please analyze market trends, key players, and future outlook.",
        #     "initial_context": None
        # }
    ]

    # Create the graph
    graph = create_main_graph()
    
    # Run each use case
    for use_case in use_cases:
        print(f"\n{'='*80}")
        print(f"Running Use Case: {use_case['name']}")
        print(f"Query: {use_case['query']}")
        print(f"{'='*80}")
        
        # Prepare initial state
        initial_state = FintechState(
            user_query=use_case["query"],
            input=use_case["initial_context"] or {}
        )

        print(f"Initial state before invoking the graph: {initial_state}")
        
        try:
            # Run the graph
            result = graph.invoke(initial_state)
            
            # Print results
            print("\nFinal State:")

            print(f"{result}")
            
            
           
                
        except Exception as e:
            print(f"Error executing use case: {str(e)}")
        
        print(f"\n{'-'*80}\n")
        await asyncio.sleep(1)  # Small delay between use cases

if __name__ == "__main__":
    asyncio.run(run_all_use_cases()) 