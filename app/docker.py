import shlex
import subprocess

def execute_docker_command_safe(command: str) -> str:
    try:
        parsed_command = shlex.split(command)
        process = subprocess.Popen(
            parsed_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        output_lines = []
        print("Executing Docker command:")
        while True:
            line = process.stdout.readline()
            if line:
                print(line, end="")
                output_lines.append(line)
            elif process.poll() is not None:
                break

        stderr = process.stderr.read()
        if process.returncode != 0:
            return f"Error: {stderr.strip()}"

        return ''.join(output_lines).strip()
    except Exception as e:
        return f"Exception occurred: {str(e)}"

def list_containers(all_containers: bool = False) -> str:
    command = "docker ps"
    if all_containers:
        command += " -a"
    return execute_docker_command_safe(command)

def start_container(container_name: str) -> str:
    return execute_docker_command_safe(f"docker start {container_name}")

def stop_container(container_name: str) -> str:
    return execute_docker_command_safe(f"docker stop {container_name}")

def remove_container(container_name: str) -> str:
    return execute_docker_command_safe(f"docker rm {container_name}")