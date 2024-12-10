from anthropic import Anthropic

def get_claude_response_sync(question):
    try:
        client = Anthropic()
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=150,
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ]
        )
        return {
            "question": question,
            "answer": response.content[0].text,
            "status": "success"
        }
    except Exception as e:
        return {
            "question": question,
            "answer": None,
            "status": "error",
            "error": str(e)
        }

def main_sync():
    questions = [
        "What is Python? Answer in one sentence.",
        "What is JavaScript? Answer in one sentence.",
        "What is Java? Answer in one sentence."
    ]
    
    # Process one question at a time
    for question in questions:
        print("\n" + "="*50)
        result = get_claude_response_sync(question)
        print(f"Question: {result['question']}")
        if result['status'] == 'success':
            print(f"Answer: {result['answer']}")
        else:
            print(f"Error: {result['error']}")

if __name__ == "__main__":
    main_sync()