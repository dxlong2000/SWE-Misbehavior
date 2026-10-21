import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from queue import Queue

from .config import DEVEVAL, load_run_samples


def create_env(
    deveval: str | Path,
    framework: str,
    experiment: str,
    lv: str,
    model_id: str,
    env_idx: int,
    *,
    source_subdir: str = "Source_Code",
) -> Path:
    """
    Create (or reuse) a working-environment copy for a batch worker.

    Returns the path to the environment directory.
    """
    model_safe = model_id.replace("/", "_")
    wd = Path(deveval) / f"SC_{framework}_{experiment}_{lv}_{model_safe}_env{env_idx}"

    if wd.exists():
        print("Env already exists:", wd)
    else:
        shutil.copytree(
            Path(deveval) / source_subdir,
            wd,
            symlinks=True,
            ignore_dangling_symlinks=True,
        )
        print("Created env:", wd)
    return wd


def run_batch(
    framework: str,
    experiment: str,
    *,
    lv: str,
    model_id: str,
    outdir: str = "results",
    num_samples: int | None = None,
    parallel: int = 4,
    mnr: int = 3,
    json_name: str = "samples",
    full_tools: bool = False,
    lessons: bool = False,
    max_steps: int = 20,
    no_stream: bool = False,
    extra_args: list[str] | None = None,
    source_subdir: str = "Source_Code",
    interactive: bool = True,
):
    """
    Run a batch of experiment samples in parallel.

    Args:
        framework: ``"sm"``, ``"oh"``, or ``"ag"``.
        experiment: ``"cg"``, ``"exec"``, or ``"fm"``.
        lv: Level identifier (e.g. ``"1"``, ``"execute"``, ``"aef"``).
        model_id: OpenRouter model ID.
        outdir: Output directory name (default ``"results"``).
        num_samples: Max samples to run (None = all).
        parallel: Number of parallel workers.
        mnr: Max retries for no-response.
        json_name: JSON file name (default ``"samples"``).
        full_tools: Whether to use the full toolset.
        lessons: Whether to append lessons to the prompt.
        max_steps: Max agent steps (sm only).
        no_stream: Disable streaming (sm only).
        extra_args: Additional CLI args for the one-shot script.
        source_subdir: Source directory to copy from.
        interactive: If True, prompt user about resume/restart.
    """
    # Determine the metadata path based on experiment type
    if experiment == "cg":
        mapper_path = f"{DEVEVAL}/metadata/cg/lv{lv}/{json_name}.json"
    elif experiment == "exec":
        mapper_path = f"{DEVEVAL}/metadata/exec/{lv}/{json_name}.json"
    elif experiment == "fm":
        mapper_path = f"{DEVEVAL}/metadata/fm/{lv}/{json_name}.json"
    else:
        raise ValueError(f"Unknown experiment: {experiment}")

    with open(mapper_path, encoding="utf-8") as f:
        mappers = json.load(f)

    saved_folder = Path(f"{DEVEVAL}/{outdir}/{framework}/{experiment}/{lv}/{model_id}")
    saved_folder.mkdir(parents=True, exist_ok=True)
    status_file = saved_folder / "run_status.txt"

    # Check for existing progress
    run_samples_path = saved_folder / "run_samples.json"
    try:
        with open(run_samples_path) as f:
            run_samples = json.load(f)

        if interactive:
            prompt_msg = (
                f"\033[33mYou've already run {len(run_samples)} samples. "
                f"This run will proceed with the next {num_samples} samples? "
                f"('c' - continue, 'r' - restart, '<other>' - quit)\033[0m "
            )
            m = input(prompt_msg)
            if m == "r":
                run_samples = {}
                run_samples_path.write_text("{}")
            elif m == "c":
                pass
            else:
                return
    except FileNotFoundError:
        run_samples = {}

    done_keys = set(run_samples.keys())
    keys = [k for k in mappers if k not in done_keys]
    if num_samples:
        keys = keys[:num_samples]

    n_parallel = min(parallel, num_samples) if num_samples else parallel

    print(f"Running {len(keys)} samples with {n_parallel} workers...")

    # Create environments
    with ThreadPoolExecutor(max_workers=n_parallel) as ex:
        workdirs = list(
            ex.map(
                lambda i: create_env(
                    DEVEVAL, framework, experiment, lv, model_id, i,
                    source_subdir=source_subdir,
                ),
                range(n_parallel),
            )
        )

    # Build the subprocess command
    one_script = Path(__file__).parent.parent / f"run_{experiment}_one.py"
    base_cmd = [
        sys.executable, str(one_script),
        "--framework", framework,
        "--lv", str(lv),
        "--model_id", model_id,
        "--outdir", outdir,
        "--mnr", str(mnr),
        "--json", json_name,
    ]
    if full_tools:
        base_cmd.append("--full_tools")
    if lessons:
        base_cmd.append("--lessons")
    if max_steps != 20 and experiment in ("cg", "exec"):
        base_cmd.extend(["--max_steps", str(max_steps)])
    if no_stream and experiment in ("cg", "exec"):
        base_cmd.append("--no_stream")
    if extra_args:
        base_cmd.extend(extra_args)

    free_envs: Queue = Queue()
    for i in range(len(workdirs)):
        free_envs.put(i)

    def run_one_dynamic(key: str) -> tuple[str, int, Path]:
        worker_idx = free_envs.get()
        try:
            completion_path = Path(mappers[key]["completion_path"])
            log_dir = saved_folder / completion_path.parent
            if experiment == "fm" and lv == "delif":
                log_dir = saved_folder / completion_path
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"{key}.log"

            cmd = base_cmd + ["--workdir", workdirs[worker_idx].name, "--key", key]
            with open(log_file, "w") as lf:
                result = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT)

            return key, result.returncode, log_file
        finally:
            free_envs.put(worker_idx)

    with ThreadPoolExecutor(max_workers=n_parallel) as executor:
        futures = {executor.submit(run_one_dynamic, key): key for key in keys}
        for future in as_completed(futures):
            key, returncode, log_file = future.result()
            msg = f"[OK] {key}" if returncode == 0 else f"[FAIL] {key}, see: {log_file}"
            print(msg)
            with open(status_file, "a") as sf:
                sf.write(msg + "\n")

    print(f"\nDone. Ran {len(keys)} samples.")
