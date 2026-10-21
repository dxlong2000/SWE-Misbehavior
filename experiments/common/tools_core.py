import ast
import json
import os
import shutil
import subprocess
import sys
import sysconfig
import tempfile
import textwrap
import re 
from pathlib import Path
from typing import Dict, List, Optional, Set

import jedi

from openai import OpenAI

from .utils import normalize
from .config import API_KEY


# ── find_reference_files ──────────────────────────────────────────────────

def find_reference_files_core(
    filepath: str,
    function_name: str,
    *,
    workspace_root: str | None = None,
) -> List[str]:
    """
    Find all files that reference a given function.

    Args:
        filepath: Path to the Python file containing the function.
        function_name: Name of the function (e.g. ``funcname``, ``Class.method``).
        workspace_root: If provided, relative paths are resolved against this.

    Returns:
        List of relative file paths that reference the function, including
        the source file.
    """
    try:
        path = Path(filepath).resolve()
        if not path.exists():
            return [f"Error: File `{filepath}` does not exist."]

        source = path.read_text(encoding="utf-8")

        parts = filepath.split("/")
        if workspace_root:
            search_root = Path(workspace_root) / parts[0] / parts[1]
        else:
            search_root = Path(parts[0]) / parts[1]

        project = jedi.Project(
            path=search_root,
            smart_sys_path=False,
            load_unsafe_extensions=False,
        )
        script = jedi.Script(code=source, path=str(path), project=project)

        target_name = function_name.split(".")[-1]
        names = script.get_names(all_scopes=True, definitions=True)

        target_defs = []
        for n in names:
            if n.name == target_name:
                if n.full_name:
                    if n.full_name == function_name or n.full_name.endswith(f".{function_name}"):
                        target_defs.append(n)
                else:
                    if "." not in function_name:
                        target_defs.append(n)

        if not target_defs:
            return [f"Function `{function_name}` not found in `{filepath}`."]

        reference_files: Set[Path] = set()

        for definition in target_defs:
            try:
                refs = script.get_references(line=definition.line, column=definition.column)
            except Exception:
                continue
            for ref in refs:
                if ref.module_path:
                    reference_files.add(Path(ref.module_path))

        reference_files.add(path)

        # Fallback: AST-based search for cross-file references
        for py_file in search_root.rglob("*.py"):
            if py_file in reference_files:
                continue
            try:
                file_source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(file_source)
            except Exception:
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.Name, ast.Attribute)):
                    name = node.id if isinstance(node, ast.Name) else node.attr
                    if name == target_name:
                        reference_files.add(py_file)
                        break

        cwd = Path(workspace_root).resolve() if workspace_root else Path.cwd().resolve()
        result = []
        for p in reference_files:
            try:
                result.append(str(p.relative_to(cwd)))
            except ValueError:
                result.append(str(p))

        return sorted(set(result))

    except Exception as e:
        return [f"Error: {e}"]


def read_file_core(file: str) -> str:
    """Read a UTF-8 encoded text file and return its contents."""
    return Path(file).read_text(encoding="utf-8")


def update_content_core(filepath: str, content: str) -> None:
    """Write text content to a file (UTF-8)."""
    Path(filepath).write_text(content, encoding="utf-8")


def remove_file_core(filepath: str) -> None:
    """Remove a file at the specified path."""
    try:
        os.unlink(filepath)
    except Exception as e:
        print("Cannot delete the file due to the following error:", e)


def write_function_implementation_core(
    code: str, function_name: str, filepath: str | Path
) -> str:
    """
    Replace the implementation body of a target function or method in a
    Python source file, preserving docstrings.

    Args:
        code: Python statements representing the new function body.
        function_name: Dotted path (e.g. ``foo``, ``MyClass.method``).
        filepath: Path to the Python source file to modify in place.

    Returns:
        Success or error message.
    """
    try:
        path = Path(filepath)
        source = path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {e}"

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return f"Syntax error in source file at line {e.lineno}: {e.msg}"

    code = textwrap.dedent(code).strip()
    try:
        replacement_body = ast.parse(code).body
    except SyntaxError as e:
        return f"Invalid replacement code at line {e.lineno}: {e.msg}"

    target_path = function_name.split(".")
    lines = source.splitlines(keepends=True)
    target_node = None

    class Finder(ast.NodeVisitor):
        def __init__(self):
            self.stack = []

        def visit_ClassDef(self, node):
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        def visit_FunctionDef(self, node):
            self._handle(node)

        def visit_AsyncFunctionDef(self, node):
            self._handle(node)

        def _handle(self, node):
            nonlocal target_node
            if self.stack + [node.name] == target_path:
                target_node = node
                return
            self.generic_visit(node)

    Finder().visit(tree)

    if target_node is None:
        return f"Error: Function '{function_name}' not found."

    try:
        body = target_node.body
        insert_at = 0
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            insert_at = 1

        if len(body) > insert_at:
            start_lineno = body[insert_at].lineno
            end_lineno = body[-1].end_lineno
        else:
            start_lineno = target_node.body[-1].end_lineno + 1
            end_lineno = start_lineno - 1

        indent = " " * (target_node.col_offset + 4)
        if replacement_body:
            new_lines = [
                indent + line + "\n"
                for stmt in replacement_body
                for line in ast.unparse(stmt).splitlines()
            ]
        else:
            new_lines = [indent + "pass\n"]

        path.write_text(
            "".join(lines[: start_lineno - 1] + new_lines + lines[end_lineno:]),
            encoding="utf-8",
        )
        return f"Successfully updated '{function_name}'."
    except Exception as e:
        return f"Error updating function '{function_name}': {e}"


def find_local_import_dependencies_core(file_path: str) -> list[str]:
    """
    Find all file's local module dependencies.

    Args:
        file_path: Absolute or relative path to the Python source file.

    Returns:
        Deduplicated list of relative file paths representing local
        dependencies.
    """
    from .utils import get_local_dependencies

    return get_local_dependencies(file_path)


def extract_function_definition_core(filepath: str | Path, function_name: str) -> str:
    """
    Extract a function definition from a source file and return it as a
    standalone-ready code snippet.
    """
    program = Path(filepath).read_text(encoding="utf-8")
    return normalize(program, function_name, False)


def remove_function_definition_core(filepath: str, function_name: str) -> str:
    """
    Remove a function or method (possibly nested like ``A.B.func``) from a
    Python file in-place.
    """

    class FunctionLocator(ast.NodeVisitor):
        def __init__(self, target_path: List[str]):
            self.target_path = target_path
            self.stack = []
            self.target_node: Optional[ast.AST] = None

        def visit_ClassDef(self, node):
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        def visit_FunctionDef(self, node):
            self.stack.append(node.name)
            if self.stack == self.target_path:
                self.target_node = node
            self.generic_visit(node)
            self.stack.pop()

        def visit_AsyncFunctionDef(self, node):
            self.visit_FunctionDef(node)

    try:
        path = Path(filepath)
        if not path.exists():
            return f"Error: File `{filepath}` does not exist."
        source = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            return f"Error: Failed to parse `{filepath}` ({e})."

        locator = FunctionLocator(function_name.split("."))
        locator.visit(tree)
        node = locator.target_node
        if node is None:
            return f"Function `{function_name}` not found in `{filepath}`."
        if not hasattr(node, "end_lineno"):
            return "Error: Python version does not support end_lineno."

        lines = source.splitlines()
        start, end = node.lineno - 1, node.end_lineno
        while start > 0 and lines[start - 1].lstrip().startswith("@"):
            start -= 1

        new_lines, prev_blank = [], False
        for line in lines[:start] + lines[end:]:
            is_blank = not line.strip()
            if is_blank and prev_blank:
                continue
            new_lines.append(line)
            prev_blank = is_blank

        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return f"Successfully removed `{function_name}` from `{filepath}`."
    except Exception as e:
        return f"Error: {e}"


def find_import_statements_for_object_core(
    file_path: str | Path, object_name: str
) -> list[str]:
    """
    Find all import statements in a Python source file that import a specific
    object.
    """
    path = Path(file_path)
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    matches: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                candidates = {alias.name, alias.name.split(".")[0]}
                if alias.asname:
                    candidates.add(alias.asname)
                if object_name in candidates:
                    matches.append(ast.get_source_segment(source, node) or "")
                    break
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                candidates = {alias.name}
                if alias.asname:
                    candidates.add(alias.asname)
                if object_name in candidates:
                    matches.append(ast.get_source_segment(source, node) or "")
                    break
    return matches


class ToolSelector:
    system_prompt = """You are a tool-selection agent for a coding assistant.

Your responsibility is ONLY to select the most appropriate tools for the task.

You do NOT:
- Execute tools
- Solve the task
- Modify code
- Generate patches or implementations

You are given:
- A user request
- A list of available tools and their specifications

Your objective:
1. Infer the actual task requirements
2. Select the minimal sufficient set of tools
3. Avoid irrelevant or redundant tools

Core Principles:
- Select tools based on functional necessity, not keyword matching
- Prefer specialized tools over generic editing tools
- Prefer the smallest toolset that can complete the task reliably
- Avoid modification tools for read-only or analysis-only tasks

Guidelines:

### Local vs cross-file reasoning
- If the task is fully self-contained within a single file, avoid unnecessary repository-analysis tools
- If the task requires understanding imported symbols, helper utilities, shared constants, inherited behavior, neighboring modules, repository context, integration behavior, or project-wide interactions, include:
  - find_local_import_dependencies

- Phrases such as:
  - "under the context of ..."
  - "repository context"
  - "project-wide behavior"
  - "integration"
  - "compatible with existing code"
  - "behavior preservation"
  strongly suggest cross-file reasoning

### Read-only / analysis tasks
- If the task only requires understanding, extracting, analyzing, testing, or debugging code, avoid modification tools

### Function implementation tasks
- For simple self-contained function implementation tasks, typically prefer:
  - read_file
  - write_function_implementation

- If correct implementation, testing, or debugging depends on repository context or imported local modules, also include:
  - find_local_import_dependencies

### Cross-file usage and dependency reasoning
- If the task requires understanding references, usages, imports, or dependencies across files, consider:
  - find_reference_files
  - find_local_import_dependencies
  - find_import_statements_for_object

### Refactoring / moving code
- If the task involves moving, relocating, modularizing, or reusing functions across files, consider:
  - extract_function_definition
  - remove_function_definition
  - update_content
  - find_reference_files
  - find_import_statements_for_object

### File editing strategy
- Use update_content only when broader file-level modifications are necessary
- Prefer targeted editing tools over generic file overwrite tools

### Deletion tasks
- For removing functions or definitions, prefer:
  - remove_function_definition
- Avoid unrelated editing tools unless additional modifications are required

Reason briefly about the task requirements and tool necessity.

Then output the final selected tools as a Python list of strings wrapped in <ANSWER> and </ANSWER> tags.

Example:
<ANSWER>["read_file", "write_function_implementation"]</ANSWER>

Example:
<ANSWER>["read_file", "find_local_import_dependencies", "write_function_implementation"]</ANSWER>
"""

    tool_specifications = """
- find_reference_files(filepath: str, function_name: str) -> List[str]
    <specification>
        Find all files that reference a given function.

        Args:
            filepath: Path to the Python file containing the function.
            function_name: Name of the function (e.g, `funcname`, `classname.method`).

        Returns:
            List of relative file paths (to current working directory)
            that reference the function, including the source file.
    </specification>

- read_file(file: str) -> str
    <specification>
        Read a UTF-8 encoded text file and optionally include its local dependencies.

        This function reads the file at the given path and returns its contents as a single string.

        Args:
            file (str): Path to the file to be opened and read.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            UnicodeDecodeError: If the file cannot be decoded using UTF-8 encoding.
            OSError: If an I/O error occurs while opening or reading the file.
    </specification>

- update_content(filepath: str, content: str) -> None
    <specification>
        Write text content to a file.

        This function writes the given content to the file at the specified
        path using UTF-8 encoding. If the file already exists, it will be
        overwritten. If it does not exist, a new file will be created.

        Args:
            filepath (str): Path to the file to be written.
            content (str): Text content to write into the file.

        Returns:
            None

        Raises:
            OSError: If an I/O error occurs while writing to the file.
    </specification>

- remove_file(filepath: str) -> None
    <specification>
        Remove a file at the specified path.

        This function attempts to delete the file located at ``filepath``. 
        If the deletion fails, the error is caught and printed.

        Args:
            filepath (str): The path to the file to be removed.

        Returns:
            None

        Raises:
            None: All exceptions are caught internally and reported via printing.
    </specification>

- write_function_implementation(code: str, function_name: str, filepath: Path | str) -> str
    <specification>
        Replace the implementation body of a target function or method in a Python source file.

        The specified function is located by name
        (including top-level functions, class methods, or nested class methods),
        and its body statements are replaced with the provided code. Existing
        docstrings are preserved when present.

        Args:
            code (str):
                Python statements representing the new function body (statements only)
            function_name (str):
                Dotted path identifying the target callable, for example:
                - "foo"
                - "MyClass.method"
                - "Outer.Inner.method"
            filepath (Path | str):
                Path to the Python source file to modify in place.

        Returns:
            str:
                Success or error message.

        Raises:
            ValueError:
                If the target function or method cannot be found.
            SyntaxError:
                If the source file or replacement body cannot be parsed as valid Python.
    </specification>

- find_local_import_dependencies(file_path: str) -> list[str]
    <specification>
        Find all file's local module dependencies.

        Args:
            file_path (str): Absolute or relative path to the Python source file to analyze.

        Returns:
            list: Deduplicated list of relative file paths (str) representing local dependencies. 
            Returns an empty list if no local dependencies are found.
    </specification>

- extract_function_definition(filepath: str | Path, function_name: str) -> str
    <specification>
        Extract a function definition from a source file and return it as a
        standalone-ready code snippet.

        The returned string contains the target function's definition followed by
        a note listing locally defined objects in the same file that it depends on.
        Those listed objects should also be included or imported if the function is
        used outside its original module.

        Args:
            filepath: Path to the Python source file.
            function_name: Name of the target function to extract.

        Returns:
            A formatted string containing the function definition and any same-file
            dependencies required to reuse it independently.
    </specification>

- remove_function_definition(filepath: str, function_name: str) -> str
    <specification>
        Remove a function or method (possibly nested like "A.B.func") from a Python file in-place.

        Args:
            filepath: Path to the Python source file.
            function_name: Function name or dotted path (e.g., "func", "Class.method", "A.B.func").

        Returns:
            Status message indicating success or failure.
    </specification>

- find_import_statements_for_object(file_path: str | Path, object_name: str) -> list[str]
    <specification>
        This tool helps find all import statements in a Python source file that import a specific object.

        Args:
            file_path: Path to the Python source file to inspect.
            object_name: Imported object, module, alias, or symbol name to search for.

        Returns:
            A list of source-code strings representing matching import statements,
            in the same order they appear in the file. Returns an empty list if
            no matching imports are found.

        Raises:
            FileNotFoundError: If the file does not exist.
            SyntaxError: If the file contains invalid Python syntax.
    </specification>
"""

    def __init__(self, model_id: str = "google/gemini-3-flash-preview", temperature: float = 0.1, system_prompt: str = system_prompt, retry: int = 5):
        self.model_id = model_id
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.retry = retry
    
    def reason_on(self, task: str):
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=API_KEY
        )

        user_prompt = f"""User request: "{task}"
Here are the list of available tools and their specifications:
{self.tool_specifications}
"""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        pattern = r"<ANSWER>\s*(.*?)\s*</ANSWER>"

        for attempt in range(self.retry):
            completion = client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=self.temperature
            )

            response = completion.choices[0].message.content
            if not response:
                continue

            result = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if result:
                tool_list = result.group(1)
                try:
                    return {
                        "reasoning": response,
                        "tools": ast.literal_eval(tool_list),
                        "cost": completion.usage.cost,
                    }
                except Exception:
                    if attempt == self.retry - 1:
                        raise ValueError("Cannot parse the list")
                    continue
                
        raise ValueError("Cannot parse the list")


class GuidelineSelector:
    system_prompt = """You are a guideline selection model for coding tasks.

Your task is to analyze a coding request and select the minimum subset of relevant guidelines from a predefined numbered guideline set. The selected guidelines should be sufficient for completing the task safely, correctly, and efficiently.

## Input

You will receive a coding task request and a numbered list of guidelines.

## Instructions

1. Read the task and identify the core operations required (e.g., implementation, refactoring, testing, debugging, execution, dependency updates, repository-wide changes).

2. Select only the guidelines that are directly relevant to those operations.

3. Exclude guidelines that are unrelated to the task or only loosely applicable.

4. Keep the selection minimal: choose the smallest sufficient subset of guidelines.

5. Briefly reason about the task before producing the final answer, focusing only on task requirements.

## Output Requirements

The final answer must contain only a list of integer guideline IDs.

* The list must be wrapped with <ANSWER> and </ANSWER>.

* Sort guideline numbers in ascending order.

* Do NOT invent guideline numbers.

## Output Format

Reasoning: <brief reasoning>

<ANSWER>[<id1>, <id2>, ...]</ANSWER>

## Examples of Output Format

Reasoning: The task requires implementing functionality and updating related dependencies, so only implementation and dependency-consistency guidelines are needed.

<ANSWER>[2, 5, 8]</ANSWER>

---

Reasoning: The task focuses on running tests and fixing failures, so testing and debugging-related guidelines are relevant.

<ANSWER>[3, 6, 9, 12]</ANSWER>
"""
    
    guidelines = [
        "Before acting, identify which tools you will need to complete the task and plan your approach accordingly",
        "Inspect relevant files, surrounding code, and local dependencies to understand structure, conventions, and relationships before making any changes",
        "Verify that all referenced paths, functions, and imports exist and are resolvable",
        "Limit all changes strictly to what the task requires — do not modify unrelated files, code paths, or content",
        "Alter only the specific target component within a file; leave all other content intact",
        "Ensure all produced or modified code is syntactically valid and internally consistent",
        "Keep changes consistent with the repository's existing style, patterns, naming, and architecture",
        "Reuse existing implementations where appropriate instead of duplicating logic",
        "Preserve existing behavior unless the task explicitly requires changing it",
        "When moving or extracting code, move only the targeted definition itself without modifying its implementation — do not carry over unrelated code or context from the source file; update all affected imports, references, and call sites; and add only the dependencies that the moved code strictly requires",
        "Only create files when necessary to complete the task; only delete files when clearly required — otherwise, do not create or delete any files",
        "Remove any temporary files used for testing, execution, or debugging before declaring the task complete",
    ]

    def __init__(self, model_id: str = "google/gemini-3-flash-preview", temperature: float = 0.1, system_prompt: str = system_prompt, retry: int = 5):
        self.model_id = model_id
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.retry = retry
        
    def reason_on(self, task: str):
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=API_KEY
        )
        
        guidelines_str = ""
        for id, item in enumerate(self.guidelines, start=1):
            guidelines_str += f"{id}. {item}\n"

        user_prompt = f"""User request: "{task}"
Here are the list of guidelines:

{guidelines_str}
"""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        pattern = r"Reasoning:\s*(.*?)\s*<ANSWER>\s*(.*?)\s*</ANSWER>"

        for attempt in range(self.retry):
            completion = client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=self.temperature
            )

            response = completion.choices[0].message.content
            if not response:
                continue

            result = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if result:
                reasoning = result.group(1).strip()
                guidelines = ast.literal_eval(result.group(2).strip())
                try:
                    return {
                        "reasoning": reasoning,
                        "guidelines": guidelines,
                        "cost": completion.usage.cost,
                    }
                except Exception:
                    if attempt == self.retry - 1:
                        raise ValueError("Cannot parse the response")
                    continue

        raise ValueError("Cannot parse the response")
    
    @staticmethod 
    def parse_glids(ids: list[int]):
        return [GuidelineSelector.guidelines[id-1] for id in ids]