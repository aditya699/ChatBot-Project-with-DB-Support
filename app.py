import os
import chainlit as cl
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

# Load environment variables from .env file
load_dotenv()
ANTHROPIC_API_KEY=os.getenv("ANTHROPIC_API_KEY")

llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0,
    max_tokens=4092,
    timeout=None,
    max_retries=2,
    api_key=ANTHROPIC_API_KEY
    # other params...
)


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="General Company Policies",
            message="Can help with leave Policy",
            icon="/public/policy.svg",
            ),

        cl.Starter(
            label="General Tickets Information",
            message="Can help you with all Customer Related Information",
            icon="/public/tickets.PNG",
            ),
        cl.Starter(
            label="Can you help me with general Query",
            message="What is AI?",
            icon="/public/query.PNG",
            )
        ]

@cl.on_chat_start
def on_chat_start():
    print("A new chat session has started!")

@cl.on_message
async def main(message: cl.Message):

    user=message.content
    history=cl.chat_context.to_openai()
    CHAT_PROMPT=f'''
    You are a helpful assitant that helps people
    User_Question:
    {user}

    History:
    {history}

    '''
    print(history)
    print(CHAT_PROMPT)

    

    # response="The Bot is under Development"
    response=llm.invoke(CHAT_PROMPT).content

    # Send a response back to the user
    await cl.Message(
        content=f"Received: {response}",
    ).send()
