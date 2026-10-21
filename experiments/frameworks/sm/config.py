import builtins
import os
from contextlib import redirect_stdout
from pathlib import Path

from smolagents import CodeAgent, OpenAIModel

from common.config import DEVEVAL, API_KEY, OPENROUTER_API_BASE


all_builtins = {
    name: getattr(builtins, name)
    for name in dir(builtins)
    if callable(getattr(builtins, name)) and not name.startswith("_")
}
all_builtins.pop("print", None)


def openrouter_model(model_id: str):
    return OpenAIModel(
        model_id=model_id,
        api_base=OPENROUTER_API_BASE,
        api_key=API_KEY,
    )


def create_agent(
    model_id: str,
    tools: list,
    *,
    max_steps: int = 20,
    additional_imports: list | None = None,
    stream_outputs: bool = True,
    executor_kwargs: dict | None = None,
) -> CodeAgent:
    """Create a smolagents CodeAgent."""
    model = openrouter_model(model_id)
    return CodeAgent(
        model=model,
        tools=tools,
        additional_authorized_imports=additional_imports or ["*"],
        max_steps=max_steps,
        stream_outputs=stream_outputs,
        executor_kwargs=executor_kwargs or {"additional_functions": all_builtins},
    )


def run_and_record(agent, prompt: str, write_history_to: str | Path, retry: int = 3):
    for _ in range(retry):
        try:
            response = agent.run(prompt)
            with open(write_history_to, "w", encoding="utf-8") as f:
                history = agent.write_memory_to_messages()
                with redirect_stdout(f):
                    for i in range(1, len(history)):
                        print(history[i].content[0]["text"])
            return response
        except Exception as e:
            print("Failed:", e)
            continue


def run_agent(
    model_id: str,
    task: str,
    workspace: str | Path,
    *,
    write_history_to: str | Path | None = None,
    tools: list | None = None,
    max_steps: int = 20,
    additional_imports: list | None = None,
    stream_outputs: bool = True,
    executor_kwargs: dict | None = None,
    mnr: int = 3,
):
    import time

    agent = create_agent(
        model_id,
        tools or [],
        max_steps=max_steps,
        additional_imports=additional_imports,
        stream_outputs=stream_outputs,
        executor_kwargs=executor_kwargs,
    )

    prompt = task

    current_wd = os.getcwd()
    os.chdir(workspace)

    try:
        response = None
        if write_history_to:
            response = run_and_record(agent, prompt, write_history_to)
        else:
            response = agent.run(prompt)

        no_response_count = 0
        while not response and no_response_count < mnr:
            if write_history_to:
                response = run_and_record(agent, prompt, write_history_to)
            else:
                response = agent.run(prompt)
            no_response_count += 1
            time.sleep(2)
    except Exception:
        response = None
    finally:
        os.chdir(current_wd)

    return response
