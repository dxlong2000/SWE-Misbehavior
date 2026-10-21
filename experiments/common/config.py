import os
import json
import platform
from pathlib import Path
from contextlib import contextmanager


DEVEVAL = os.getcwd()
API_KEY = os.environ["OPENROUTER_API_KEY"]

OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"


# ── Cross-platform file locking ───────────────────────────────────────────

_IS_WINDOWS = platform.system() == "Windows"


@contextmanager
def file_lock(lock_path: str | Path):
    """
    Cross-platform exclusive file lock.

    On Unix, uses ``fcntl.flock`` (matching the original implementation).
    On Windows, uses ``msvcrt.locking`` as a best-effort advisory lock.
    Falls back to a no-op if neither is available.

    Usage::

        with file_lock(lock_path):
            ...  # critical section
    """
    lock_path = Path(lock_path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_file = open(lock_path, "w")

    try:
        if _IS_WINDOWS:
            try:
                import msvcrt

                msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            except (ImportError, OSError):
                pass  # best-effort; proceed without lock
        else:
            try:
                import fcntl

                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            except (ImportError, OSError):
                pass

        yield
    finally:
        if not _IS_WINDOWS:
            try:
                import fcntl
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            except (ImportError, OSError):
                pass
        lock_file.close()


def load_run_samples(path: str | Path) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_run_samples(path: str | Path, key: str, entry: dict) -> None:
    path = Path(path)
    lock_path = path.with_suffix(".lock")

    with file_lock(lock_path):
        run_samples = load_run_samples(path)
        run_samples[key] = entry
        with open(path, "w", encoding="utf-8") as f:
            json.dump(run_samples, f, indent=4)
