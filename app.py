import os
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
os.environ["GOOGLE_API_KEY"] =os.getenv("GEMINI_API_KEY")

# Initialize Anthropic client
client = Anthropic()

def recommend_health_plan(height: float, weight: float) -> str:
    """
    Recommends a health plan based on BMI calculated from height and weight.
    """
    if height <= 0 or weight <= 0:
        return "Invalid input: Height and weight must be positive numbers."
    
    bmi = weight / (height ** 2)
    
    if bmi < 18.5:
        return "Option 1: Underweight plan"
    elif 18.5 <= bmi < 25:
        return "Option 2: Healthy weight plan"
    elif 25 <= bmi < 30:
        return "Option 3: Overweight plan"
    else:
        return "Option 4: Obesity plan"

def query_document(user_query: str) -> str:
    """
    Queries the document based on user's question using RAG.
    """
    try:
        # Initialize RAG components
        loader = PyPDFLoader("company_policy.pdf")
        docs = loader.load()
        
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=500)
        splits = text_splitter.split_documents(docs)
        
        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
        retriever = vectorstore.as_retriever()
        
        llm = ChatAnthropic(model="claude-3-haiku-20240307", max_tokens=4092)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            Use the following context to answer the question. 
            If you don't know the answer, say that you don't know.
            
            {context}
            """),
            ("human", "{input}"),
        ])
        
        # Create and execute the chain
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        
        result = rag_chain.invoke({"input": user_query})
        return result["context"][0].page_content
    
    except Exception as e:
        return f"Error processing query: {str(e)}"

# Tool configurations
health_plan_tool = {
    "name": "health_plan_recommender",
    "description": "A health plan recommendation system that suggests plans based on BMI calculation.",
    "input_schema": {
        "type": "object",
        "properties": {
            "height": {
                "type": "number",
                "description": "The person's height in meters."
            },
            "weight": {
                "type": "number",
                "description": "The person's weight in kilograms."
            }
        },
        "required": ["height", "weight"]
    }
}

document_query_tool = {
    "name": "document_querier",
    "description": "A tool for querying company documents and policies using RAG.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The question to ask about company policies or documents."
            }
        },
        "required": ["query"]
    }
}

async def process_with_claude(prompt):
    """
    Process the input with Claude using both tools.
    """
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
            tools=[health_plan_tool, document_query_tool]
        )

        if response.stop_reason == "tool_use":
            tool_use = response.content[-1]
            tool_input = tool_use.input

            if tool_use.name == "health_plan_recommender":
                height = tool_input["height"]
                weight = tool_input["weight"]
                return recommend_health_plan(height, weight)
            
            elif tool_use.name == "document_querier":
                return query_document(tool_input["query"])
        
        return response.content[0].text

    except Exception as e:
        return f"An error occurred: {str(e)}"

@cl.on_chat_start
def on_chat_start():
    print("A new chat session has started!")

@cl.on_message
async def main(message: cl.Message):
    user = message.content
    history = cl.chat_context.to_openai()
    
    CHAT_PROMPT = f'''
    You are a helpful assistant that provides health plan recommendations and answers queries about company policies.
    When a health plan recommendations questions comes invoke health_plan_tool.
    When a company related question invoke document_query_tool.
    User_Question:
    {user}

    History:
    {history}
    '''
    
    response = await process_with_claude(CHAT_PROMPT)
    await cl.Message(content=response).send()

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Health Plan Recommendation",
            message="I need a health plan recommendation. I'm 1.75m tall and weigh 70kg.",
            icon="/public/policy.svg"
        ),
        cl.Starter(
            label="General Company Policies",
            message="Can you help me with leave Policy",
            icon="/public/policy.svg",
        ),
        cl.Starter(
            label="General Tickets Information",
            message="Can help you with all Customer Related Information",
            icon="/public/tickets.PNG",
        ),
        cl.Starter(
            label="Can you help me with general query",
            message="What is AI?",
            icon="/public/query.PNG",
        )
    ]

if __name__ == "__main__":
    cl.run()