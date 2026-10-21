#!/usr/bin/env python
"""
Unified function-modification (fm) single-sample runner.

Usage:
    python run_fm_one.py --framework sm --lv aef --model_id openai/gpt-4o-mini \
        --workdir SC_sm_fm_aef_env0 --key s1

Supports all three frameworks via --framework {sm, oh, ag}.
FM levels: aef (add existing function), anf (add new function),
           delf (delete file), delif (delete files with imports).
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
from common.utils import find_recent_modified_files
from common.file_tracking import (
    load_all_expected_files,
    check_already_done,
    log_file_history,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Run a single FM sample")
    parser.add_argument("--framework", type=str, required=True, choices=["sm", "oh", "ag"])
    parser.add_argument("--key", type=str, required=True)
    parser.add_argument("--workdir", type=str, required=True)
    parser.add_argument("--lv", type=str, required=True, help="aef, anf, delf, or delif")
    parser.add_argument("--model_id", type=str, required=True)
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
    lv = args.lv

    # ── Framework-specific imports ─────────────────────────────────────────
    if args.framework == "sm":
        from frameworks.sm.config import run_agent, all_builtins
        from frameworks.sm.tools import get_basic_tools, get_selected_tools, set_runtime_env
    elif args.framework == "oh":
        from frameworks.oh.config import run_agent
        from frameworks.oh.tools import get_extra_tool_names, get_selected_tool_names, register_runtime_tools
    elif args.framework == "ag":
        from frameworks.ag.config import run_agent
        from frameworks.ag.tools import get_basic_tools, get_selected_tools

    # ── Paths ──────────────────────────────────────────────────────────────
    RUN_ENV = f"{DEVEVAL}/{args.workdir}"
    SAVED_FOLDER = Path(f"{DEVEVAL}/{args.outdir}/{args.framework}/fm/{lv}/{args.model_id}")
    SAVED_FOLDER.mkdir(parents=True, exist_ok=True)

    # ── Load metadata ─────────────────────────────────────────────────────
    mapper_path = f"{DEVEVAL}/metadata/fm/{lv}/{args.json}.json"
    with open(mapper_path, encoding="utf-8") as f:
        mappers = json.load(f)

    ground_truth = "Source_Code_fmdelif" if lv == "delif" else "Source_Code"
    all_expected_files = load_all_expected_files(DEVEVAL, "fm", lv)

    # ── Skip if already done ──────────────────────────────────────────────
    if check_already_done(SAVED_FOLDER, args.key):
        print(f"[skip] {args.key} already done")
        return

    infor = mappers[args.key]
    completion_path = Path(infor["completion_path"])
    history_file = SAVED_FOLDER / completion_path.parent / f"run_history_{args.key}.txt"

    # ── Level-specific tracking variables ─────────────────────────────────
    if lv in ("aef", "anf"):
        modify_all_expected_files = False
        modify_unexpected_file = False
        need_update_files = infor["need_update"]
        count_modify_all_expected_files = 0
    elif lv in ("delf", "delif"):
        delete_unexpected_file = False
        delete_expected_file = False

    # ── Framework-specific tool setup ─────────────────────────────────────
    if args.framework == "sm":
        set_runtime_env(RUN_ENV, ground_truth)
        tools = get_basic_tools()  # overridden by selector if --toolsel
        executor_kwargs = {"additional_functions": all_builtins}
        additional_imports = ["*"]
        stream_outputs = not args.no_stream
    elif args.framework == "oh":
        register_runtime_tools(run_env=RUN_ENV, source_dir=f"{DEVEVAL}/{ground_truth}")
        extra_tools = []  # overridden by selector if --toolsel
    elif args.framework == "ag":
        tools = get_basic_tools()  # overridden by selector if --toolsel
        extra_tools = tools

    SAVED_FOLDER.joinpath(completion_path.parent).mkdir(parents=True, exist_ok=True)

    # ── Build base prompt ─────────────────────────────────────────────────
    base_prompt = random.choice(infor["prompt"])

    # ── Tool selection (--toolsel → ask selector) ───────────────────────
    if args.toolsel:
        selector = ToolSelector()
        selected = selector.reason_on(base_prompt)
        if args.framework == "sm":
            tools = get_selected_tools(selected["tools"])
        elif args.framework == "oh":
            extra_tools = get_selected_tool_names(selected["tools"])
        elif args.framework == "ag":
            extra_tools = get_selected_tools(selected["tools"])

    # ── Guideline selection (--guidelines → inject relevant subset) ──────────
    if args.guidelines:
        gl_selector = GuidelineSelector()
        gl_result = gl_selector.reason_on(base_prompt)
        guidelines = GuidelineSelector.parse_glids(gl_result["guidelines"])
        guideline_text = "\n".join(f"* {g}" for g in guidelines)
        prompt = base_prompt + f"\n\n## Guidelines:\n{guideline_text}"
    else:
        prompt = base_prompt

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

    # ── Track file changes ────────────────────────────────────────────────
    elapsed_minutes = (time.time() - start_time) / 60 + 0.5
    recent_modified_files = find_recent_modified_files(RUN_ENV, minutes=elapsed_minutes)

    created_files, updated_files = [], []
    for file in recent_modified_files:
        if file.endswith(".pyc") or ".pytest_cache" in file:
            continue
        if not os.path.exists(f"{DEVEVAL}/{ground_truth}/{file}"):
            created_files.append(file)
        else:
            updated_files.append(file)
            if lv in ("aef", "anf"):
                if file not in need_update_files:
                    modify_unexpected_file = True
                else:
                    count_modify_all_expected_files += 1
                    if count_modify_all_expected_files == len(need_update_files):
                        modify_all_expected_files = True

    # ── Save modified files per level ─────────────────────────────────────
    os.chdir(RUN_ENV)

    if lv == "aef":
        for file in need_update_files:
            cp = Path(file)
            if file != infor["completion_path"]:
                if file != need_update_files[-1]:
                    shutil.copy2(file, SAVED_FOLDER / completion_path.parent / f"references_{args.key}_{cp.stem}.py", follow_symlinks=False)
                else:
                    shutil.copy2(file, SAVED_FOLDER / completion_path.parent / f"updated_{args.key}_{cp.stem}.py", follow_symlinks=False)
            else:
                shutil.copy2(file, SAVED_FOLDER / completion_path.parent / f"updated_{args.key}_{completion_path.stem}.py", follow_symlinks=False)

    elif lv == "anf":
        created_file_dir = SAVED_FOLDER / completion_path.parent / f"created_files_{args.key}_{lv}"
        created_file_dir.mkdir(parents=True, exist_ok=True)
        for file in created_files:
            shutil.copy2(file, created_file_dir, follow_symlinks=False)
        for file in need_update_files:
            cp = Path(file)
            if file != infor["completion_path"]:
                shutil.copy2(file, SAVED_FOLDER / completion_path.parent / f"references_{args.key}_{cp.stem}.py", follow_symlinks=False)
            else:
                shutil.copy2(file, SAVED_FOLDER / completion_path.parent / f"updated_{args.key}_{completion_path.stem}.py", follow_symlinks=False)

    os.chdir(DEVEVAL)

    # ── Track deleted files ───────────────────────────────────────────────
    deleted_files = {
        f for f in all_expected_files
        if ".pytest_cache" not in f and not os.path.lexists(f"{RUN_ENV}/{f}")
    }

    for file in deleted_files:
        Path(f"{RUN_ENV}/{file}").parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f"{ground_truth}/{file}", f"{RUN_ENV}/{file}", follow_symlinks=False)

        if lv == "delf":
            if file != infor["completion_path"]:
                delete_unexpected_file = True
            else:
                delete_expected_file = True
        elif lv == "delif":
            dummies = infor["dm"]
            if file not in dummies:
                delete_unexpected_file = True
            else:
                delete_expected_file = True

    # ── Log file history ──────────────────────────────────────────────────
    extra_lines = []
    if lv in ("delf", "delif"):
        extra_lines.append(f"Delete unexpected files: {delete_unexpected_file}")
        extra_lines.append(f"Delete expected files: {delete_expected_file}")
    if lv in ("aef", "anf"):
        extra_lines.append(f"Modify all expected files: {modify_all_expected_files}")
        extra_lines.append(f"Modify unexpected_file: {modify_unexpected_file}")

    file_info = {
        "recent_modified": recent_modified_files,
        "created": created_files,
        "updated": updated_files,
        "deleted": deleted_files,
    }
    log_file_history(SAVED_FOLDER, args.key, file_info, extra_lines=extra_lines)

    # ── Restore updated/created files ─────────────────────────────────────
    for file in updated_files:
        Path(f"{RUN_ENV}/{file}").parent.mkdir(parents=True, exist_ok=True)
        dst = f"{RUN_ENV}/{file}"
        if os.path.exists(dst) or os.path.islink(dst):
            os.unlink(dst)
        shutil.copy2(f"{ground_truth}/{file}", dst, follow_symlinks=False)

    for file in created_files:
        os.unlink(f"{RUN_ENV}/{file}")

    # ── Save run_samples ──────────────────────────────────────────────────
    if lv in ("delf", "delif"):
        entry = {
            "no_response": not bool(response),
            "completion_path": infor["completion_path"],
            "file_create": len(created_files),
            "file_delete": len(deleted_files),
            "file_update": len(updated_files),
            "delete_unexpected_file": delete_unexpected_file,
            "delete_expected_file": delete_expected_file,
        }
        if lv == "delif" and "need_read" in infor:
            entry["need_read"] = infor["need_read"]
    elif lv in ("anf", "aef"):
        entry = {
            "no_response": not bool(response),
            "completion_path": infor["completion_path"],
            "new_completion_path": str(completion_path.parent / f"updated_{args.key}_{completion_path.stem}.py").replace("\\", "/"),
            "need_update": infor["need_update"],
            "function_name": infor["function_name"],
            "file_create": len(created_files),
            "file_delete": len(deleted_files),
            "file_update": len(updated_files),
            "modify_all_expected_files": modify_all_expected_files,
            "modify_unexpected_file": modify_unexpected_file,
        }

    save_run_samples(SAVED_FOLDER / "run_samples.json", args.key, entry)
    print(f"[done] {args.key}: {history_file}")


if __name__ == "__main__":
    main()
