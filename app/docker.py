import os
import json
from openai import OpenAI
from config.settings import OPENAI_API_KEY, SYSTEM_MESSAGE, MODEL_NAME
from app.state import add_context

# Create a client instance
client = OpenAI(
    api_key=OPENAI_API_KEY  # Uses the key from settings or environment
)

def query_openai(prompt: str, context: str = '') -> dict:
    try:
        # Ensure the system message is included in the context
        full_context = SYSTEM_MESSAGE
        if context.strip():
            full_context += f'\n{context.strip()}'

        # Prepare the messages
        messages = [
            {'role': 'system', 'content': full_context.strip()},
            {'role': 'user', 'content': prompt.strip()}
        ]

        # Call the chat completion endpoint
        response = client.chat.completions.create(
            messages=messages,
            model=MODEL_NAME
        )

        # Extract and parse the assistant's response
        ai_response = response.choices[0].message.content.strip()
        try:
            return json.loads(ai_response)
        except json.JSONDecodeError:
            return {'action': 'inquiry', 'query': 'I couldn't understand the task. Could you clarify?'}

    except Exception as e:
        # Handle unexpected errors
        return {'action': 'error', 'message': f'Error communicating with OpenAI API: {str(e)}'}
