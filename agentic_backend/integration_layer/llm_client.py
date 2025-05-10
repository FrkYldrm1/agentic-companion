import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class LLMClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("❌ OPENAI_API_KEY is missing in environment variables.")
        self.client = OpenAI(api_key=api_key)

    def get_response(self, message: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a friendly AI companion for elderly users.",
                    },
                    {"role": "user", "content": message},
                ],
                temperature=0.7,
                max_tokens=200,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ LLM error: {e}")
            return "I'm sorry, I couldn't generate a response right now."
