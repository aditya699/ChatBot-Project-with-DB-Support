import asyncio
from anthropic import Anthropic
import time

# Configure for 50 RPM limit - let's use 45 to be safe
SEM = asyncio.Semaphore(45)  # Allow up to 45 concurrent requests

async def analyze_sentiment(client, text, number, total):
    async with SEM:
        try:
            before_call = time.time()
            
            # Note: Asking for just positive/negative for faster, shorter responses
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,  # Reduced tokens since we need only one word
                messages=[
                    {
                        "role": "user",
                        "content": f"Classify as only 'positive' or 'negative': '{text}'"
                    }
                ]
            )
            
            after_call = time.time()
            sentiment = response.content[0].text.strip().lower()
            
            return {
                "text": text,
                "sentiment": sentiment,
                "time": after_call - before_call,
                "number": number
            }
            
        except Exception as e:
            return {
                "text": text,
                "error": str(e),
                "number": number
            }

async def main():
    start_time = time.time()
    client = Anthropic()
    
    # Test texts - mix of clearly positive and negative statements
    texts = [
        "I love this product!",
        "This is terrible service.",
        "Amazing experience!",
        "Worst purchase ever.",
        "Highly recommended!",
        "Complete waste of money.",
        "Outstanding quality!",
        "Very disappointed.",
        "Excellent work!",
        "Do not buy this.",
        # Add more to test scaling...
    ] * 4  # Multiply to get 40 items

    print(f"Processing {len(texts)} texts...")
    print(f"Maximum concurrent requests: {SEM._value}")
    
    tasks = [
        analyze_sentiment(client, text, i+1, len(texts))
        for i, text in enumerate(texts)
    ]
    
    results = await asyncio.gather(*tasks)
    results.sort(key=lambda x: x['number'])  # Sort by original order
    
    # Calculate statistics
    total_api_time = sum(r['time'] for r in results if 'time' in r)
    successful = len([r for r in results if 'sentiment' in r])
    errors = len([r for r in results if 'error' in r])
    
    # Print results
    for result in results:
        if 'sentiment' in result:
            print(f"\nText {result['number']}: {result['text']}")
            print(f"Sentiment: {result['sentiment']}")
            print(f"API Time: {result['time']:.2f}s")
        else:
            print(f"\nText {result['number']} Error: {result['error']}")
    
    # Print summary
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n" + "="*50)
    print("Performance Summary:")
    print(f"Total texts processed: {len(texts)}")
    print(f"Successful analyses: {successful}")
    print(f"Errors: {errors}")
    print(f"Total wall clock time: {total_time:.2f} seconds")
    print(f"Total API time (sum of all calls): {total_api_time:.2f} seconds")
    print(f"Average time per text: {total_time/len(texts):.2f} seconds")
    print(f"Parallel efficiency gain: {(total_api_time - total_time)/total_api_time*100:.1f}%")

if __name__ == "__main__":
    asyncio.run(main())