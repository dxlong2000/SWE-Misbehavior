import os
import ast
import shutil
from collections.abc import Sequence
from pathlib import Path

from pydantic import Field

from openhands.sdk import (
    Action,
    ImageContent,
    Observation,
    TextContent,
    ToolDefinition,
)
from openhands.sdk.tool import ToolExecutor, register_tool

from common.config import DEVEVAL
from common.tools_core import (
    find_reference_files_core,
    write_function_implementation_core,
    find_local_import_dependencies_core,
    extract_function_definition_core,
    remove_function_definition_core,
    find_import_statements_for_object_core,
)

__all__ = [
    "WriteFunctionImplementationTool",
    "FindLocalImportDependenciesTool",
    "FindReferenceFilesTool",
    "ExtractFunctionDefinitionTool",
    "RemoveFunctionDefinitionTool",
    "FindImportStatementsForObjectTool",
    "register_runtime_tools",
    "get_extra_tool_names",
    "get_selected_tool_names",
]

# ── Workspace root (set by register_runtime_tools) ────────────────────────

_workspace_root: str | None = None


def _resolve(p: str) -> Path:
    """Resolve a path against the workspace root if relative."""
    path = Path(p)
    if not path.is_absolute() and _workspace_root:
        path = Path(_workspace_root) / path
    return path


# ── Helper: tool name list ─────────────────────────────────────────────────

def get_extra_tool_names(full_tools: bool = False) -> list[str]:
    """Return the list of extra tool names for the oh framework."""
    if not full_tools:
        return []
    return [
        WriteFunctionImplementationTool.name,
        FindLocalImportDependenciesTool.name,
        FindReferenceFilesTool.name,
        ExtractFunctionDefinitionTool.name,
        RemoveFunctionDefinitionTool.name,
        FindImportStatementsForObjectTool.name,
    ]


# Mapping from selector tool name → oh tool class name attribute
_TOOL_NAME_REGISTRY = {
    "write_function_implementation": WriteFunctionImplementationTool,
    "find_local_import_dependencies": FindLocalImportDependenciesTool,
    "find_reference_files": FindReferenceFilesTool,
    "extract_function_definition": ExtractFunctionDefinitionTool,
    "remove_function_definition": RemoveFunctionDefinitionTool,
    "find_import_statements_for_object": FindImportStatementsForObjectTool,
}


def get_selected_tool_names(names: list[str]) -> list[str]:
    """
    Return oh tool name strings matching *names* from the registry.
    Tools not in the registry are silently ignored.
    """
    return [
        cls.name
        for name in names
        if (cls := _TOOL_NAME_REGISTRY.get(name)) is not None
    ]


# ── Tool: write_function_implementation ────────────────────────────────────

class WriteFunctionImplementationAction(Action):
    code: str = Field(description="Python statements representing the new function body (statements only).")
    function_name: str = Field(description='Dotted path, e.g. "foo", "MyClass.method".')
    filepath: str = Field(description="Path to the Python source file to modify.")


class WriteFunctionImplementationObservation(Observation):
    result: str = ""

    @property
    def to_llm_content(self) -> Sequence[TextContent | ImageContent]:
        return [TextContent(text=self.result)]


class WriteFunctionImplementationExecutor(ToolExecutor[WriteFunctionImplementationAction, WriteFunctionImplementationObservation]):
    def __call__(self, action: WriteFunctionImplementationAction, conversation=None) -> WriteFunctionImplementationObservation:
        result = write_function_implementation_core(action.code, action.function_name, str(_resolve(action.filepath)))
        return WriteFunctionImplementationObservation(result=result)


class WriteFunctionImplementationTool(ToolDefinition[WriteFunctionImplementationAction, WriteFunctionImplementationObservation]):
    """Replace the implementation body of a target function or method in a Python source file."""

    @classmethod
    def create(cls, conv_state=None, **_):
        return [cls(
            description="Replace the implementation body of a target function or method in a Python source file, preserving docstrings.",
            action_type=WriteFunctionImplementationAction,
            observation_type=WriteFunctionImplementationObservation,
            executor=WriteFunctionImplementationExecutor(),
        )]


# ── Tool: find_local_import_dependencies ──────────────────────────────────

class FindLocalImportDependenciesAction(Action):
    file_path: str = Field(description="Path to the Python source file to analyze.")


class FindLocalImportDependenciesObservation(Observation):
    dependencies: list[str] = Field(default_factory=list)

    @property
    def to_llm_content(self) -> Sequence[TextContent | ImageContent]:
        return [TextContent(text="\n".join(self.dependencies) if self.dependencies else "(none)")]


class FindLocalImportDependenciesExecutor(ToolExecutor[FindLocalImportDependenciesAction, FindLocalImportDependenciesObservation]):
    def __call__(self, action: FindLocalImportDependenciesAction, conversation=None) -> FindLocalImportDependenciesObservation:
        resolved = str(_resolve(action.file_path))
        deps = find_local_import_dependencies_core(resolved)
        if _workspace_root:
            prefix = _workspace_root.rstrip("/") + "/"
            deps = [d[len(prefix):] if d.startswith(prefix) else d for d in deps]
        return FindLocalImportDependenciesObservation(dependencies=deps)


class FindLocalImportDependenciesTool(ToolDefinition[FindLocalImportDependenciesAction, FindLocalImportDependenciesObservation]):
    """Analyze a Python source file and return its local module import dependencies."""

    @classmethod
    def create(cls, conv_state=None, **_):
        return [cls(
            description="Analyze a Python source file and return its local module import dependencies.",
            action_type=FindLocalImportDependenciesAction,
            observation_type=FindLocalImportDependenciesObservation,
            executor=FindLocalImportDependenciesExecutor(),
        )]


# ── Tool: find_reference_files ───────────────────────────────────────────

class FindReferenceFilesAction(Action):
    filepath: str = Field(description="Path to the Python file containing the function.")
    function_name: str = Field(description="Name of the function (e.g. `funcname`, `classname.method`).")


class FindReferenceFilesObservation(Observation):
    files: list[str] = Field(default_factory=list)

    @property
    def to_llm_content(self) -> Sequence[TextContent | ImageContent]:
        return [TextContent(text="\n".join(self.files) if self.files else "(none)")]


class FindReferenceFilesExecutor(ToolExecutor[FindReferenceFilesAction, FindReferenceFilesObservation]):
    def __call__(self, action: FindReferenceFilesAction, conversation=None) -> FindReferenceFilesObservation:
        files = find_reference_files_core(
            action.filepath, action.function_name, workspace_root=_workspace_root
        )
        return FindReferenceFilesObservation(files=files)


class FindReferenceFilesTool(ToolDefinition[FindReferenceFilesAction, FindReferenceFilesObservation]):
    """Find all files that reference a given function."""

    @classmethod
    def create(cls, conv_state=None, **_):
        return [cls(
            description="Find all files that reference a given function.",
            action_type=FindReferenceFilesAction,
            observation_type=FindReferenceFilesObservation,
            executor=FindReferenceFilesExecutor(),
        )]


# ── Tool: extract_function_definition ────────────────────────────────────

class ExtractFunctionDefinitionAction(Action):
    filepath: str = Field(description="Path to the source file.")
    function_name: str = Field(description="Name of the target function to extract.")


class ExtractFunctionDefinitionObservation(Observation):
    content: str = ""

    @property
    def to_llm_content(self) -> Sequence[TextContent | ImageContent]:
        return [TextContent(text=self.content)]


class ExtractFunctionDefinitionExecutor(ToolExecutor[ExtractFunctionDefinitionAction, ExtractFunctionDefinitionObservation]):
    def __call__(self, action: ExtractFunctionDefinitionAction, conversation=None) -> ExtractFunctionDefinitionObservation:
        content = extract_function_definition_core(str(_resolve(action.filepath)), action.function_name)
        return ExtractFunctionDefinitionObservation(content=content)


class ExtractFunctionDefinitionTool(ToolDefinition[ExtractFunctionDefinitionAction, ExtractFunctionDefinitionObservation]):
    """Extract a function definition along with all its dependencies from a source file."""

    @classmethod
    def create(cls, conv_state=None, **_):
        return [cls(
            description="Extract a function definition along with all its dependencies from a source file.",
            action_type=ExtractFunctionDefinitionAction,
            observation_type=ExtractFunctionDefinitionObservation,
            executor=ExtractFunctionDefinitionExecutor(),
        )]


# ── Tool: remove_function_definition ────────────────────────────────────

class RemoveFunctionDefinitionAction(Action):
    filepath: str = Field(description="Path to the Python source file.")
    function_name: str = Field(description='Function name or dotted path (e.g. "func", "Class.method").')


class RemoveFunctionDefinitionObservation(Observation):
    result: str = ""

    @property
    def to_llm_content(self) -> Sequence[TextContent | ImageContent]:
        return [TextContent(text=self.result)]


class RemoveFunctionDefinitionExecutor(ToolExecutor[RemoveFunctionDefinitionAction, RemoveFunctionDefinitionObservation]):
    def __call__(self, action: RemoveFunctionDefinitionAction, conversation=None) -> RemoveFunctionDefinitionObservation:
        result = remove_function_definition_core(str(_resolve(action.filepath)), action.function_name)
        return RemoveFunctionDefinitionObservation(result=result)


class RemoveFunctionDefinitionTool(ToolDefinition[RemoveFunctionDefinitionAction, RemoveFunctionDefinitionObservation]):
    """Remove a function or method from a Python file in-place."""

    @classmethod
    def create(cls, conv_state=None, **_):
        return [cls(
            description="Remove a function or method from a Python file in-place.",
            action_type=RemoveFunctionDefinitionAction,
            observation_type=RemoveFunctionDefinitionObservation,
            executor=RemoveFunctionDefinitionExecutor(),
        )]


# ── Tool: find_import_statements_for_object ─────────────────────────────

class FindImportStatementsForObjectAction(Action):
    file_path: str = Field(description="Path to the Python source file to inspect.")
    object_name: str = Field(description="Imported object, module, alias, or symbol name to search for.")


class FindImportStatementsForObjectObservation(Observation):
    statements: list[str] = Field(default_factory=list)

    @property
    def to_llm_content(self) -> Sequence[TextContent | ImageContent]:
        return [TextContent(text="\n".join(self.statements) if self.statements else "(none)")]


class FindImportStatementsForObjectExecutor(ToolExecutor[FindImportStatementsForObjectAction, FindImportStatementsForObjectObservation]):
    def __call__(self, action: FindImportStatementsForObjectAction, conversation=None) -> FindImportStatementsForObjectObservation:
        statements = find_import_statements_for_object_core(str(_resolve(action.file_path)), action.object_name)
        return FindImportStatementsForObjectObservation(statements=statements)


class FindImportStatementsForObjectTool(ToolDefinition[FindImportStatementsForObjectAction, FindImportStatementsForObjectObservation]):
    """Find all import statements in a Python source file that import a specific object."""

    @classmethod
    def create(cls, conv_state=None, **_):
        return [cls(
            description="Find all import statements in a Python source file that import a specific object.",
            action_type=FindImportStatementsForObjectAction,
            observation_type=FindImportStatementsForObjectObservation,
            executor=FindImportStatementsForObjectExecutor(),
        )]


# ── Registration ───────────────────────────────────────────────────────────

for _tool_cls in [
    WriteFunctionImplementationTool,
    FindLocalImportDependenciesTool,
    FindReferenceFilesTool,
    ExtractFunctionDefinitionTool,
    RemoveFunctionDefinitionTool,
    FindImportStatementsForObjectTool,
]:
    register_tool(_tool_cls.name, _tool_cls)
