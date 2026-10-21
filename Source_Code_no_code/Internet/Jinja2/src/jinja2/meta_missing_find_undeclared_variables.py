"""Functions that expose information about templates that might be
interesting for introspection.
"""
import typing as t

from . import nodes
from .compiler import CodeGenerator
from .compiler import Frame

if t.TYPE_CHECKING:
    from .environment import Environment


class TrackingCodeGenerator(CodeGenerator):
    """We abuse the code generator for introspection."""

    def __init__(self, environment: "Environment") -> None:
        super().__init__(environment, "<introspection>", "<introspection>")
        self.undeclared_identifiers: t.Set[str] = set()

    def write(self, x: str) -> None:
        """Don't write."""

    def enter_frame(self, frame: Frame) -> None:
        """Remember all undeclared identifiers."""
        super().enter_frame(frame)

        for _, (action, param) in frame.symbols.loads.items():
            if action == "resolve" and param not in self.environment.globals:
                self.undeclared_identifiers.add(param)


def find_undeclared_variables(ast: nodes.Template) -> t.Set[str]:
    """This function returns all undeclared variables in the given AST.
    Input-Output Arguments
    :param ast: nodes.Template. The AST of a Jinja2 template.
    :return: Set[str]. A set of all variables in the AST that will be looked up from the context at runtime.
    """


_ref_types = (nodes.Extends, nodes.FromImport, nodes.Import, nodes.Include)
_RefType = t.Union[nodes.Extends, nodes.FromImport, nodes.Import, nodes.Include]


def find_referenced_templates(ast: nodes.Template) -> t.Iterator[t.Optional[str]]:
    """Finds all the referenced templates from the AST.  This will return an
    iterator over all the hardcoded template extensions, inclusions and
    imports.  If dynamic inheritance or inclusion is used, `None` will be
    yielded.

    >>> from jinja2 import Environment, meta
    >>> env = Environment()
    >>> ast = env.parse('{% extends "layout.html" %}{% include helper %}')
    >>> list(meta.find_referenced_templates(ast))
    ['layout.html', None]

    This function is useful for dependency tracking.  For example if you want
    to rebuild parts of the website after a layout template has changed.
    """
    template_name: t.Any

    for node in ast.find_all(_ref_types):
        template: nodes.Expr = node.template  # type: ignore

        if not isinstance(template, nodes.Const):
            # a tuple with some non consts in there
            if isinstance(template, (nodes.Tuple, nodes.List)):
                for template_name in template.items:
                    # something const, only yield the strings and ignore
                    # non-string consts that really just make no sense
                    if isinstance(template_name, nodes.Const):
                        if isinstance(template_name.value, str):
                            yield template_name.value
                    # something dynamic in there
                    else:
                        yield None
            # something dynamic we don't know about here
            else:
                yield None
            continue
        # constant is a basestring, direct template name
        if isinstance(template.value, str):
            yield template.value
        # a tuple or list (latter *should* not happen) made of consts,
        # yield the consts that are strings.  We could warn here for
        # non string values
        elif isinstance(node, nodes.Include) and isinstance(
            template.value, (tuple, list)
        ):
            for template_name in template.value:
                if isinstance(template_name, str):
                    yield template_name
        # something else we don't care about, we could warn here
        else:
            yield None