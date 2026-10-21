import os
from datetime import datetime, timezone
from pathlib import Path

from openhands.sdk import LLM, Agent, Conversation, Tool
from openhands.sdk.conversation.exceptions import ConversationRunError
from openhands.tools.file_editor import FileEditorTool
from openhands.tools.file_editor.editor import FileEditor
from openhands.tools.task_tracker import TaskTrackerTool
from openhands.tools.terminal import TerminalTool
from openhands.sdk.conversation import ConversationExecutionStatus
from openhands.sdk.llm.llm import LLM as _LLM

# Disable Responses API path — it injects reasoning_text blocks that
# non-reasoning models (e.g. gpt-5-mini via OpenRouter) reject in
# conversation history.
_LLM.uses_responses_api = lambda self: False

# Patch FileEditor to resolve relative paths against its workspace root
_original_call = FileEditor.__call__


def _patched_call(self, *, command, path: str, **kwargs):
    p = Path(path)
    if not p.is_absolute() and self._cwd:
        path = str(Path(self._cwd) / p)
    return _original_call(self, command=command, path=path, **kwargs)


FileEditor.__call__ = _patched_call

from common.config import DEVEVAL, API_KEY, OPENROUTER_API_BASE


def create_agent(model: str, extra_tools: list | None = None) -> Agent:
    """Create an openhands Agent."""
    llm = LLM(
        model=f"openrouter/{model}",
        api_key=API_KEY,
        base_url=OPENROUTER_API_BASE,
        reasoning_effort=None,
        enable_encrypted_reasoning=False,
    )

    all_tools = [
        Tool(name=TerminalTool.name),
        Tool(name=FileEditorTool.name),
        Tool(name=TaskTrackerTool.name),
    ]
    if extra_tools:
        all_tools += [Tool(name=t) for t in extra_tools]

    return Agent(llm=llm, tools=all_tools)


# ── Event formatting / logging ────────────────────────────────────────────

def _format_event(event) -> str | None:
    event_type = type(event).__name__

    if event_type == "SystemPromptEvent":
        return None

    fields = (
        event.model_dump(mode="json", exclude_none=True)
        if hasattr(event, "model_dump")
        else {}
    )

    if event_type == "MessageEvent":
        source = fields.get("source", "?")
        content_blocks = fields.get("llm_message", {}).get("content", [])
        text = " ".join(
            block["text"] for block in content_blocks if "text" in block
        ).strip()
        return f"[{source}]: {text}"

    if event_type == "ActionEvent":
        source = fields.get("source", "?")
        tool = fields.get("tool_name", "?")
        action = fields.get("action", {})
        thought_blocks = fields.get("thought", [])
        thought = " ".join(b["text"] for b in thought_blocks if "text" in b).strip()
        lines = [f"[{source}] tool_call: {tool}"]
        if thought:
            lines.append(f"  thought : {thought}")
        lines.append(f"  action  : {action}")
        return "\n".join(lines)

    if event_type == "ObservationEvent":
        tool = fields.get("tool_name", "?")
        obs = fields.get("observation", {})
        is_error = obs.get("is_error", False)
        content_blocks = obs.get("content", [])
        text = " ".join(
            block["text"] for block in content_blocks if "text" in block
        ).strip()
        status = "ERROR" if is_error else "OK"
        return f"[environment/{tool}] ({status}): {text}"

    if event_type == "ConversationErrorEvent":
        code = fields.get("code", "?")
        detail = fields.get("detail", "")
        return f"[error] {code}: {detail}"

    return None


def _write_log(path, events, task, model, workspace, status):
    """Write conversation history to a log file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"Timestamp : {datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"Model     : {model}\n")
        f.write(f"Workspace : {workspace}\n")
        f.write(f"Status    : {status}\n")
        f.write(f"Task      :\n  {task}\n")
        f.write("CONVERSATION HISTORY\n")

        i = 0
        for event in events:
            line = _format_event(event)
            if line is None:
                continue
            i += 1
            f.write(f"[{i:03d}] {line}\n\n")


# ── Run agent ─────────────────────────────────────────────────────────────

def run_agent(
    model: str,
    task: str,
    workspace: str | Path,
    *,
    write_history_to: str | Path | None = None,
    extra_tools: list | None = None,
    mnr: int = 3,
):
    """
    Create an openhands agent, run a conversation, and optionally log history.

    Returns the list of events if the conversation finished, or ``None``.
    """
    import time

    prompt = task

    failed_count = 0
    while True:
        agent = create_agent(model=model, extra_tools=extra_tools)
        conversation = Conversation(agent=agent, workspace=str(workspace))
        conversation.send_message(prompt)
        try:
            conversation.run()
        except ConversationRunError:
            pass

        events = list(conversation.state.events)
        status = conversation.state.execution_status

        if write_history_to is not None:
            _write_log(
                path=write_history_to,
                events=events,
                task=prompt,
                model=model,
                workspace=workspace,
                status=status,
            )

        if status == ConversationExecutionStatus.FINISHED:
            return events

        if failed_count < mnr:
            failed_count += 1
            time.sleep(2)
            continue

        return None
