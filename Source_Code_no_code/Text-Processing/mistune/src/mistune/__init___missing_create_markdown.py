"""
    mistune
    ~~~~~~~

    A fast yet powerful Python Markdown parser with renderers and
    plugins, compatible with sane CommonMark rules.

    Documentation: https://mistune.lepture.com/
"""

from .markdown import Markdown
from .core import BlockState, InlineState, BaseRenderer
from .block_parser import BlockParser
from .inline_parser import InlineParser
from .renderers.html import HTMLRenderer
from .util import escape, escape_url, safe_entity, unikey
from .plugins import import_plugin


def create_markdown(escape: bool=True, hard_wrap: bool=False, renderer='html', plugins=None) -> Markdown:
    """Create a Markdown instance based on the given condition. 
    
    Input-Output Arguments
    :param escape: Bool, whether to escape HTML if the renderer is set to "html". 
    :param hard_wrap: Bool, whether to break every new line into <br> if the renderer is set to "html".
    :param renderer: renderer instance, default is HTMLRenderer.
    :param plugins: List, a list of plugins.
    
    """


html: Markdown = create_markdown(
    escape=False,
    plugins=['strikethrough', 'footnotes', 'table', 'speedup']
)


__cached_parsers = {}


def markdown(text, escape=True, renderer='html', plugins=None) -> str:
    if renderer == 'ast':
        # explicit and more similar to 2.x's API
        renderer = None
    key = (escape, renderer, plugins)
    if key in __cached_parsers:
        return __cached_parsers[key](text)

    md = create_markdown(escape=escape, renderer=renderer, plugins=plugins)
    # improve the speed for markdown parser creation
    __cached_parsers[key] = md
    return md(text)


__all__ = [
    'Markdown', 'HTMLRenderer',
    'BlockParser', 'BlockState', 'BaseRenderer',
    'InlineParser', 'InlineState',
    'escape', 'escape_url', 'safe_entity', 'unikey',
    'html', 'create_markdown', 'markdown',
]

__version__ = '3.0.2'
__homepage__ = 'https://mistune.lepture.com/'