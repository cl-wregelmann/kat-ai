import json
import logging
from openai import OpenAI
from config.settings import OPENAI_API_KEY, SYSTEM_MESSAGE, MODEL_NAME
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=OPENAI_API_KEY  # Uses the key from settings or environment
)

messages: List = [
    {"role": "system", "content": SYSTEM_MESSAGE.strip()}
]

def query_openai(prompt: str):
        
    try:

        logger.info(f'Querying OpenAI with prompt: {prompt}')

        response = client.chat.completions.create(
            messages=messages+[{"role": "user", "content": prompt}],
            model=MODEL_NAME,
            response_format={type: json_object}
        )

        ai_response = response.choices[0].message.content.strip()

        try:
            return json.loads(ai_response)
        except json.JSONDecodeError:
            return {"action": "inquiry", "query": ai_response}

    except Exception as e:
        logger.error(f'Error communicating with OpenAI API: {str(e)}')
        return {"action": "inquiry", "query": str(e)}

def add_message(role: str, content: str) -> None:
    messages.append({"role": role, "content": content})