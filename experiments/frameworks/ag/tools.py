"""
agno (ag) framework adapter — tools.

Wraps the framework-agnostic core tool implementations (from
``common.tools_core``) with the ``@tool`` decorator from agno so they can
be passed to an agno ``Agent``.

The ag framework uses ``os.chdir(workspace)`` (inside ``run_agent``)
to set the working directory; file paths in tools are therefore
relative to the CWD.
"""

from pathlib import Path

from agno.tools import tool

from common.tools_core import (
    find_reference_files_core,
    write_function_implementation_core,
    find_local_import_dependencies_core,
    extract_function_definition_core,
    remove_function_definition_core,
    find_import_statements_for_object_core,
)

__all__ = [
    "write_function_implementation",
    "find_local_import_dependencies",
    "find_reference_files",
    "extract_function_definition",
    "remove_function_definition",
    "find_import_statements_for_object",
    "replace_import_statement",
    "get_full_tools",
    "get_basic_tools",
    "get_selected_tools",
]


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
def extract_function_definition(filepath: str, function_name: str) -> str:
    """
    Extract a function definition from a source file and return it as a
    standalone-ready code snippet.

    Args:
        filepath: Path to the Python source file.
        function_name: Name of the target function to extract.

    Returns:
        A formatted string containing the function definition and any same-file dependencies.
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


@tool
def replace_import_statement(
    file_path: str, old_import_statement: str, new_import_statement: str
) -> str:
    """
    Replace an existing import statement in a Python source file with a new one.

    Args:
        file_path: Path to the Python source file to update.
        old_import_statement: Exact existing import statement to replace.
        new_import_statement: New import statement to insert.

    Returns:
        A status message describing the result.
    """
    return replace_import_statement_core(file_path, old_import_statement, new_import_statement)


# ── Tool-set helpers ──────────────────────────────────────────────────────

# ag uses ShellTools+FileTools by default; extra tools are the AST tools.
# We keep a registry so the selector can map names → decorated functions.
_TOOL_REGISTRY = {
    "write_function_implementation": write_function_implementation,
    "find_local_import_dependencies": find_local_import_dependencies,
    "find_reference_files": find_reference_files,
    "extract_function_definition": extract_function_definition,
    "remove_function_definition": remove_function_definition,
    "find_import_statements_for_object": find_import_statements_for_object,
}


def get_full_tools() -> list:
    """Return the full set of extra tools for the ag framework."""
    return list(_TOOL_REGISTRY.values())


def get_basic_tools() -> list:
    """Return the basic (empty) tool set for the ag framework."""
    return []


def get_selected_tools(names: list[str]) -> list:
    """
    Return tools matching *names* from the registry.
    Tools not in the registry are silently ignored.
    """
    return [t for name in names if (t := _TOOL_REGISTRY.get(name)) is not None]
