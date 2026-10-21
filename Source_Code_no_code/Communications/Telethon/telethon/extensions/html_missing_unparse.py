"""
Simple HTML -> Telegram entity parser.
"""
import struct
from collections import deque
from html import escape
from html.parser import HTMLParser
from typing import Iterable, Optional, Tuple, List

from ..helpers import add_surrogate, del_surrogate
from ..tl import TLObject
from ..tl.types import (
    MessageEntityBold, MessageEntityItalic, MessageEntityCode,
    MessageEntityPre, MessageEntityEmail, MessageEntityUrl,
    MessageEntityTextUrl, MessageEntityMentionName,
    MessageEntityUnderline, MessageEntityStrike, MessageEntityBlockquote,
    TypeMessageEntity
)


class HTMLToTelegramParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = ''
        self.entities = []
        self._building_entities = {}
        self._open_tags = deque()
        self._open_tags_meta = deque()

    def handle_starttag(self, tag, attrs):
        self._open_tags.appendleft(tag)
        self._open_tags_meta.appendleft(None)

        attrs = dict(attrs)
        EntityType = None
        args = {}
        if tag == 'strong' or tag == 'b':
            EntityType = MessageEntityBold
        elif tag == 'em' or tag == 'i':
            EntityType = MessageEntityItalic
        elif tag == 'u':
            EntityType = MessageEntityUnderline
        elif tag == 'del' or tag == 's':
            EntityType = MessageEntityStrike
        elif tag == 'blockquote':
            EntityType = MessageEntityBlockquote
        elif tag == 'code':
            try:
                # If we're in the middle of a <pre> tag, this <code> tag is
                # probably intended for syntax highlighting.
                #
                # Syntax highlighting is set with
                #     <code class='language-...'>codeblock</code>
                # inside <pre> tags
                pre = self._building_entities['pre']
                try:
                    pre.language = attrs['class'][len('language-'):]
                except KeyError:
                    pass
            except KeyError:
                EntityType = MessageEntityCode
        elif tag == 'pre':
            EntityType = MessageEntityPre
            args['language'] = ''
        elif tag == 'a':
            try:
                url = attrs['href']
            except KeyError:
                return
            if url.startswith('mailto:'):
                url = url[len('mailto:'):]
                EntityType = MessageEntityEmail
            else:
                if self.get_starttag_text() == url:
                    EntityType = MessageEntityUrl
                else:
                    EntityType = MessageEntityTextUrl
                    args['url'] = del_surrogate(url)
                    url = None
            self._open_tags_meta.popleft()
            self._open_tags_meta.appendleft(url)

        if EntityType and tag not in self._building_entities:
            self._building_entities[tag] = EntityType(
                offset=len(self.text),
                # The length will be determined when closing the tag.
                length=0,
                **args)

    def handle_data(self, text):
        previous_tag = self._open_tags[0] if len(self._open_tags) > 0 else ''
        if previous_tag == 'a':
            url = self._open_tags_meta[0]
            if url:
                text = url

        for tag, entity in self._building_entities.items():
            entity.length += len(text)

        self.text += text

    def handle_endtag(self, tag):
        try:
            self._open_tags.popleft()
            self._open_tags_meta.popleft()
        except IndexError:
            pass
        entity = self._building_entities.pop(tag, None)
        if entity:
            self.entities.append(entity)


def parse(html: str) -> Tuple[str, List[TypeMessageEntity]]:
    """
    Parses the given HTML message and returns its stripped representation
    plus a list of the MessageEntity's that were found.

    :param html: the message with HTML to be parsed.
    :return: a tuple consisting of (clean message, [message entities]).
    """
    from ..helpers import strip_text
    if not html:
        return html, []

    parser = HTMLToTelegramParser()
    parser.feed(add_surrogate(html))
    text = strip_text(parser.text, parser.entities)
    return del_surrogate(text), parser.entities


ENTITY_TO_FORMATTER = {
    MessageEntityBold: ('<strong>', '</strong>'),
    MessageEntityItalic: ('<em>', '</em>'),
    MessageEntityCode: ('<code>', '</code>'),
    MessageEntityUnderline: ('<u>', '</u>'),
    MessageEntityStrike: ('<del>', '</del>'),
    MessageEntityBlockquote: ('<blockquote>', '</blockquote>'),
    MessageEntityPre: lambda e, _: (
        "<pre>\n"
        "    <code class='language-{}'>\n"
        "        ".format(e.language), "{}\n"
        "    </code>\n"
        "</pre>"
    ),
    MessageEntityEmail: lambda _, t: ('<a href="mailto:{}">'.format(t), '</a>'),
    MessageEntityUrl: lambda _, t: ('<a href="{}">'.format(t), '</a>'),
    MessageEntityTextUrl: lambda e, _: ('<a href="{}">'.format(escape(e.url)), '</a>'),
    MessageEntityMentionName: lambda e, _: ('<a href="tg://user?id={}">'.format(e.user_id), '</a>'),
}


def unparse(text: str, entities: Iterable[TypeMessageEntity]) -> str:
    """This function takes a normal text and a list of MessageEntity objects and converts them into HTML representation. It checks for special cases, such as empty text or the absence of entities, and utilizes a dictionary to determine HTML formatting for different message entity types. The function handles surrogate pairs and generates the final HTML output by combining formatted text and escaped portions. The goal is to reverse the operation of a parser, producing HTML from plain text and associated entities.
    Input-Output Arguments
    :param text: str. The text to be converted into HTML.
    :param entities: Iterable[TypeMessageEntity]. The list of MessageEntity objects applied to the text.
    :return: str. The HTML representation of the text with applied formatting based on the entities.
    """