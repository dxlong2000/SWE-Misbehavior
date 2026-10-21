#!/usr/bin/env python
"""
Unified code-generation (cg) single-sample runner.

Usage:
    python run_cg_one.py --framework sm --lv 1 --model_id openai/gpt-4o-mini \
        --workdir SC_sm_cg_lv1_env0 --key s1

Supports all three frameworks via --framework {sm, oh, ag}.
"""

import os
import json
import argparse
import random
import time
import shutil
from pathlib import Path
from contextlib import redirect_stdout

from common.config import DEVEVAL, save_run_samples
from common.tools_core import ToolSelector, GuidelineSelector
from common.utils import (
    find_recent_modified_files,
    get_local_dependencies as _get_local_dependencies,
    extract_python_code,
)
from common.file_tracking import (
    categorize_modified_files,
    log_file_history,
    restore_environment,
    load_all_expected_files,
    check_already_done,
    restore_completion_file
)


def parse_args():
    parser = argparse.ArgumentParser(description="Run a single CG sample")
    parser.add_argument("--framework", type=str, required=True, choices=["sm", "oh", "ag"])
    parser.add_argument("--workdir", type=str, required=True)
    parser.add_argument("--lv", type=int, required=True, choices=[1, 2, 3])
    parser.add_argument("--model_id", type=str, required=True)
    parser.add_argument("--key", type=str, required=True, help="Sample key to run")
    parser.add_argument("--max_steps", type=int, default=20)
    parser.add_argument("--no_stream", action="store_true")
    parser.add_argument("--outdir", type=str, default="results")
    parser.add_argument("--mnr", type=int, default=3)
    parser.add_argument("--json", type=str, default="samples")
    parser.add_argument("--toolsel", action="store_true")
    parser.add_argument("--guidelines", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    lv = f"lv{args.lv}"

    # ── Framework-specific imports ─────────────────────────────────────────
    if args.framework == "sm":
        from frameworks.sm.config import run_agent, all_builtins
        from frameworks.sm.tools import get_basic_tools, get_selected_tools, set_runtime_env
    elif args.framework == "oh":
        from frameworks.oh.config import run_agent
        from frameworks.oh.tools import get_extra_tool_names, get_selected_tool_names
    elif args.framework == "ag":
        from frameworks.ag.config import run_agent
        from frameworks.ag.tools import get_basic_tools, get_selected_tools

    # ── Paths ──────────────────────────────────────────────────────────────
    RUN_ENV = f"{DEVEVAL}/{args.workdir}"
    SAVED_FOLDER = Path(f"{DEVEVAL}/{args.outdir}/{args.framework}/cg/{lv}/{args.model_id}")
    SAVED_FOLDER.mkdir(parents=True, exist_ok=True)

    # ── Load metadata ─────────────────────────────────────────────────────
    mapper_path = f"{DEVEVAL}/metadata/cg/{lv}/{args.json}.json"
    with open(mapper_path, encoding="utf-8") as f:
        mappers = json.load(f)

    all_expected_files = load_all_expected_files(DEVEVAL, "cg")

    # ── Skip if already done ──────────────────────────────────────────────
    if check_already_done(SAVED_FOLDER, args.key):
        print(f"[skip] {args.key} already done")
        return

    infor = mappers[args.key]
    completion_path = infor["completion_path"]
    new_completion_path = Path(infor["new_completion_path"])

    # ── Pre-run: copy missing-function file, set up tools ─────────────────
    shutil.copy2(
        Path("Source_Code_no_code") / new_completion_path,
        Path(RUN_ENV) / Path(completion_path).parent,
    )

    # ── Framework-specific tool setup (base — overridden by selector below) ──
    extra_tools = None
    if args.framework == "sm":
        set_runtime_env(RUN_ENV, "Source_Code_no_code")
        tools = get_basic_tools()
        executor_kwargs = {"additional_functions": all_builtins}
        additional_imports = ["*"]
        stream_outputs = not args.no_stream
    elif args.framework == "oh":
        extra_tools = [] 
    elif args.framework == "ag":
        tools = get_basic_tools()
        extra_tools = tools

    # ── Build prompt ──────────────────────────────────────────────────────
    os.chdir(RUN_ENV)

    base_prompt = random.choice(infor["prompt"])
    if args.guidelines:
        local_dependencies = _get_local_dependencies(completion_path)
        base_prompt += f"\n\n## Local dependencies: {local_dependencies}"

    # ── Tool selection (--toolsel → ask selector, not use all tools) ───
    if args.toolsel:
        selector = ToolSelector()
        selected = selector.reason_on(base_prompt)
        if args.framework == "sm":
            tools = get_selected_tools(selected["tools"])
        elif args.framework == "oh":
            extra_tools = get_selected_tool_names(selected["tools"])
        elif args.framework == "ag":
            extra_tools = get_selected_tools(selected["tools"])

    if args.guidelines:
        gl_selector = GuidelineSelector()
        gl_result = gl_selector.reason_on(base_prompt)
        guidelines = GuidelineSelector.parse_glids(gl_result["guidelines"])
        guideline_text = "\n".join(f"* {g}" for g in guidelines)
        prompt = base_prompt + f"\n\n## Guidelines:\n{guideline_text}"
    else:
        prompt = base_prompt

    # Temporarily delete the ground truth
    Path(completion_path).unlink(missing_ok=True)

    SAVED_FOLDER.joinpath(new_completion_path.parent).mkdir(parents=True, exist_ok=True)
    history_file = SAVED_FOLDER / new_completion_path.parent / f"run_history_{args.key}.txt"

    # ── Run agent ─────────────────────────────────────────────────────────
    start_time = time.time()
    try:
        if args.framework == "sm":
            response = run_agent(
                args.model_id, task=prompt, workspace=RUN_ENV,
                write_history_to=history_file, tools=tools,
                max_steps=args.max_steps, additional_imports=additional_imports,
                stream_outputs=stream_outputs, executor_kwargs=executor_kwargs,
                mnr=args.mnr,
            )
        elif args.framework == "oh":
            response = run_agent(
                args.model_id, task=prompt, workspace=RUN_ENV,
                write_history_to=history_file, extra_tools=extra_tools, mnr=args.mnr,
            )
        elif args.framework == "ag":
            response = run_agent(
                args.model_id, task=prompt, workspace=RUN_ENV,
                write_history_to=history_file, extra_tools=extra_tools, mnr=args.mnr,
            )
    except Exception:
        response = None

    # ── lv1: extract python code ──────────────────────────────────────────
    if lv == "lv1":
        output_path = SAVED_FOLDER / Path(completion_path).parent / f"{args.key}_output_function.py"
        with open(output_path, "w") as f:
            try:
                if isinstance(response, list):
                    response_text = "\n".join(str(r) for r in response)
                else:
                    response_text = str(response) if response else ""
                code = extract_python_code(response_text)
                f.write(code)
            except Exception as e:
                print("Cannot extract function:", e)
                f.write("")

    # ── Move completed file to saved folder ───────────────────────────────
    src = Path(RUN_ENV) / new_completion_path
    dst = SAVED_FOLDER / new_completion_path
    if dst.exists():
        dst.unlink()
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        shutil.move(src, dst.parent)

    os.chdir(DEVEVAL)

    # ── Track file changes ────────────────────────────────────────────────
    file_info = categorize_modified_files(
        RUN_ENV, DEVEVAL, "Source_Code", start_time,
        all_expected_files, exclude_completion_path=completion_path,
    )

    log_file_history(SAVED_FOLDER, args.key, file_info)

    # ── Restore environment ──────────────────────────────────────────────
    restore_environment(RUN_ENV, DEVEVAL, "Source_Code", file_info)
    restore_completion_file(RUN_ENV, DEVEVAL, completion_path, "Source_Code")

    # ── Save run_samples ──────────────────────────────────────────────────
    entry = {
        "completion_path": infor["completion_path"],
        "new_completion_path": infor["new_completion_path"],
        "function_name": infor["function_name"],
        "need_read": infor["need_read"],
        "file_create": len(file_info["created"]),
        "file_delete": len(file_info["deleted"]),
        "file_update": len(file_info["updated"]),
        "no_response": not bool(response),
    }
    save_run_samples(SAVED_FOLDER / "run_samples.json", args.key, entry)

    print(f"[done] {args.key}: {history_file}")


if __name__ == "__main__":
    main()
