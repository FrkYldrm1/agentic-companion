import os
from openai import OpenAI
from dotenv import load_dotenv
import traceback

# ✅ Force-load .env from correct path
from pathlib import Path

dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)


class LLMClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        print(f"🔍 Loaded OPENAI_API_KEY: {api_key}")  # Diagnostic print

        if not api_key or not api_key.startswith("sk-"):
            raise ValueError(f"❌ Invalid or missing OPENAI_API_KEY: {api_key}")
        self.client = OpenAI(api_key=api_key)

    def get_response(self, message: str) -> str:
        try:
            print(f"📨 Sending message to OpenAI: {message}")
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
            reply = response.choices[0].message.content.strip()
            print(f"✅ OpenAI reply: {reply}")
            return reply

        except Exception as e:
            print("❌ LLM error occurred!")
            traceback.print_exc()
            return "I'm sorry, I couldn't generate a response right now."
