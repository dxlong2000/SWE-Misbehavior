"""
smolagents (sm) framework adapter — tools.

Wraps the framework-agnostic core tool implementations (from
``common.tools_core``) with the ``@tool`` decorator from smolagents so
they can be passed to a ``CodeAgent``.

The sm framework relies on ``os.chdir(workspace)`` to set the working
directory; file paths in tools are therefore relative to the CWD.
"""

import os
import shutil
from pathlib import Path

from smolagents import tool

from common.config import DEVEVAL
from common.tools_core import (
    find_reference_files_core,
    read_file_core,
    update_content_core,
    remove_file_core,
    write_function_implementation_core,
    find_local_import_dependencies_core,
    extract_function_definition_core,
    remove_function_definition_core,
    find_import_statements_for_object_core,
)

__all__ = [
    "read_file",
    "update_content",
    "remove_file",
    "write_function_implementation",
    "find_local_import_dependencies",
    "find_reference_files",
    "extract_function_definition",
    "remove_function_definition",
    "find_import_statements_for_object",
    "get_full_tools",
    "get_basic_tools",
    "get_selected_tools",
    "set_runtime_env",
]

# ── Runtime environment (set by run scripts) ──────────────────────────────

_RUN_ENV: str | None = None
_SOURCE_DIR: str = "Source_Code"


def set_runtime_env(run_env: str, source_dir: str = "Source_Code"):
    """Set the runtime environment for detect/restore tools."""
    global _RUN_ENV, _SOURCE_DIR
    _RUN_ENV = run_env
    _SOURCE_DIR = source_dir


# ── Tool definitions ──────────────────────────────────────────────────────

@tool
def read_file(file: str) -> str:
    """
    Read a UTF-8 encoded text file and return its contents as a single string.

    Args:
        file: Path to the file to be opened and read.

    Returns:
        The file contents as a string.
    """
    return read_file_core(file)


@tool
def update_content(filepath: str, content: str) -> None:
    """
    Write text content to a file (UTF-8). Overwrites if exists, creates if not.

    Args:
        filepath: Path to the file to be written.
        content: Text content to write into the file.
    """
    update_content_core(filepath, content)


@tool
def remove_file(filepath: str) -> None:
    """
    Remove a file at the specified path.

    Args:
        filepath: The path to the file to be removed.
    """
    remove_file_core(filepath)


@tool
def write_function_implementation(code: str, function_name: str, filepath: str) -> str:
    """
    Replace the implementation body of a target function or method in a Python
    source file, preserving docstrings.

    Args:
        code: Python statements representing the new function body (statements only).
        function_name: Dotted path, e.g. "foo", "MyClass.method".
        filepath: Path to the Python source file to modify in place.

    Returns:
        Success or error message.
    """
    return write_function_implementation_core(code, function_name, filepath)


@tool
def find_local_import_dependencies(file_path: str) -> list[str]:
    """
    Find all file's local module dependencies.

    Args:
        file_path: Absolute or relative path to the Python source file to analyze.

    Returns:
        Deduplicated list of relative file paths representing local dependencies.
    """
    return find_local_import_dependencies_core(file_path)


@tool
def find_reference_files(filepath: str, function_name: str) -> list[str]:
    """
    Find all files that reference a given function.

    Args:
        filepath: Path to the Python file containing the function.
        function_name: Name of the function (e.g. `funcname`, `classname.method`).

    Returns:
        List of relative file paths that reference the function, including the source.
    """
    return find_reference_files_core(filepath, function_name)


@tool
def extract_function_definition(filepath: str, function_name: str) -> str:
    """
    Extract a function definition from a source file and return it as a
    standalone-ready code snippet.

    Args:
        filepath: Path to the Python source file.
        function_name: Name of the target function to extract.

    Returns:
        A formatted string containing the function definition and dependencies.
    """
    return extract_function_definition_core(filepath, function_name)


@tool
def remove_function_definition(filepath: str, function_name: str) -> str:
    """
    Remove a function or method from a Python file in-place.

    Args:
        filepath: Path to the Python source file.
        function_name: Function name or dotted path (e.g. "func", "Class.method").

    Returns:
        Status message indicating success or failure.
    """
    return remove_function_definition_core(filepath, function_name)


@tool
def find_import_statements_for_object(file_path: str, object_name: str) -> list[str]:
    """
    Find all import statements in a Python source file that import a specific object.

    Args:
        file_path: Path to the Python source file to inspect.
        object_name: Imported object, module, alias, or symbol name to search for.

    Returns:
        A list of source-code strings representing matching import statements.
    """
    return find_import_statements_for_object_core(file_path, object_name)


# ── Tool-set helpers ──────────────────────────────────────────────────────

# Mapping from tool name string → decorated tool object
_TOOL_REGISTRY = {
    "read_file": read_file,
    "update_content": update_content,
    "remove_file": remove_file,
    "write_function_implementation": write_function_implementation,
    "find_local_import_dependencies": find_local_import_dependencies,
    "find_reference_files": find_reference_files,
    "extract_function_definition": extract_function_definition,
    "remove_function_definition": remove_function_definition,
    "find_import_statements_for_object": find_import_statements_for_object,
}

_ALWAYS_INCLUDED = [read_file, remove_file, update_content]


def get_full_tools() -> list:
    """Return the full set of tools for the sm framework."""
    return list(_TOOL_REGISTRY.values())


def get_basic_tools() -> list:
    """Return the basic (minimal) tool set for the sm framework."""
    return _ALWAYS_INCLUDED.copy()


def get_selected_tools(names: list[str]) -> list:
    """
    Return tools matching *names* from the registry, always including the
    basic read/write/remove trio regardless of what was selected.
    """
    selected = {t for name in names if (t := _TOOL_REGISTRY.get(name)) is not None}
    # Ensure always-included tools are present
    for t in _ALWAYS_INCLUDED:
        selected.add(t)
    # Preserve a stable order matching _TOOL_REGISTRY
    return [t for t in _TOOL_REGISTRY.values() if t in selected]
