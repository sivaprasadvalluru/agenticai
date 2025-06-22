import streamlit as st
from openai import OpenAI
import time
from dotenv import load_dotenv

load_dotenv()

# Initialize the OpenAI client
client = OpenAI()

def get_completion_from_messages(messages, model="gpt-4o-mini", temperature=0):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content

# Initialize session state for message history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Set up the Streamlit page
st.title("ChatBot")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What's on your mind?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Convert session state messages to the format expected by the completion function
        messages_for_completion = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in st.session_state.messages
        ]
        
        response = get_completion_from_messages(messages_for_completion)
        message_placeholder.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})