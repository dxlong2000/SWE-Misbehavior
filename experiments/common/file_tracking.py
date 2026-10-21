import os
import json
import shutil
import time
from contextlib import redirect_stdout
from pathlib import Path
from typing import Optional

from .config import file_lock, load_run_samples, DEVEVAL
from .utils import find_recent_modified_files


def categorize_modified_files(
    run_env: str | Path,
    deveval: str | Path,
    ground_truth: str = "Source_Code",
    start_time: float | None = None,
    all_expected_files: set[str] | None = None,
    exclude_completion_path: str | None = None,
) -> dict:

    if start_time is None:
        start_time = time.time()

    elapsed_minutes = (time.time() - start_time) / 60 + 0.5
    recent_modified_files = find_recent_modified_files(run_env, minutes=elapsed_minutes)

    created_files, updated_files = [], []

    for file in recent_modified_files:
        if file.endswith(".pyc") or ".pytest_cache" in file:
            continue
        if not os.path.exists(f"{deveval}/{ground_truth}/{file}"):
            created_files.append(file)
        else:
            updated_files.append(file)

    if all_expected_files is not None:
        deleted_files = {
            f
            for f in all_expected_files
            if ".pytest_cache" not in f
            and not os.path.lexists(f"{run_env}/{f}")
        }
        if exclude_completion_path:
            deleted_files = {f for f in deleted_files if f != exclude_completion_path}
    else:
        deleted_files = set()

    return {
        "recent_modified": recent_modified_files,
        "created": created_files,
        "updated": updated_files,
        "deleted": deleted_files,
        "elapsed_minutes": elapsed_minutes,
    }


def log_file_history(
    saved_folder: str | Path,
    sample_key: str,
    file_info: dict,
    extra_lines: list[str] | None = None,
) -> None:
    """
    Append a file-history entry for *sample_key* to ``file_history.txt``.

    Args:
        saved_folder: Output directory.
        sample_key: The sample identifier.
        file_info: Dict from :func:`categorize_modified_files`.
        extra_lines: Additional lines to log (e.g. FM-specific metrics).
    """
    history_path = Path(saved_folder) / "file_history.txt"
    with open(history_path, "a", encoding="utf-8") as f:
        with redirect_stdout(f):
            print(f"## Sample: {sample_key}")
            print("Recent modified files:", file_info["recent_modified"])
            print("Created files", file_info["created"])
            print("Updated files", file_info["updated"])
            print("Deleted files", list(file_info["deleted"]))
            if extra_lines:
                for line in extra_lines:
                    print(line)
            print()


def restore_environment(
    run_env: str | Path,
    deveval: str | Path,
    ground_truth: str,
    file_info: dict,
    *,
    restore_deleted: bool = True,
    restore_updated: bool = True,
    remove_created: bool = True,
) -> None:

    run_env = Path(run_env)
    deveval = Path(deveval)

    if restore_deleted:
        for file in file_info["deleted"]:
            src = deveval / ground_truth / file
            dst = run_env / file
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.resolve() != dst.resolve():
                try:
                    shutil.copy2(src, dst, follow_symlinks=False)
                except FileNotFoundError:
                    pass

    if restore_updated:
        for file in file_info["updated"]:
            src = deveval / ground_truth / file
            dst = run_env / file
            dst.parent.mkdir(parents=True, exist_ok=True)
            if os.path.exists(dst) or os.path.islink(dst):
                os.unlink(dst)
            if src.resolve() != dst.resolve():
                try:
                    shutil.copy2(src, dst, follow_symlinks=False)
                except FileNotFoundError:
                    pass

    if remove_created:
        for file in file_info["created"]:
            try:
                os.unlink(f"{run_env}/{file}")
            except FileNotFoundError:
                pass


def restore_completion_file(
    run_env: str | Path,
    deveval: str | Path,
    completion_path: str,
    ground_truth: str = "Source_Code",
) -> None:
    """Restore a single ground-truth completion file into the run environment."""
    src = Path(deveval) / ground_truth / completion_path
    dst = Path(run_env) / Path(completion_path).parent
    if src.exists():
        shutil.copy2(src, dst, follow_symlinks=False)

# ── All-files list loading ────────────────────────────────────────────────

def load_all_expected_files(deveval: str | Path, experiment: str, lv: str = "") -> set[str]:
    deveval = Path(deveval)

    if experiment == "cg":
        path = deveval / "all_files_cg.txt"
    elif experiment == "exec":
        path = deveval / "all_files_cg.txt"
    elif experiment == "fm":
        if lv == "delif":
            path = deveval / "all_files_fm_delif.txt"
        else:
            path = deveval / "all_files_fm.txt"
    else:
        path = deveval / "all_files_cg.txt"

    with open(path) as f:
        return {line.strip() for line in f}


def check_already_done(saved_folder: str | Path, key: str) -> bool:
    run_samples_path = Path(saved_folder) / "run_samples.json"
    run_samples = load_run_samples(run_samples_path)
    return key in run_samples
