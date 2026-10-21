"""
agno (ag) framework adapter — configuration.

Provides agent creation, model setup, and response logging for the agno
framework.  Mirrors the original ``experiments/ag/config.py`` but imports
shared values from ``common.config``.
"""

import json
import os
from pathlib import Path

from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.tools.shell import ShellTools
from agno.tools.file import FileTools
from agno.utils.print_response.agent import build_panels
from agno.utils.timer import Timer
from rich.console import Console, Group

from common.config import DEVEVAL, API_KEY, OPENROUTER_API_BASE

# agno reads the API key from the environment
os.environ["OPENROUTER_API_KEY"] = API_KEY


def run_agent(
    model: str,
    task: str,
    workspace: str,
    *,
    write_history_to: str | Path | None = None,
    extra_tools: list | None = None,
    mnr: int = 3,
):
    """
    Create an agno Agent, run the task, and optionally write history.

    Returns the final text response (str) or ``None``.
    """
    import time

    prompt = task

    current_wd = os.getcwd()
    os.chdir(workspace)

    failed_count = 0
    response = None

    while True:
        agent = Agent(
            model=OpenRouter(id=model),
            tools=[ShellTools(), FileTools()] + (extra_tools or []),
            markdown=True,
        )

        timer = Timer()
        timer.start()
        response = agent.run(prompt)
        timer.stop()

        if response.content:
            break

        if failed_count < mnr:
            failed_count += 1
            time.sleep(2)
            continue

        response = None
        break

    if write_history_to is not None and response is not None:
        write_history_to = Path(write_history_to)
        write_history_to.parent.mkdir(parents=True, exist_ok=True)

        log_path = write_history_to.with_suffix(".log")
        with open(log_path, "w", encoding="utf-8") as f:
            console = Console(file=f, width=180)
            panels = build_panels(
                run_response=response,
                response_timer=timer,
                output_schema=None,
                show_reasoning=True,
                show_full_reasoning=False,
                tags_to_include_in_markdown={"think", "thinking"},
                markdown=True,
                compression_manager=agent.compression_manager,
            )
            console.print(Group(*panels))

        with open(write_history_to, "w", encoding="utf-8") as f:
            f.write("### METRICS ###\n")
            if response.metrics:
                f.write(json.dumps(response.metrics.to_dict(), indent=2) + "\n\n")
            else:
                f.write("No metrics returned by the provider.\n\n")

            f.write("### MESSAGE HISTORY & TOOL CALLS ###\n")
            if response.messages:
                for idx, msg in enumerate(response.messages, start=1):
                    f.write(f"--- Message {idx} ({msg.role.upper()}) ---\n")
                    if msg.content:
                        f.write(f"Content:\n{msg.content}\n")
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        f.write("Tool Calls:\n")
                        for tool in msg.tool_calls:
                            f.write(f"  - {tool}\n")
                    f.write("\n")
            else:
                f.write("No message history available for this run.\n")

    os.chdir(current_wd)

    if response and response.content:
        return response.content
    return None
