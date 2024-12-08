import os
import chainlit as cl
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables from .env file
load_dotenv()

# Initialize Anthropic client
client = Anthropic()

def recommend_health_plan_india(height: float, weight: float) -> str:
    """
    Recommends a health plan based on BMI calculated from height and weight for Indian citizens.
    """
    if height <= 0 or weight <= 0:
        return "Invalid input: Height and weight must be positive numbers."
    
    bmi = weight / (height ** 2)
    
    if bmi < 18.5:
        return """Option 1: Indian Underweight Plan
        - Customized diet plan with high-calorie Indian foods
        - Ayurvedic supplements consultation
        - Yoga and light exercise routine
        - Quarterly health check-ups
        - Coverage for nutritionist visits"""
    elif 18.5 <= bmi < 25:
        return """Option 2: Indian Healthy Weight Plan
        - Balanced diet plan with traditional Indian nutrition
        - Preventive health checkups
        - Yoga and meditation sessions
        - Annual wellness assessment
        - Basic health insurance coverage"""
    elif 25 <= bmi < 30:
        return """Option 3: Indian Weight Management Plan
        - Specialized Indian diet consultation
        - Regular fitness monitoring
        - Stress management through yoga
        - Quarterly health assessments
        - Enhanced health insurance coverage"""
    else:
        return """Option 4: Indian Comprehensive Health Plan
        - Medical nutrition therapy
        - Personal fitness trainer
        - Regular health monitoring
        - Specialist consultations
        - Premium health insurance coverage"""

def recommend_health_plan_uk(height: float, weight: float) -> str:
    """
    Recommends a health plan based on BMI calculated from height and weight for UK residents.
    """
    if height <= 0 or weight <= 0:
        return "Invalid input: Height and weight must be positive numbers."
    
    bmi = weight / (height ** 2)
    
    if bmi < 18.5:
        return """Option 1: UK Underweight Plan
        - NHS-aligned nutrition guidance
        - Private dietitian consultations
        - Gentle exercise programs
        - Regular GP check-ups
        - Basic private health coverage"""
    elif 18.5 <= bmi < 25:
        return """Option 2: UK Wellness Plan
        - Regular health screenings
        - Gym membership
        - Nutritional guidance
        - Mental health support
        - Standard private health coverage"""
    elif 25 <= bmi < 30:
        return """Option 3: UK Weight Management Plan
        - Specialized nutrition support
        - Personal training sessions
        - Behavioral therapy options
        - Comprehensive health checks
        - Enhanced private health coverage"""
    else:
        return """Option 4: UK Comprehensive Care Plan
        - Full medical assessment
        - Specialist referrals
        - Customized exercise program
        - Mental health support
        - Premium private health coverage"""

@cl.set_chat_profiles
async def chat_profiles():
    return [
        cl.ChatProfile(
            name="India",
            markdown_description="Health plans tailored for Indian residents with focus on traditional wellness approaches",
         
        ),
        cl.ChatProfile(
            name="United Kingdom",
            markdown_description="Health plans designed for UK residents aligned with NHS guidelines",
           
        ),
    ]

async def process_with_claude(prompt, country):
    """
    Process the input with Claude and the country-specific health plan tool.
    """
    health_plan_tool = {
        "name": "health_plan_recommender",
        "description": f"A health plan recommendation system that suggests plans based on BMI calculation for {country} residents.",
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
                
                if country == "India":
                    result = recommend_health_plan_india(height, weight)
                else:
                    result = recommend_health_plan_uk(height, weight)
                    
                return f"Based on your height ({height}m) and weight ({weight}kg), here's your {country}-specific recommendation:\n{result}"
        
        return response.content[0].text

    except Exception as e:
        return f"An error occurred: {str(e)}"

@cl.on_chat_start
async def on_chat_start():
    chat_profile = cl.user_session.get("chat_profile")
    await cl.Message(
        content=f"Welcome! You've selected the {chat_profile} health plan advisor. I'll provide health recommendations tailored for {chat_profile} residents. How can I help you today?"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    chat_profile = cl.user_session.get("chat_profile")
    user = message.content
    history = cl.chat_context.to_openai()
    
    CHAT_PROMPT = f'''
    You are a helpful assistant that provides health plan recommendations for {chat_profile} residents.
    
    User_Question:
    {user}

    History:
    {history}
    '''
    
    # Process the message using Claude and the health plan tool
    response = await process_with_claude(CHAT_PROMPT, chat_profile)
    
    # Send the response back to the user
    await cl.Message(content=response).send()