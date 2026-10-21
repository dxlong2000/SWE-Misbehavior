import os
import time
import sys
import sysconfig
import ast
import re

from typing import Set


def find_recent_modified_files(root, minutes=5):
    """Return relative paths of files modified within *minutes*."""
    cutoff = time.time() - minutes * 60

    def scan(dirpath):
        with os.scandir(dirpath) as it:
            for entry in it:
                try:
                    if entry.is_file():
                        if entry.stat().st_mtime >= cutoff:
                            yield os.path.relpath(entry.path, root)
                    elif entry.is_dir():
                        yield from scan(entry.path)
                except (PermissionError, FileNotFoundError):
                    pass

    return list(scan(root))


def extract_python_code(text: str) -> str:
    pattern = r"```python\s*(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


def get_local_dependencies(file_path: str) -> list[str]:
    """
    Analyse a Python source file and return its local module dependencies.

    Args:
        file_path: Absolute or relative path to the Python source file.

    Returns:
        Deduplicated list of relative file paths (str) representing local
        dependencies.  Returns an empty list if none are found.
    """

    def _stdlib_modules():
        if hasattr(sys, "stdlib_module_names"):
            return set(sys.stdlib_module_names)
        stdlib_path = sysconfig.get_paths()["stdlib"]
        return {name.split(".")[0] for name in os.listdir(stdlib_path)}

    STDLIB = _stdlib_modules()

    def _resolve(parts, root):
        rel = os.path.join(*parts)
        if os.path.isfile(os.path.join(root, rel + ".py")):
            return rel + ".py"
        if os.path.isfile(os.path.join(root, rel, "__init__.py")):
            return rel.replace(os.sep, "/") + "/__init__.py"
        return None

    def _fwd(p):
        return p.replace(os.sep, "/")

    def _collect(tree, fp):
        results = []
        file_dir = os.path.dirname(os.path.abspath(fp))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    results.append((alias.name.split("."), [None]))
            elif isinstance(node, ast.ImportFrom):
                level = node.level or 0
                module = node.module or ""
                if level > 0:
                    base_dir = file_dir
                    for _ in range(level - 1):
                        base_dir = os.path.dirname(base_dir)
                    base = ["__relative__", base_dir] + (module.split(".") if module else [])
                else:
                    base = module.split(".") if module else []
                names = [a.name for a in node.names] if node.names else [None]
                results.append((base, names))
        return results

    def _resolve_import(base, names, root):
        found = []
        if base and base[0] == "__relative__":
            base_dir, module_parts = base[1], base[2:]
            try:
                rel_base = os.path.relpath(base_dir, os.path.abspath(root))
            except ValueError:
                return []
            if rel_base.startswith(".."):
                return []
            prefix = rel_base.split(os.sep) if rel_base != "." else []
            full = prefix + module_parts
            for name in names:
                r = _resolve(full + [name], root) if name else (_resolve(full, root) if full else None)
                if r is None and name and full:
                    r = _resolve(full, root)
                if r:
                    found.append(_fwd(r))
        else:
            if not base or base[0] in STDLIB:
                return []
            for name in names:
                r = _resolve(base + [name], root) if name else _resolve(base, root)
                if r is None and name:
                    r = _resolve(base, root)
                if r:
                    found.append(_fwd(r))
        return found

    def _to_cwd(deps, root):
        cwd = os.getcwd()
        result = []
        for d in deps:
            abs_dep = os.path.join(root, d)
            rel = os.path.relpath(abs_dep, cwd)
            result.append(rel.replace(os.sep, "/"))
        return result

    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    imports = _collect(tree, file_path)
    rel_imports = [(b, n) for b, n in imports if b and b[0] == "__relative__"]
    abs_imports = [(b, n) for b, n in imports if not b or b[0] != "__relative__"]

    candidates = []
    d = os.path.dirname(os.path.abspath(file_path))
    while True:
        candidates.append(d)
        p = os.path.dirname(d)
        if p == d:
            break
        d = p

    for root in candidates:
        abs_deps = [dep for b, n in abs_imports for dep in _resolve_import(b, n, root)]
        if abs_deps:
            rel_deps = [dep for b, n in rel_imports for dep in _resolve_import(b, n, root)]
            return _to_cwd(list(dict.fromkeys(abs_deps + rel_deps)), root)

    for root in candidates:
        deps = [dep for b, n in rel_imports for dep in _resolve_import(b, n, root)]
        if deps:
            return _to_cwd(list(dict.fromkeys(deps)), root)

    return []


# ── AST helpers (used by extract_function_definition) ────────────────────

class NameCollector(ast.NodeVisitor):
    def __init__(self):
        self.names = set()

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.names.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name):
            self.names.add(node.value.id)
        self.generic_visit(node)


def split_focus(focus: str):
    if "." in focus:
        cls, meth = focus.split(".", 1)
        return cls, meth
    else:
        return focus, None


def find_class_method(defs, class_name, method_name):
    cls = defs.get(class_name)
    if not isinstance(cls, ast.ClassDef):
        return None
    for node in cls.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == method_name:
            return node
    return None


def analyze_dependencies(tree: ast.Module):
    defs = {}
    imports = []
    direct_deps = {}

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defs[node.name] = node
            collector = NameCollector()
            collector.visit(node)
            direct_deps[node.name] = collector.names

        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(node)

    return defs, imports, direct_deps


def compute_needed(defs, direct_deps, focus: str) -> Set[str]:
    needed = set()
    stack = [focus]

    while stack:
        name = stack.pop()
        if name in needed:
            continue
        needed.add(name)

        for dep in direct_deps.get(name, []):
            if dep in defs and dep not in needed:
                stack.append(dep)

    return needed


class PrintStripper(ast.NodeTransformer):
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            node.args = []
            node.keywords = []
        return self.generic_visit(node)


def is_print_call(node):
    return (
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Name)
        and node.value.func.id == "print"
    )


def normalize(program: str, focus: str, rm_print_args: bool = False) -> str:
    """
    Extract *focus* (a function/class name or ``Class.method``) from *program*
    along with all its intra-file dependencies, returning a standalone source
    string.
    """
    tree = ast.parse(program)

    defs, imports, direct_deps = analyze_dependencies(tree)

    cls, meth = split_focus(focus)

    if meth is None:
        if focus not in defs:
            raise ValueError(f"Focus `{focus}` not found.")
        focus_name = focus
    else:
        method_node = find_class_method(defs, cls, meth)
        if method_node is None:
            raise ValueError(f"Method `{focus}` not found.")
        focus_name = cls

    needed = compute_needed(defs, direct_deps, focus_name)

    kept_nodes = []

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name in needed:
                kept_nodes.append(node)

        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names_used = set().union(*(direct_deps.get(n, set()) for n in needed))
            imported_names = set()

            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_names.add(alias.asname or alias.name.split('.')[0])
            else:
                for alias in node.names:
                    imported_names.add(alias.asname or alias.name)

            if names_used & imported_names:
                kept_nodes.append(node)

        elif is_print_call(node):
            kept_nodes.append(node)

    new_tree = ast.Module(body=kept_nodes, type_ignores=[])

    if rm_print_args:
        new_tree = PrintStripper().visit(new_tree)
        ast.fix_missing_locations(new_tree)

    return ast.unparse(new_tree)
