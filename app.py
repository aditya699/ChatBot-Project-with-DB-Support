import os
import pandas as pd
import chainlit as cl
from dotenv import load_dotenv
from anthropic import Anthropic
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic

# Load environment variables
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")

# Initialize Anthropic client
client = Anthropic()

# Create simple ticket data with 10 rows
def create_dummy_ticket_data():
    """Create simple ticket data with 10 manually defined rows"""
    data = {
        'ticket_id': ['TKT001', 'TKT002', 'TKT003', 'TKT004', 'TKT005', 
                     'TKT006', 'TKT007', 'TKT008', 'TKT009', 'TKT010'],
        'customer_name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Davis',
                         'Eve Wilson', 'Frank Miller', 'Grace Lee', 'Henry Ford', 'Ivy Chen'],
        'issue_type': ['Technical', 'Billing', 'Account', 'Service', 'Product',
                      'Technical', 'Billing', 'Service', 'Account', 'Product'],
        'status': ['Open', 'In Progress', 'Resolved', 'Closed', 'Open',
                  'In Progress', 'Resolved', 'Open', 'Closed', 'In Progress'],
        'priority': ['High', 'Medium', 'Low', 'High', 'Medium',
                    'Low', 'High', 'Medium', 'Low', 'High'],
        'created_date': pd.date_range(start='2024-01-01', periods=10),
        'resolution_time': [pd.Timedelta(days=x) for x in [3, 5, 2, 4, 6, 1, 7, 3, 4, 2]],
        'satisfaction_score': [4.5, 3.8, 4.2, 3.5, 4.7, 3.9, 4.1, 4.8, 3.7, 4.3]
    }
    return pd.DataFrame(data)

# Function to query ticket data
def query_ticket_data(ticket_id=None, query_type='status'):
    """Query ticket information based on ticket ID"""
    df = create_dummy_ticket_data()
    
    if ticket_id:
        ticket = df[df['ticket_id'] == ticket_id]
        if ticket.empty:
            return "Ticket not found"
        
        if query_type == 'status':
            return f"""
            Ticket Details for {ticket_id}:
            Status: {ticket['status'].iloc[0]}
            Priority: {ticket['priority'].iloc[0]}
            Issue Type: {ticket['issue_type'].iloc[0]}
            Created Date: {ticket['created_date'].iloc[0].strftime('%Y-%m-%d')}
            Resolution Time: {ticket['resolution_time'].iloc[0].days} days
            Satisfaction Score: {ticket['satisfaction_score'].iloc[0]}/5
            """
        elif query_type == 'statistics':
            return f"""
            Overall Ticket Statistics:
            Total Tickets: {len(df)}
            Open Tickets: {len(df[df['status'] == 'Open'])}
            Resolved Tickets: {len(df[df['status'] == 'Resolved'])}
            Average Resolution Time: {df['resolution_time'].mean().days:.1f} days
            Average Satisfaction: {df['satisfaction_score'].mean():.1f}/5
            """
    return "Please provide a valid ticket ID"

# Existing health plan recommendation function
def recommend_health_plan(height: float, weight: float) -> str:
    """Recommends a health plan based on BMI calculation."""
    if height <= 0 or weight <= 0:
        return "Invalid input: Height and weight must be positive numbers."
    
    bmi = weight / (height ** 2)
    
    if bmi < 18.5:
        return """Option 1: Underweight Plan
        - Customized high-calorie diet plan
        - Nutritionist consultation
        - Gentle exercise routine
        - Regular health monitoring"""
    elif 18.5 <= bmi < 25:
        return """Option 2: Healthy Weight Plan
        - Balanced nutrition plan
        - Preventive health checkups
        - Fitness recommendations
        - Wellness guidance"""
    elif 25 <= bmi < 30:
        return """Option 3: Weight Management Plan
        - Specialized diet consultation
        - Regular fitness monitoring
        - Lifestyle modifications
        - Health coaching"""
    else:
        return """Option 4: Comprehensive Health Plan
        - Medical nutrition therapy
        - Personal fitness trainer
        - Regular health assessments
        - Specialist consultations"""

# Setup RAG chain
def setup_rag_chain():
    """Sets up and returns the RAG chain"""
    try:
        loader = PyPDFLoader("company_policy.pdf")
        docs = loader.load()
        
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        
        llm = ChatAnthropic(model="claude-3-haiku-20240307", max_tokens=4092)
        
        system_prompt = """
        Use the following contexts to answer questions about company policies.
        If you don't find relevant information, say that you don't know.
        
        {context}
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        return create_retrieval_chain(retriever, question_answer_chain)
    except Exception as e:
        print(f"Error setting up RAG chain: {str(e)}")
        return None

# Tool configurations
health_plan_tool = {
    "name": "health_plan_recommender",
    "description": "Health plan recommendation system based on BMI calculation.",
    "input_schema": {
        "type": "object",
        "properties": {
            "height": {"type": "number", "description": "Height in meters"},
            "weight": {"type": "number", "description": "Weight in kilograms"}
        },
        "required": ["height", "weight"]
    }
}

document_query_tool = {
    "name": "document_querier",
    "description": "Tool for querying company documents and policies.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Question about company policies"}
        },
        "required": ["query"]
    }
}

ticket_query_tool = {
    "name": "ticket_querier",
    "description": "Tool for querying ticket information and statistics.",
    "input_schema": {
        "type": "object",
        "properties": {
            "ticket_id": {"type": "string", "description": "Ticket ID to query"},
            "query_type": {"type": "string", "enum": ["status", "statistics"], "description": "Type of query"}
        },
        "required": ["ticket_id", "query_type"]
    }
}

@cl.set_chat_profiles
async def chat_profiles():
    return [
        cl.ChatProfile(
            name="General Chat",
            markdown_description="General conversation without specific tools"
        ),
        cl.ChatProfile(
            name="Health Advisor",
            markdown_description="Health plan recommendations based on BMI"
        ),
        cl.ChatProfile(
            name="Company Policies",
            markdown_description="Information about company policies"
        ),
        cl.ChatProfile(
            name="Ticket Management",
            markdown_description="Query ticket status and statistics"
        )
    ]

async def process_with_claude(prompt, profile, rag_chain=None):
    """Process input based on selected profile"""
    try:
        if profile == "General Chat":
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000
            )
            return response.content[0].text

        elif profile == "Health Advisor":
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                tools=[health_plan_tool]
            )
            if response.stop_reason == "tool_use":
                tool_use = response.content[-1]
                if tool_use.name == "health_plan_recommender":
                    return recommend_health_plan(tool_use.input["height"], tool_use.input["weight"])
            return response.content[0].text

        elif profile == "Company Policies":
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                tools=[document_query_tool]
            )
            if response.stop_reason == "tool_use" and rag_chain:
                tool_use = response.content[-1]
                if tool_use.name == "document_querier":
                    return query_document(tool_use.input["query"], rag_chain)
            return response.content[0].text

        elif profile == "Ticket Management":
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                tools=[ticket_query_tool]
            )
            if response.stop_reason == "tool_use":
                tool_use = response.content[-1]
                if tool_use.name == "ticket_querier":
                    return query_ticket_data(
                        tool_use.input["ticket_id"],
                        tool_use.input["query_type"]
                    )
            return response.content[0].text

    except Exception as e:
        return f"An error occurred: {str(e)}"

@cl.on_chat_start
async def on_chat_start():
    rag_chain = setup_rag_chain()
    cl.user_session.set("rag_chain", rag_chain)
    
    chat_profile = cl.user_session.get("chat_profile")
    welcome_messages = {
        "General Chat": "Welcome to general chat! Feel free to ask anything.",
        "Health Advisor": "Welcome to Health Advisor! I can recommend personalized health plans.",
        "Company Policies": "Welcome! I can help you find information about company policies.",
        "Ticket Management": "Welcome to Ticket Management! I can help you check ticket status and statistics for tickets TKT001 to TKT010."
    }
    
    await cl.Message(content=welcome_messages.get(chat_profile, "Welcome!")).send()

@cl.on_message
async def main(message: cl.Message):
    chat_profile = cl.user_session.get("chat_profile")
    rag_chain = cl.user_session.get("rag_chain")
    user = message.content
    history = cl.chat_context.to_openai()
    
    CHAT_PROMPT = f'''
    You are a helpful assistant in {chat_profile} mode.
    For Health Advisor: Recommend health plans based on BMI.
    For Company Policies: Find relevant policy information.
    For Ticket Management: Help with ticket queries and statistics.
    For General Chat: Engage in regular conversation.
    
    User_Question:
    {user}

    History:
    {history}
    '''
    
    response = await process_with_claude(CHAT_PROMPT, chat_profile, rag_chain)
    await cl.Message(content=response).send()

if __name__ == "__main__":
    cl.run()