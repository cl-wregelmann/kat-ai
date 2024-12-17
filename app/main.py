import sys
import logging
import os
import json
import time
import shlex
from openai import OpenAI
from app.assistant import assistant, client
from app.tools.execute import Handler as ExecuteHandler

# Configure logging in main.py only
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    filename="runtime/main.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def handle_tool_calls(run_data):
    """
    Handle required tool calls by executing them and returning their outputs.
    """
    # Corrected attribute access
    required_action = getattr(run_data, 'required_action', None)
    if not required_action or not getattr(required_action, 'submit_tool_outputs', None):
        logger.warning("No 'submit_tool_outputs' found in required_action.")
        return []

    tool_calls = getattr(required_action.submit_tool_outputs, 'tool_calls', [])
    if not tool_calls:
        logger.warning("No 'tool_calls' found in submit_tool_outputs.")
        return []

    tool_outputs = []

    for tc in tool_calls:
        tool_name = getattr(tc.function, 'name', None)
        arguments_str = getattr(tc.function, 'arguments', '{}')

        if not tool_name:
            logger.warning("Tool call without a name detected.")
            tool_outputs.append({
                "tool_call_id": getattr(tc, 'id', 'unknown'),
                "output": "Error: Tool name missing."
            })
            continue

        # Parse the arguments JSON string into a dictionary
        try:
            arguments = json.loads(arguments_str)
            logger.debug("Parsed arguments for tool '%s': %s", tool_name, arguments)
        except json.JSONDecodeError as e:
            logger.exception("Failed to parse arguments for tool '%s': %s", tool_name, e)
            tool_outputs.append({
                "tool_call_id": getattr(tc, 'id', 'unknown'),
                "output": f"Error: Invalid JSON arguments for tool '{tool_name}'"
            })
            continue

        # Dispatch to the correct handler based on tool_name
        if tool_name == "execute":
            command = arguments.get("command", "").strip()
            try:
                handler = ExecuteHandler({"command": command})
                result = handler.run()
                logger.debug("Executed tool '%s' with result: %s", tool_name, result)
                tool_outputs.append({
                    "tool_call_id": getattr(tc, 'id', 'unknown'),
                    "output": result
                })
            except Exception as e:
                logger.exception("Error while running tool '%s': %s", tool_name, e)
                tool_outputs.append({
                    "tool_call_id": getattr(tc, 'id', 'unknown'),
                    "output": f"Error: Failed to run tool '{tool_name}': {str(e)}"
                })
        else:
            # If we have tools not handled yet, return an error
            logger.warning("No handler implemented for tool '%s'", tool_name)
            tool_outputs.append({
                "tool_call_id": getattr(tc, 'id', 'unknown'),
                "output": f"Error: No handler implemented for tool '{tool_name}'"
            })

    # Log the tool outputs before submission
    logger.debug("Tool outputs to submit: %s", tool_outputs)

    return tool_outputs

def main():
    print("Welcome! Type 'exit' or 'quit' to end the session.\n")
    logger.info("Application started.")

    # Create a thread for this conversation
    try:
        thread = client.beta.threads.create()
        logger.info("Created thread with ID: %s", thread.id)
    except Exception as e:
        logger.exception("Failed to create thread: %s", e)
        print("Failed to create conversation thread. Please check the logs.")
        sys.exit(1)

    while True:
        try:
            user_input = input("# ")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            logger.info("Session ended by user.")
            break

        if user_input.strip().lower() in ["exit", "quit"]:
            print("Goodbye!")
            logger.info("Session ended by user.")
            break

        # Add the user message to the thread
        try:
            message = client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_input
            )
            logger.info("Added user message: %s", user_input)
        except openai.BadRequestError as e:
            logger.error("Failed to add user message: %s", e)
            print(f"Failed to add your message: {e['error']['message']}. Please try again.")
            continue
        except Exception as e:
            logger.exception("Failed to add user message: %s", e)
            print("Failed to add your message. Please check the logs.")
            continue

        # Initiate a run to process this message
        try:
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id
            )
            logger.info("Created run with ID: %s, status: %s", run.id, run.status)
        except openai.BadRequestError as e:
            logger.error("Failed to create run: %s", e)
            print(f"Failed to process your message: {e['error']['message']}. Please try again.")
            continue
        except Exception as e:
            logger.exception("Failed to create run: %s", e)
            print("Failed to process your message. Please check the logs.")
            continue

        # Handle run states until it either succeeds or fails
        # Runs may transition through multiple statuses
        max_retries = 10  # Adjust as needed
        retries = 0
        while run.status in ["queued", "running", "requires_action", "in_progress"] and retries < max_retries:
            logger.info("Current run status: %s", run.status)
            if run.status == "requires_action":
                logger.info("Run '%s' requires action: %s", run.id, run.required_action)
                tool_outputs = handle_tool_calls(run)
                if tool_outputs:
                    try:
                        run = client.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread.id,
                            run_id=run.id,
                            tool_outputs=tool_outputs
                        )
                        logger.info("Submitted tool outputs for run '%s', new status: %s", run.id, run.status)
                    except openai.BadRequestError as e:
                        logger.error("Failed to submit tool outputs for run '%s': %s", run.id, e)
                        print(f"Failed to submit tool outputs: {e['error']['message']}. Please try again.")
                        break
                    except Exception as e:
                        logger.exception("Failed to submit tool outputs for run '%s': %s", run.id, e)
                        print("Failed to submit tool outputs. Please check the logs.")
                        break
                else:
                    # If we have requires_action but no tool outputs, break or handle differently
                    logger.warning("No tool outputs found despite requires_action.")
                    break
            else:
                # If the run is queued, running, or in_progress, wait and re-fetch the run status
                time.sleep(2)  # Wait for 2 seconds before checking again
                try:
                    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                    logger.info("Refetched run '%s' status: %s", run.id, run.status)
                except openai.BadRequestError as e:
                    logger.error("Failed to retrieve run '%s': %s", run.id, e)
                    print(f"Failed to retrieve run status: {e['error']['message']}. Please try again.")
                    break
                except Exception as e:
                    logger.exception("Failed to retrieve run '%s': %s", run.id, e)
                    print("Failed to retrieve run status. Please check the logs.")
                    break
            retries += 1

        if run.status == "completed":
            # The run has completed successfully
            try:
                messages = client.beta.threads.messages.list(thread_id=thread.id).data
                assistant_msgs = [m for m in messages if m.role == 'assistant']
                if assistant_msgs:
                    final_response = assistant_msgs[-1].content
                    print(f"Assistant: {final_response}\n")
                    logger.info("Assistant final response: %s", final_response)
                else:
                    print("Assistant: [No response]\n")
                    logger.error("Run succeeded, but no assistant messages found.")
            except Exception as e:
                logger.exception("Failed to retrieve assistant messages: %s", e)
                print("Failed to retrieve assistant's response. Please check the logs.")
        else:
            # The run did not succeed after maximum retries
            print("An error occurred. Please try again.")
            logger.error("Run '%s' ended with status: %s after %d retries", run.id, run.status, retries)
            logger.debug("Run details: %s", run)

if __name__ == "__main__":
    main()