from .util import striptags


def add_toc_hook(md, min_level=1, max_level=3, heading_id=None):
    """This function adds a hook to save table of contents (TOC) items into the state.env. It is usually helpful for doc generator.
    Input-Output Arguments
    :param md: Markdown instance. The instance of the Markdown class.
    :param min_level: Integer. The minimum heading level to include in the TOC.
    :param max_level: Integer. The maximum heading level to include in the TOC.
    :param heading_id: Function. A function to generate heading_id.
    :return: No return values.
    """


def normalize_toc_item(md, token):
    text = token['text']
    tokens = md.inline(text, {})
    html = md.renderer(tokens, {})
    text = striptags(html)
    attrs = token['attrs']
    return attrs['level'], attrs['id'], text


def render_toc_ul(toc):
    """Render a <ul> table of content HTML. The param "toc" should
    be formatted into this structure::

        [
          (level, id, text),
        ]

    For example::

        [
          (1, 'toc-intro', 'Introduction'),
          (2, 'toc-install', 'Install'),
          (2, 'toc-upgrade', 'Upgrade'),
          (1, 'toc-license', 'License'),
        ]
    """
    if not toc:
        return ''

    s = '<ul>\n'
    levels = []
    for level, k, text in toc:
        item = '<a href="#{}">{}</a>'.format(k, text)
        if not levels:
            s += '<li>' + item
            levels.append(level)
        elif level == levels[-1]:
            s += '</li>\n<li>' + item
        elif level > levels[-1]:
            s += '\n<ul>\n<li>' + item
            levels.append(level)
        else:
            levels.pop()
            while levels:
                last_level = levels.pop()
                if level == last_level:
                    s += '</li>\n</ul>\n</li>\n<li>' + item
                    levels.append(level)
                    break
                elif level > last_level:
                    s += '</li>\n<li>' + item
                    levels.append(last_level)
                    levels.append(level)
                    break
                else:
                    s += '</li>\n</ul>\n'
            else:
                levels.append(level)
                s += '</li>\n<li>' + item

    while len(levels) > 1:
        s += '</li>\n</ul>\n'
        levels.pop()

    return s + '</li>\n</ul>\n'