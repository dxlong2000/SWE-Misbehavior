import re
from typing import Any, Callable, Optional

from lxml import etree

from w3lib.html import HTML5_WHITESPACE


regex = f"[{HTML5_WHITESPACE}]+"
replace_html5_whitespaces = re.compile(regex).sub


def set_xpathfunc(fname: str, func: Optional[Callable]) -> None:  # type: ignore[type-arg]
    """This function registers a custom extension function to use in XPath expressions. The function registered under the fname identifier will be called for every matching node, being passed a context parameter as well as any parameters passed from the corresponding XPath expression.
    Input-Output Arguments
    :param fname: String. The identifier under which the function will be registered.
    :param func: Callable. The function to be registered. If None, the extension function will be removed.
    :return: No return values.
    """


def setup() -> None:
    set_xpathfunc("has-class", has_class)


def has_class(context: Any, *classes: str) -> bool:
    """has-class function.

    Return True if all ``classes`` are present in element's class attr.

    """
    if not context.eval_context.get("args_checked"):
        if not classes:
            raise ValueError(
                "XPath error: has-class must have at least 1 argument"
            )
        for c in classes:
            if not isinstance(c, str):
                raise ValueError(
                    "XPath error: has-class arguments must be strings"
                )
        context.eval_context["args_checked"] = True

    node_cls = context.context_node.get("class")
    if node_cls is None:
        return False
    node_cls = " " + node_cls + " "
    node_cls = replace_html5_whitespaces(" ", node_cls)
    for cls in classes:
        if " " + cls + " " not in node_cls:
            return False
    return True