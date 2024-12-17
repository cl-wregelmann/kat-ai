from typing import Dict
from app.helpers.docker_helper import exec_command_persistent
import logging

logger = logging.getLogger(__name__)

class Handler:
    def __init__(self, params: Dict):
        self.command = params.get("command")
        if not self.command:
            raise ValueError("No command provided")

    def run(self) -> str:
        dir = exec_command_persistent("pwd")
        print(f"{dir}> {self.command}")
        logger.debug(f"Executing command: {self.command}")
        try:
            result = exec_command_persistent(self.command)
            print(f"{result}\n")
            logger.debug(f"Command result: {result}")
            return result
        except Exception as e:
            error_message = str(e).strip()
            print(f"Error: {error_message}\n")
            logger.error(f"Error executing command '{self.command}': {error_message}")
            return f"Error: {error_message}"

# Correctly structured tool definition with 'function' key
tool = {
    "type": "function",
    "function": {
        "name": "execute",
        "description": "Executes a shell command inside a Docker container",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute inside the Docker container"
                }
            },
            "required": ["command"]
        }
    }
}