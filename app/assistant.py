import os
import logging
import importlib
from openai import OpenAI
import app.config

logger = logging.getLogger(__name__)

def load_tools():
    tools = []
    tools_dir = os.path.join(os.path.dirname(app.config.__file__), "tools")
    if os.path.isdir(tools_dir):
        for filename in os.listdir(tools_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                module_name = filename[:-3]
                try:
                    mod = importlib.import_module(f"app.tools.{module_name}")
                    if hasattr(mod, "tool"):
                        tools.append(mod.tool)
                    else:
                        logger.warning(f"Module {module_name} does not have a 'tool' attribute.")
                except Exception as e:
                    logger.exception("Error loading tool %s: %s", module_name, e)
    else:
        logger.error(f"Tools directory not found: {tools_dir}")
    return tools

def initialize_assistant(client: OpenAI):
    tools = load_tools()
    try:
        assistant_obj = client.beta.assistants.create(
            name=app.config.ASSISTANT_NAME,
            instructions=app.config.INSTRUCTIONS,
            model=app.config.MODEL,
            tools=tools
        )
        logger.info("Assistant created with ID: %s", assistant_obj.id)
        return assistant_obj
    except Exception as e:
        logger.exception("Failed to create assistant: %s", e)
        raise

# Initialize the OpenAI client once, using the API key from config or environment variable.
api_key = app.config.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("No OpenAI API key found. Set OPENAI_API_KEY in config or as an environment variable.")

client = OpenAI(api_key=api_key)
assistant = initialize_assistant(client)

def get_assistant():
    return assistant