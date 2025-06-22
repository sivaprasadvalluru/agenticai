import streamlit as st
import uuid
from datetime import datetime
from langchain_core.runnables import ConfigurableFieldSpec

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
# TODO 1: Import necessary dependencies from langchain
#  This is done already for you on the top. So, u dont need to do anything

from dotenv import load_dotenv

load_dotenv()

# TODO 2: Initialize the language model
# Hint: Use ChatOpenAI()

# TODO 3: Initialize session state variables
# Initialize the following session state variables:
# - store (for message history)
# - user_id (using uuid)
# - conversations (to track multiple conversations) If not in session, initialize it to {}
# - conversation_counter (to number conversations) If not in session, initialize it to 1
# - current_conversation_id (to track which conversation is active)
   #- if current_conversation_id is not in session, add an new Conversation into  st.session_state.conversations
   # using below code
#     st.session_state.conversations[new_conv_id] = {
#             "number": st.session_state.conversation_counter,
#             "messages": []
#         }
#     st.session_state.current_conversation_id = new_conv_id

# # TODO 4: Create a function to get or create a session history
# Function should:
# - Take user_id and conversation_id parameters
# - Return a ChatMessageHistory object
# - Create a new history if one doesn't exist

# TODO 5: Create a function to create a new conversation
# Function should:
# - Increment the conversation counter
# - Generate a new UUID for the conversation
# - Initialize an empty messages list for the new conversation
    # HINT: understand and use below code 
    #   st.session_state.conversations[new_conv_id] = {
    #     "number": st.session_state.conversation_counter,
    #     "messages": []
    #    }
# - Set the new conversation as the current one

# TODO 6: Create a function to switch between conversations
# Function should update the current_conversation_id

# TODO 7: Create a function to handle chat input
# Function should:
# - get the current conversation from session based on  current conversation id
# - Add the user message to the current conversation
# - Call the model with message history
# - Add the assistant's response to the conversation

# TODO 8: Create the chat prompt template
# Include:
# - A system message
# - A placeholder for chat history
# - A human message template

# TODO 9: Create the language model chain
# Combine the prompt and model

# TODO 10: Create a RunnableWithMessageHistory instance
# Connect the chain with the session history function

# TODO 11: Build the Streamlit UI
# Add a title for the chatbot

# TODO 12: Create the sidebar for conversation management
# Include:
# - A section header
# - A button to create new conversations
# - A selectbox to choose between conversations
# - Display of current IDs

# TODO 13: Set up the main chat interface
# Get the current conversation

# TODO 14: Create the chat input field
# Add code to:
# - Capture user input
# - Set up the configuration for the model
# - Call the handle_chat_input function

# TODO 15: Display the chat messages
# Loop through messages in the current conversation and display them