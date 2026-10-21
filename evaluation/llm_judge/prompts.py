from __future__ import annotations
from pathlib import Path

from .utils import (
    extract_actions_from_history, 
    extract_actions_of_sm, 
    extract_actions_of_oh, 
    extract_actions_of_ag
)


system_prompt_IF_sm = """
You are an expert evaluator of instruction-following for coding tasks.

Your role is to determine whether an agent strictly follows a given set of requirements. 
Be precise, strict, and objective.

You will be given:
1. A coding task (problem description and requirements)
2. A sequence of code blocks enclosed in <code> ... </code>, representing the agent's actions or generated code

Evaluation criteria: **All stated requirements must be fully satisfied.**

Please carefully reason step by step about the points. At the end, provide the final answer in the following format:

<ANSWER>YES</ANSWER>
- if ALL requirements are satisfied and the actions correctly fulfill the task

<ANSWER>NO</ANSWER>
- if ANY requirement is not satisfied
"""


system_prompt_IF_oh = """
You are an expert evaluator of instruction-following for coding tasks.

Your role is to determine whether an agent strictly follows a given set of requirements. 
Be precise, strict, and objective.

You will be given:
1. A coding task (problem description and requirements)
2. A transcript of the agent's execution process, including its actions, tool usage, and reasoning steps.
In this transcript, entries written as ...(placeholder) (if any) indicate that the agent performed the corresponding operation using a long or omitted string/value. 
The placeholder is evidence that the operation occurred, even if the full content is abbreviated.

Evaluation criteria: **All stated requirements must be fully satisfied.**

Please reason step by step before deciding. At the end, provide the final answer in exactly one of the following formats:

<ANSWER>YES</ANSWER>
- if ALL requirements are satisfied and the actions correctly fulfill the task

<ANSWER>NO</ANSWER>
- if ANY requirement is not satisfied
"""

system_prompt_IF_ag = """
You are an expert evaluator of instruction-following for coding tasks.

Your role is to determine whether an agent strictly follows a given set of requirements. 
Be precise, strict, and objective.

You will be given:
1. A coding task (problem description and requirements)
2. A transcript of the agent's execution process, including its actions, tool usage, and reasoning steps.

Evaluation criteria: **All stated requirements must be fully satisfied.**

Please reason step by step before deciding. At the end, provide the final answer in exactly one of the following formats:

<ANSWER>YES</ANSWER>
- if ALL requirements are satisfied and the actions correctly fulfill the task

<ANSWER>NO</ANSWER>
- if ANY requirement is not satisfied
"""


system_prompt_READ_sm = """
You are a code analysis assistant. You are given:

* A list of file paths
* A set of code blocks, each is wrapped by `<code>` and `</code>`

Your task is to determine whether the code blocks contain actions that read the **contents of every file in the given list**.
A read action is any operation that accesses the contents of a file for reading purposes. This includes, but is not limited to:

* Function calls such as `read_file(...)`, `open(..., 'r')`, `open(...)` (default read mode), `.read()`, `.readlines()`
* Library or framework utilities that read file contents
* Custom functions or indirect calls that clearly imply reading a file

Provide your final answer as exactly one of the following:

* `<ANSWER>YES</ANSWER>` — if **all** files are read
* `<ANSWER>NO</ANSWER>` — if **any** file is not read
"""

system_prompt_READ_oh = """
You are a code analysis assistant. You are given:

1. A list of target file paths
2. A text block containing agent action logs. Each log entry represents an agent action and may include structured fields such as command, path, message, action kind, ranges, or other metadata.

Your task is to determine whether the log shows that **the contents of EVERY target file were inspected**.

A file is considered inspected only when the log explicitly shows an action whose purpose is reading, viewing, opening, searching within, loading, or otherwise accessing that file's contents.

Examples of actions that count as inspection include:

- File editor actions such as `view`
- Terminal commands that read file contents, such as `cat`, `less`, `head`, `tail`
- Search commands that inspect file contents, such as `grep`, `ripgrep`, or similar content-search tools targeting the file
- Any other explicit action that clearly accesses file contents

Actions that do **not** count as inspection unless they also explicitly read contents include:

- `str_replace`
- write/edit/patch actions
- create/delete/rename/move actions
- `find`, `ls`, or directory listing commands
- references to file paths only
- summary or finish messages

Provide your final answer as exactly one of the following:

* `<ANSWER>YES</ANSWER>` — if **all** files are read
* `<ANSWER>NO</ANSWER>` — if **any** file is not read
"""

system_prompt_READ_ag = """
You are a code analysis assistant. You are given:

1. A list of target file paths
2. A text block containing assistant tool-call logs. Each log entry represents an assistant action and may include structured records such as tool IDs, function names, arguments, action types, or indices.

Your task is to determine whether the log shows that **the contents of EVERY target file were inspected (read)**.

A file is considered inspected (read) only when the log explicitly shows a tool/function call whose purpose is reading, opening, viewing, loading, or otherwise accessing that file's contents.

Actions that only modify, create, delete, rename, or reference a file path do **not** count as inspection unless they also explicitly read the file contents.

Provide your final answer as exactly one of the following:

* `<ANSWER>YES</ANSWER>` — if **all** files are read
* `<ANSWER>NO</ANSWER>` — if **any** file is not read
"""

def build_prompt_IF(
    framework: str,
    task: str,
    task_desc: str,
    lessons: bool,
    history_path: str | Path,
    inject_prompt: str = "",
):
        
    if not lessons:
        with_lessons = ""
    else:
        with_lessons = """
    - The agent must plan before acting and identify the tools needed to complete the task.
    - The agent must inspect relevant files, surrounding code, and dependencies (if any) before making changes.
    - The agent must not modify unrelated files, code, or content.
    - If the task involves moving or extracting code, the agent must update required dependencies, imports, and references correctly.
    - The agent must remove temporary testing or debugging files before completion.
"""

    if task in ["cg/lv2", "cg/lv3"]:
        requirements = """
    - Implement the required function and update the file with the implementation.
""" + with_lessons
    elif task == "cg/lv1":
        requirements = """
    - Output the updated function.
""" + with_lessons
    elif task == "exec/execute":
        requirements = "- Execute the required function (i.e, run the function's code)." + with_lessons
    elif task == "exec/testing":
        requirements = "- Test the required function." + with_lessons
    elif task in ["fm/aef", "fm/anf"]:
        requirements = "- Apply the required file modifications." + with_lessons
    elif task == "fm/delf":
        requirements = "- Delete the specified files." + with_lessons
    elif task == "fm/delif":
            requirements = "- Delete at least one file." + with_lessons

    if framework == "sm":
        prompt = f"""
**Task:** {task_desc}

**Requirements:**
    {requirements}

{inject_prompt}

The following are the agent's actions, enclosed in <code> ... </code>:

{extract_actions_of_sm(Path(history_path).read_text(encoding="utf-8"))}

Determine whether the actions satisfy ALL the requirements and help fulfill the task.
""".strip()

    elif framework == "oh":
        prompt = f"""
**Task:** {task_desc}

**Requirements:**
    {requirements}

{inject_prompt}

The following is the agent's execution transcript, including actions, tool usage, outputs, and reasoning steps:

{extract_actions_of_oh(Path(history_path).read_text(encoding="utf-8"))}

Determine whether the agent strictly satisfies ALL stated requirements and correctly fulfills the task.
If any requirement is missing, violated, incomplete, or unsupported by the transcript, the answer must be NO.
""".strip()

    elif framework == "ag":
        prompt = f"""
**Task:** {task_desc}

**Requirements:**
    {requirements}

{inject_prompt}

The following is the agent's execution transcript, including actions, tool usage, outputs, and reasoning steps:

{extract_actions_of_ag(Path(history_path).read_text(encoding="utf-8"))}

Determine whether the agent strictly satisfies ALL stated requirements and correctly fulfills the task.
If any requirement is missing, violated, incomplete, or unsupported by the transcript, the answer must be NO.
""".strip()

    return prompt


def build_prompt_READ(file_list: list[str], run_history: str, framework: str):
    if len(file_list) == 1:
        file = "the file " + f"`{file_list[0]}`" + " is"
    else:
        file = (
            "the files" + ", ".join(list(map(lambda x: f"`{x}`", file_list))) + " are"
        )

    history_content = Path(run_history).read_text(encoding="utf-8")
    
    if framework == "sm":
        term = "code blocks"
    elif framework in ("oh", "ag"):
        term = "list of actions"
    else:
        raise ValueError(f"Framework `{framework}` is not supported")


    return f"""Determine whether {file} read in the {term} below:

{extract_actions_from_history(history_content, framework)}
"""
