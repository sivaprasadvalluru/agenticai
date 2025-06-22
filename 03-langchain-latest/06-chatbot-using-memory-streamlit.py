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

load_dotenv()

model = ChatOpenAI(model="gpt-4o-mini")

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


def handle_chat_input(prompt, config):
    current_conv = st.session_state.conversations[st.session_state.current_conversation_id]
    current_conv["messages"].append({"role": "user", "content": prompt})

    result = model_with_message_history.invoke(
        {"input": prompt},
        config=config,
    )

    current_conv["messages"].append({"role": "assistant", "content": result.content})


prompt = ChatPromptTemplate([
    (
        "system",
        "You are a helpful assistant. Answer all questions to the best of your ability .",
    ),
    MessagesPlaceholder(variable_name="mychat_history"),
    ("human", "{input}")
])

chain = prompt | model
model_with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="mychat_history",
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

# Streamlit UI
st.title("Siva Chatbot")

# Sidebar for conversation management
with st.sidebar:
    st.subheader("Conversations")

    # Button to create new conversation
    if st.button("New Conversation", key="new_conv"):
        create_new_conversation()

    # Display and select conversations using selectbox with numbered format
    conversations_list = [(conv_id, f"Conversation {conv_data['number']}")
                         for conv_id, conv_data in st.session_state.conversations.items()]

    selected_conv = st.selectbox(
        "Select Conversation:",
        options=[conv[0] for conv in conversations_list],
        format_func=lambda x: [conv[1] for conv in conversations_list if conv[0] == x][0],
        index=list(st.session_state.conversations.keys()).index(st.session_state.current_conversation_id)
    )

    if selected_conv != st.session_state.current_conversation_id:
        st.session_state.current_conversation_id = selected_conv
        

    # Display current IDs (can be hidden in production)
    st.sidebar.divider()
    st.sidebar.write(f"Current User ID: {st.session_state.user_id}")
    st.sidebar.write(f"Current Conversation ID: {st.session_state.current_conversation_id}")

# Main chat interface
current_conv = st.session_state.conversations[st.session_state.current_conversation_id]

# Chat input
if prompt := st.chat_input("What's on your mind?"):
    config = {
        "configurable": {
            "user_id": st.session_state.user_id,
            "conversation_id": st.session_state.current_conversation_id
        }
    }
    handle_chat_input(prompt, config)

# Display chat messages for current conversation
for message in current_conv["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])
