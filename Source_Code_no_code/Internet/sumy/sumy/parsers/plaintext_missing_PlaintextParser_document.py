# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from io import open

from .parser import DocumentParser
from .._compat import to_unicode
from ..models.dom import ObjectDocumentModel, Paragraph, Sentence
from ..utils import cached_property


class PlaintextParser(DocumentParser):
    """
    Parses simple plain text in following format:

    HEADING
    This is text of 1st paragraph. Some another sentence.

    This is next paragraph.

    HEADING IS LINE ALL IN UPPER CASE
    This is 3rd paragraph with heading. Sentence in 3rd paragraph.
    Another sentence in 3rd paragraph.

    Paragraphs are separated by empty lines. And that's all :)
    """

    @classmethod
    def from_string(cls, string, tokenizer):
        return cls(string, tokenizer)

    @classmethod
    def from_file(cls, file_path, tokenizer):
        with open(file_path, encoding="utf-8") as file:
            return cls(file.read(), tokenizer)

    def __init__(self, text, tokenizer):
        super(PlaintextParser, self).__init__(tokenizer)
        self._text = to_unicode(text).strip()

    @cached_property
    def significant_words(self):
        words = []
        for paragraph in self.document.paragraphs:
            for heading in paragraph.headings:
                words.extend(heading.words)

        if words:
            return tuple(words)
        else:
            return self.SIGNIFICANT_WORDS

    @cached_property
    def stigma_words(self):
        return self.STIGMA_WORDS

    @cached_property
    def document(self):
        """This function parses the plaintext document saves in this instance and creates a document model object. It iterates through each line of the input text, identifies sentences and paragraphs, and creates corresponding objects. The final document model is returned.
        Input-Output Arguments
        :param self: PlaintextParser. An instance of the PlaintextParser class.
        :return: ObjectDocumentModel. The created document model object.
        """

    def _to_sentences(self, lines):
        text = ""
        sentence_objects = []

        for line in lines:
            if isinstance(line, Sentence):
                if text:
                    sentence_objects.extend(self._to_sentence_objects(text))

                sentence_objects.append(line)
                text = ""
            else:
                text += " " + line

        text = text.strip()
        if text:
            sentence_objects.extend(self._to_sentence_objects(text))

        return sentence_objects

    def _to_sentence_objects(self, text):
        return (Sentence(s, self._tokenizer) for s in self.tokenize_sentences(text))