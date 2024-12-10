

import asyncio
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables from .env file
load_dotenv()

# Initialize Anthropic client
client = Anthropic()

SEM = asyncio.Semaphore(5)  # Limit to 5 concurrent API calls

async def classify_text(prompt: str) -> dict:
    """Classify text as positive or negative using the Anthropic Claude API."""
    async with SEM:  # Limit concurrency
        try:
            classification_prompt = (
                f"Classify the following text as positive or negative sentiment: \"{prompt}\". "
                "Reply with 'positive' or 'negative' only."
            )
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                messages=[{"role": "user", "content": classification_prompt}],
                max_tokens=10,
                tools=[]
            )
            
            # Access the text of the first message
            classification = response.content[0].text.strip().lower()
            return {"text": prompt, "classification": classification}
        except Exception as e:
            return {"text": prompt, "classification": "Error", "error": str(e)}

async def main():
    prompts = [
        "I loved the product, it was fantastic!",
        "This is the worst service I have ever received.",
        "The experience was neutral, neither good nor bad.",
        "Highly recommend this to everyone!",
        "I would not buy this again.",
        "The quality could have been better.",
        "This was an amazing experience!"
    ]

    tasks = [classify_text(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks)

    for result in results:
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
