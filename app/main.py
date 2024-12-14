from app.ai import query_openai
from app.docker import execute_docker_command_safe
from app.state import task_state, update_task_state
from config.settings import CONTAINER_NAME  # Import container name
import shlex

def main():
    print("Welcome to the Agentic AI App")

    while True:
        # Step 1: Get user input
        user_prompt = input("Enter your task or type 'exit' to quit: ")
        if user_prompt.lower() == "exit":
            print("Exiting...")
            break

        # Step 2: Ask the AI for suggestions based on the prompt
        task_state["context"] += f"\nUser prompt: {user_prompt}"
        ai_response = query_openai(user_prompt, task_state["context"])

        while True:  # Loop to execute commands until the AI completes the task
            # Step 3: Handle the AI response based on its action
            action = ai_response.get("action")

            if action == "execute":
                command = ai_response.get("command", "").strip()
                if command:
                    # Handle here documents separately
                    if "<<" in command:
                        full_command = f'docker exec {CONTAINER_NAME} /bin/bash -c "{command}"'
                    else:
                        # Regular command execution
                        full_command = f'docker exec {CONTAINER_NAME} /bin/bash -c "{command}"'

                    print(f"\nExecuting: {full_command}")
                    output = execute_docker_command_safe(full_command)
                    print(f"\nCommand Output:\n{output}")

                    # Update context with output
                    task_state["context"] += f"\nCommand executed: {command}\nOutput:\n{output}"
                    ai_response = query_openai("", task_state["context"])  # Re-query OpenAI for next step
                    continue

            elif action == "inquiry":
                # Ask the user for more clarification
                query = ai_response.get("query", "Could you clarify your task?")
                print(f"\nThe AI needs more information: {query}")
                task_state["context"] += f"\nAI inquiry: {query}"
                break

            elif action == "complete":
                # Task complete, but the app continues running
                message = ai_response.get("message", "Task complete.")
                print(f"\n{message}\nYou can enter a new task to continue.")

                # Update the task state to reflect the completion
                task_state["context"] += f"\nTask complete: {message}\n"
                break  # Exit the inner loop to allow the user to input a new task

            else:
                print("\nUnexpected response from the AI. Please try again.")
                break

if __name__ == "__main__":
    main()