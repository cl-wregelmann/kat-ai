import shlex
import subprocess
import logging
from typing import Optional
import threading
import queue

CONTAINER_ID: str = "kat"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class DockerShell:
    def __init__(self, container_id: str):
        self.container_id = container_id
        self.process = subprocess.Popen(
            shlex.split(f'docker exec -i {self.container_id} sh'),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line-buffered
        )
        self.stdout_queue = queue.Queue()
        self.stderr_queue = queue.Queue()
        self.alive = True

        threading.Thread(target=self._read_stdout, daemon=True).start()
        threading.Thread(target=self._read_stderr, daemon=True).start()

    def _read_stdout(self):
        for line in self.process.stdout:
            self.stdout_queue.put(line)
            logger.debug("STDOUT: %s", line.strip())

    def _read_stderr(self):
        for line in self.process.stderr:
            self.stderr_queue.put(line)
            logger.debug("STDERR: %s", line.strip())

    def exec_command(self, command: str, timeout: Optional[int] = 60) -> str:
        if not self.alive:
            logger.error("Shell session is not alive.")
            return "Error: Shell session is not alive."

        try:
            # Define a unique marker to indicate end of command
            marker = f"__CMD_END_{threading.get_ident()}__"
            full_command = f"{command}; echo {marker}"
            self.process.stdin.write(full_command + "\n")
            self.process.stdin.flush()
            logger.debug("Sent command: %s", full_command)

            output = ""
            while True:
                try:
                    line = self.stdout_queue.get(timeout=timeout)
                    if marker in line:
                        # Command execution completed
                        break
                    output += line
                except queue.Empty:
                    logger.error("Command execution timed out.")
                    return "Error: Command execution timed out."

            return output.strip()

        except Exception as e:
            logger.exception("Exception during command execution: %s", e)
            return f"Exception occurred: {str(e)}"

    def close(self):
        self.alive = False
        self.process.terminate()
        self.process.wait()
        logger.info("Closed persistent shell session.")

# Initialize a persistent shell session
persistent_shell = DockerShell(CONTAINER_ID)

def exec_command_persistent(command: str) -> str:
    return persistent_shell.exec_command(command)

def close_persistent_shell():
    persistent_shell.close()