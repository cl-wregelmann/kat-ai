from app.ai import query_openai, add_message
from app.docker import exec, put_file

def main():
    print("Welcome to the Agentic AI App")

    while True:
        # Step 1: Get user input
        user_input = input("> ")

        # Step 2: Ask the AI for suggestions based on the prompt
        ai_response = query_openai(user_input)
        add_message('user', user_input)

        while True:  # Loop to execute commands until the AI completes the task
            # Step 3: Handle the AI response based on its action
            action = ai_response.get("action")

            if action == "execute":
                command = ai_response.get("command", "").strip()
                dir = exec('pwd')
                if command:
                    print(f"\n{dir}# {command}")
                    output = exec(command)
                    print(f"\n{output}")
                    add_message('system', f"{dir}# {command}\n{output}")
                    ai_response = query_openai("Please continue")
                    continue

            elif action == "put_file":
                path = ai_response.get('path')
                content = ai_response.get('content')
                if path and content:
                    put_file(path, content)
                    add_message('system', f"Updated {path}:\n\n{content}")
                    ai_response = query_openai("What should we do next?")
                    continue
                break

            elif action == "inquiry":
                # Ask the user for more clarification
                query = ai_response.get("query", "Could you clarify your task?")
                add_message('assistant', query)
                print(f"\n{query}")
                break

            elif action == "complete":
                # Task complete, but the app continues running
                message = ai_response.get("message", "Task complete.")
                add_message('assistant', query)
                print(f"\n{message}")
                break  # Exit the inner loop to allow the user to input a new task

            else:
                print(ai_response)
                break

if __name__ == "__main__":
    main()