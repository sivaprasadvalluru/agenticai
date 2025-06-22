#pip install langchain langchain-openai google-auth-oauthlib google-auth-httplib2 google-api-python-client

#Google Cloud Setup:

#U can copy my credentials.json given to you if u are unable to follow these below steps

#Go to Google Cloud Console (https://console.cloud.google.com)
#Create a new project
#Enable the Gmail API for your project
#Create OAuth 2.0 credentials:

#Go to APIs & Services > Credentials
#Click "Create Credentials" > "OAuth client ID"
#Choose "Desktop app"
#Download the credentials JSON file
#Rename it to credentials.json and place it in your project directory
#Go to the Google Cloud Console and navigate to the OAuth consent screen
#Set up the consent screen with the necessary information
#Click on Audience and add your email address to the list of test users





import os
from typing import List
from datetime import datetime, timedelta

# LangChain imports
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent,create_tool_calling_agent

from langchain_community.tools.gmail import GmailCreateDraft, GmailGetMessage, GmailSearch, GmailSendMessage


# Google API imports
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from dotenv import load_dotenv

load_dotenv()

# Step 2: Create Gmail credentials and service
def get_gmail_service():
    """Creates Gmail service with proper authentication"""
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    creds = None

    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

# Get the Gmail service
service = get_gmail_service()

# Step 3: Define the tools
def create_gmail_tools(service) -> List:
    """Creates a list of Gmail tools for the agent"""
    return [
        GmailCreateDraft(api_resource=service),
        GmailGetMessage(api_resource=service),
        GmailSearch(api_resource=service),
        GmailSendMessage(api_resource=service)
    ]


# Step 4: Create the prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an AI assistant that helps manage emails.
    Your tasks include:
    1. Reading emails
    2. Creating appropriate draft responses
    3. Summarizing email content

    Always be professional and courteous in drafts.
    When creating drafts, make sure to include:
    - A professional greeting
    - Clear and detailed content
    - A proper signature"""),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

# Step 5: Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Step 6: Create tools and agent
tools = create_gmail_tools(service)
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Step 7: Create helper functions for common tasks
def search_recent_emails(agent_executor, search_query: str, max_results: int = 5):
    """Search for recent emails matching the query."""
    return agent_executor.invoke({
        "input": f"Search for the {max_results} most recent emails matching: {search_query}"
    })

def create_response_draft(agent_executor, message_id: str, response_type: str = "general"):
    """Create a draft response to a specific email."""
    return agent_executor.invoke({
        "input": f"Read the email with ID {message_id} and create a professional draft response. "
                f"This should be a {response_type} response."
    })

def process_incoming_emails(agent_executor):
    """Process new unread emails from the last 24 hours."""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')
    search_query = f"is:unread after:{yesterday}"

    try:
        result = agent_executor.invoke({
            "input": f"""
            1. Search for emails matching: {search_query}
            2. For each email:
                - Read the content
                - Create an appropriate draft response
                - Return a summary of actions taken
            """
        })
        return result
    except Exception as e:
        return f"Error processing emails: {str(e)}"




def summarize_email(agent_executor, message_id: str):
    """Create a summary of a specific email."""
    return agent_executor.invoke({
        "input": f"Read the email with ID {message_id} and create a detailed summary "
                "including the main topic, key points, and any required actions."
    })

def process_incoming_emails(agent_executor, sender_email: str):
    """
    Process unread emails from a specific sender in the last 24 hours.

    Args:
        agent_executor: The LangChain agent executor
        sender_email: The email address to filter by (e.g., 'example@gmail.com')
    """
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')
    # Gmail search query combining unread, date, and sender filters
    search_query = f"from:{sender_email} after:{yesterday}" #is:unread

    try:
        result = agent_executor.invoke({
            "input": f"""
            1. Search for emails matching: {search_query}
            2. For each email found from {sender_email}:
                - Read the content
                - Create an appropriate draft response
                - Return a summary of actions taken and summary of email
            """
        })
        return result
    except Exception as e:
        return f"Error processing emails: {str(e)}"

# Example usage in main():
def main():
    try:
        print("Starting email processing...")

        # Specify the sender email address you want to filter
        sender_email = "sivaprasad.valluru@gmail.com"

        # Process unread emails from specific sender
        print(f"\nProcessing unread emails from {sender_email} in the last 24 hours...")
        processing_result = process_incoming_emails(agent_executor, sender_email)
        print("Processing Results:", processing_result)

    except Exception as e:
        print(f"Error in main execution: {str(e)}")
        raise


# Step 8: Main execution function
#def main():

        #print("Starting email processing...")

        # Example 1: Search for specific emails
        # print("\nSearching for recent important emails...")
        # search_result = search_recent_emails(agent_executor, "important")
        # print("Search Results:", search_result)

        # Example 2: Process unread emails
        # print("\nProcessing unread emails from the last 24 hours...")
        # processing_result = process_incoming_emails(agent_executor)
        # print("Processing Results:", processing_result)

        # Example 3: If you have a specific message ID, you can use it like this:
        # message_id = "your-message-id"
        # summary = summarize_email(agent_executor, message_id)
        # print("\nEmail Summary:", summary)



if __name__ == "__main__":
    main()
