import shlex
import subprocess
import logging
from typing import Optional

CONTAINER_ID: str = "kat"
WORKING_DIR: str = "/app"  # Use uppercase for constants

# Configure a separate logger for this module
logger = logging.getLogger(__name__)

def exec_command(command: str) -> str:
    """
    Executes a shell command inside a specified Docker container.

    Args:
        command (str): The shell command to execute.

    Returns:
        str: The output of the command or an error message.
    """
    try:
        # Construct the Docker command without '-it' for non-interactive execution
        docker_command = f"docker exec -w {WORKING_DIR} {CONTAINER_ID} {command}"
        args = shlex.split(docker_command)
        logger.debug("Executing Docker command: %s", docker_command)

        # Execute the command
        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60  # Prevent hanging indefinitely
        )

        if result.returncode != 0:
            logger.error("Docker command error: %s", result.stderr.strip())
            return f"Error: {result.stderr.strip()}"

        logger.debug("Docker command output: %s", result.stdout.strip())
        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        logger.exception("Docker command timed out.")
        return "Error: Command execution timed out."
    except Exception as e:
        logger.exception("Exception occurred while executing Docker command: %s", e)
        return f"Exception occurred: {str(e)}"


def put_file(path: str, content: str) -> str:
    """
    Writes content to a specified file path.

    Args:
        path (str): The file path to write to.
        content (str): The content to write.

    Returns:
        str: Confirmation message.
    """
    try:
        with open(path, "w") as file:
            file.write(content)
        logger.info("File %s updated successfully.", path)
        return f"Updated {path}"
    except Exception as e:
        logger.exception("Failed to write to file %s: %s", path, e)
        return f"Error: Failed to update {path}"