import asyncio
import time
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables from .env file
load_dotenv()

# Initialize Anthropic client
client = Anthropic()

# Semaphore for controlling concurrent API calls
SEM = asyncio.Semaphore(5)

# Synchronous version - processes one at a time
def classify_text_sync(prompt: str) -> dict:
    """Classify text synchronously (one at a time)"""
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
        classification = response.content[0].text.strip().lower()
        return {"text": prompt, "classification": classification}
    except Exception as e:
        return {"text": prompt, "classification": "Error", "error": str(e)}

# Asynchronous version - processes concurrently
async def classify_text_async(prompt: str) -> dict:
    """Classify text asynchronously (allowing concurrent processing)"""
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
            classification = response.content[0].text.strip().lower()
            return {"text": prompt, "classification": classification}
        except Exception as e:
            return {"text": prompt, "classification": "Error", "error": str(e)}

def run_sync_version(prompts):
    """Run the synchronous version and measure time"""
    print("\nRunning synchronous version...")
    start_time = time.time()
    
    results = []
    for prompt in prompts:
        result = classify_text_sync(prompt)
        results.append(result)
        print(f"Processed: {result}")
    
    end_time = time.time()
    print(f"\nSynchronous version took {end_time - start_time:.2f} seconds")
    return results

async def run_async_version(prompts):
    """Run the asynchronous version and measure time"""
    print("\nRunning asynchronous version...")
    start_time = time.time()
    
    tasks = [classify_text_async(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks)
    
    for result in results:
        print(f"Processed: {result}")
    
    end_time = time.time()
    print(f"\nAsynchronous version took {end_time - start_time:.2f} seconds")
    return results

async def main():
    # Test data
    prompts = [
        "I loved the product, it was fantastic!",
        "This is the worst service I have ever received.",
        "The experience was neutral, neither good nor bad.",
        "Highly recommend this to everyone!",
        "I would not buy this again.",
        "The quality could have been better.",
        "This was an amazing experience!"
    ]
    
    # Run both versions for comparison
    sync_results = run_sync_version(prompts)
    async_results = await run_async_version(prompts)

if __name__ == "__main__":
    asyncio.run(main())