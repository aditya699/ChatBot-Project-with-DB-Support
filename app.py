import os
import chainlit as cl
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables from .env file
load_dotenv()

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

async def process_with_claude(prompt):
    """
    Process the input with Claude and the health plan tool.
    """
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

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            tools=[health_plan_tool]
        )

        if response.stop_reason == "tool_use":
            tool_use = response.content[-1]
            tool_input = tool_use.input

            if tool_name := tool_use.name == "health_plan_recommender":
                height = tool_input["height"]
                weight = tool_input["weight"]
                
                result = recommend_health_plan(height, weight)
                return f"Based on your height ({height}m) and weight ({weight}kg), here's your recommendation:\n{result}"
        
        return response.content[0].text

    except Exception as e:
        return f"An error occurred: {str(e)}"

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
            message="Can help with leave Policy",
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

@cl.on_chat_start
def on_chat_start():
    print("A new chat session has started!")

@cl.on_message
async def main(message: cl.Message):
    user = message.content
    history = cl.chat_context.to_openai()
    
    CHAT_PROMPT = f'''
    You are a helpful assistant that provides health plan recommendations and answers general queries.
    
    User_Question:
    {user}

    History:
    {history}
    '''
    
    # Process the message using Claude and the health plan tool
    response = await process_with_claude(CHAT_PROMPT)
    
    # Send the response back to the user
    await cl.Message(content=response).send()