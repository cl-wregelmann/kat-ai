import shlex
import subprocess
from config.settings import CONTAINER_NAME 

def exec(command: str) -> str:
    try:

        process = subprocess.Popen(
            shlex.split(f'docker exec {CONTAINER_NAME} /bin/bash -c "{command}"'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        output_lines = []
        while True:
            line = process.stdout.readline()
            if line:
                output_lines.append(line)
            elif process.poll() is not None:
                break

        stderr = process.stderr.read()
        if process.returncode != 0:
            return f"Error: {stderr.strip()}"

        return ''.join(output_lines).strip()
    
    except Exception as e:
        return f"Exception occurred: {str(e)}"