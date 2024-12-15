import json
from openai import OpenAI
from config.settings import OPENAI_API_KEY, SYSTEM_MESSAGE, MODEL_NAME
from typing import List

client = OpenAI(
    api_key=OPENAI_API_KEY  # Uses the key from settings or environment
)

messages: List = [
    {"role": "system", "content": SYSTEM_MESSAGE.strip()}
]

def query_openai(prompt: str, context: str = "") -> dict:
    try:

        response = client.chat.completions.create(
            messages=messages,
            model=MODEL_NAME,
            response_format={"type": "json_object"}
        )

        ai_response = response.choices[0].message.content.strip()

        try:
            return json.loads(ai_response)
        except json.JSONDecodeError:
            return {"action": "inquiry", "query": ai_response}

    except Exception as e:
        # Handle unexpected errors
        return {"action": "error", "message": f"Error communicating with OpenAI API: {str(e)}"}
    
def add_message(role: str, content: str) -> None:
    messages.append({"role": role, "content": content})