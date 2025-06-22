# TODO 1: Import the necessary libraries
# - streamlit for creating the web application
# - OpenAI for accessing the API
# - time (optional, for any delay effects)
# - dotenv for loading environment variables


# TODO 2: Load environment variables from .env file
# This will load your OPENAI_API_KEY from the .env file


# TODO 3: Initialize the OpenAI client
# Create a client instance to interact with the OpenAI API


# TODO 4: Create a function to get completions from the OpenAI API
# Function parameters:
# - messages: list of message objects with 'role' and 'content'
# - model: the model to use (default: "gpt-4o-mini")
# - temperature: controls randomness (default: 0)
# The function should return the content of the response


# TODO 5: Initialize session state for message history
# Check if "messages" exists in st.session_state
# If not, initialize it as an empty list


# TODO 6: Set up the Streamlit page
# Add a title for your chatbot application


# TODO 7: Display chat messages from history
# Loop through each message in the session state
# Use st.chat_message to create message containers
# Display the content using st.markdown


# TODO 8: Accept user input
# Use st.chat_input to create an input field
# Hint: Use the walrus operator (:=) for concise code


# TODO 9: When user submits a message:
# - Add the user message to chat history
# - Display the user message in a chat container
# - Generate assistant response using your completion function
# - Display the assistant response
# - Add the assistant response to chat history


# TODO 10: (Optional) Add any additional features
# - Model selection dropdown
# - Temperature slider
# - Clear conversation button
# - Character/role selection for the assistant
