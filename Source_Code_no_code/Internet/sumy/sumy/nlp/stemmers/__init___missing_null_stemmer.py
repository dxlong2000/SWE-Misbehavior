# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import nltk.stem.snowball as nltk_stemmers_module

from .czech import stem_word as czech_stemmer
from .ukrainian import stem_word as ukrainian_stemmer
from .greek import stem_word as greek_stemmer


from ...utils import normalize_language


def null_stemmer(object):
    """This function takes an object as input and converts it to a lowercase Unicode string.
    Input-Output Arguments
    :param object: Any data type. The object to be converted to lowercase Unicode.
    :return: String. The converted object in lowercase Unicode.
    """


class Stemmer(object):
    SPECIAL_STEMMERS = {
        'czech': czech_stemmer,
        'slovak': czech_stemmer,
        'hebrew': null_stemmer,
        'chinese': null_stemmer,
        'japanese': null_stemmer,
        'korean': null_stemmer,
        'ukrainian': ukrainian_stemmer,
        'greek': greek_stemmer,
    }

    def __init__(self, language):
        language = normalize_language(language)
        self._stemmer = null_stemmer
        if language.lower() in self.SPECIAL_STEMMERS:
            self._stemmer = self.SPECIAL_STEMMERS[language.lower()]
            return
        stemmer_classname = language.capitalize() + 'Stemmer'
        try:
            stemmer_class = getattr(nltk_stemmers_module, stemmer_classname)
        except AttributeError:
            raise LookupError("Stemmer is not available for language %s." % language)
        self._stemmer = stemmer_class().stem

    def __call__(self, word):
        return self._stemmer(word)