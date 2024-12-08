from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

def recommend_health_plan(height: float, weight: float) -> str:
    """
    Recommends a health plan based on BMI calculated from height and weight.
    
    Args:
        height (float): Height in meters.
        weight (float): Weight in kilograms.

    Returns:
        str: Recommended health plan.
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

def prompt_claude(prompt, client):
    """
    Sends a prompt to Claude and handles the response.
    
    Args:
        prompt (str): User's input prompt
        client: Anthropic client instance
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
            tool_name = tool_use.name
            tool_input = tool_use.input

            if tool_name == "health_plan_recommender":
                print("Processing health plan recommendation...")
                height = tool_input["height"]
                weight = tool_input["weight"]

                try:
                    result = recommend_health_plan(height, weight)
                    print(f"Recommended Health Plan: {result}")
                except ValueError as e:
                    print(f"Error in health plan calculation: {str(e)}")

        elif response.stop_reason == "end_turn":
            print("Claude's response:")
            print(response.content[0].text)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

def main():
    """
    Main function to run the chatbot loop.
    """
    print("Welcome to the Health Plan Chatbot!")
    print("Type 'quit' or 'exit' to end the conversation.")
    
    client = Anthropic()
    
    while True:
        # Get user input
        user_input = input("\nYou: ").strip()
        
        # Check for exit conditions
        if user_input.lower() in ['quit', 'exit']:
            print("Thank you for using the Health Plan Chatbot. Goodbye!")
            break
        
        # Skip empty inputs
        if not user_input:
            print("Please enter a valid query.")
            continue
        
        # Process the input
        print("\nBot: ")
        prompt_claude(user_input, client)

if __name__ == "__main__":
    main()