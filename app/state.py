from typing import Dict, List

task_state: Dict[str, any] = {
    "context": "",
    "completed_steps": [],
    "next_step": ""
}

def update_task_state(ai_response: str) -> None:
    if task_state["next_step"]:
        task_state["completed_steps"].append(task_state["next_step"])

    task_state["context"] += f"\\nAI Response: {ai_response}"
    task_state["next_step"] = ai_response

def reset_task_state() -> None:
    task_state["context"] = ""
    task_state["completed_steps"] = []
    task_state["next_step"] = ""

def add_context(additional_context: str) -> None:
    task_state["context"] += f"\\n{additional_context}"

def get_context() -> str:
    return task_state["context"]

def get_next_step() -> str:
    return task_state["next_step"]

def get_completed_steps() -> List[str]:
    return task_state["completed_steps"]