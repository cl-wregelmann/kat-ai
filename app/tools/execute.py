from typing import Dict
from app.helpers import docker

class Handler:
    def __init__(self, params: Dict):
        self.command = params.get("command")
        if not self.command:
            raise ValueError("No command provided")

    def run(self) -> str:
        try:
            result = docker.exec(self.command)
            return f"> {self.command}\n{result}"
        except Exception as e:
            return f"> {self.command}\nError: {str(e)}"

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