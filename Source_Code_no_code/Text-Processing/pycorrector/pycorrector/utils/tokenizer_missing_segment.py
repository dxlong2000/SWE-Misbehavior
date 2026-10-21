# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 切词器
"""

import os
import re

import jieba
from jieba import posseg

from pycorrector.utils.text_utils import is_chinese_string

jieba.setLogLevel(log_level="ERROR")

# \u4E00-\u9FA5a-zA-Z0-9+#&\._ : All non-space characters. Will be handled with re_han
# \r\n|\s : whitespace characters. Will not be handled.
re_han = re.compile("([\u4E00-\u9Fa5a-zA-Z0-9+#&]+)", re.U)
re_skip = re.compile("(\r\n\\s)", re.U)


def split_2_short_text(text, include_symbol=True):
    """
    文本切分为句子，以标点符号切分
    :param text: str
    :param include_symbol: bool
    :return: (sentence, idx)
    """
    result = []
    sentences = re_han.split(text)
    start_idx = 0
    for sentence in sentences:
        if not sentence:
            continue
        if include_symbol:
            result.append((sentence, start_idx))
        else:
            if re_han.match(sentence):
                result.append((sentence, start_idx))
        start_idx += len(sentence)
    return result


def split_text_by_maxlen(text, maxlen=512):
    """
    文本切分为句子，以句子maxlen切分
    :param text: str
    :param maxlen: int, 最大长度
    :return: list, (sentence, idx)
    """
    result = []
    for i in range(0, len(text), maxlen):
        result.append((text[i:i + maxlen], i))
    return result


def tokenize_words(text):
    """Word segmentation"""
    output = []
    sentences = split_2_short_text(text, include_symbol=True)
    for sentence, idx in sentences:
        if is_chinese_string(sentence):
            import jieba
            output.extend(jieba.lcut(sentence))
        else:
            output.extend(whitespace_tokenize(sentence))
    return output


def whitespace_tokenize(text):
    """Runs basic whitespace cleaning and splitting on a peice of text."""
    tokens = []
    if not text:
        return tokens
    sents = split_2_short_text(text, include_symbol=True)
    for sent, idx in sents:
        tokens.extend(sent.split())
    return tokens


class FullTokenizer(object):
    """Given Full tokenization."""

    def __init__(self, lower=True):
        self.lower = lower

    def tokenize(self, text):
        """Tokenizes a piece of text."""
        res = []
        if len(text) == 0:
            return res

        if self.lower:
            text = text.lower()
        # for the multilingual and Chinese
        res = tokenize_words(text)
        return res


def segment(sentence, cut_type='word', pos=False):
    """This function segments the input sentence into words or characters based on the given cut type. It also provides the option to enable POS tagging.
    Input-Output Arguments
    :param sentence: String. The input sentence to be segmented.
    :param cut_type: String. The type of segmentation to be used. It defaults to 'word' if not specified.
    :param pos: Bool. Whether to enable POS tagging. It defaults to False if not specified.
    :return: List. The segmented words or characters along with their POS tags if enabled.
    """


class Tokenizer(object):
    def __init__(self, dict_path='', custom_word_freq_dict=None, custom_confusion_dict=None):
        self.model = jieba
        jieba.setLogLevel("ERROR")
        # 初始化大词典
        if os.path.exists(dict_path):
            self.model.set_dictionary(dict_path)
        # 加载用户自定义词典
        if custom_word_freq_dict:
            for w, f in custom_word_freq_dict.items():
                self.model.add_word(w, freq=f)

        # 加载混淆集词典
        if custom_confusion_dict:
            for k, word in custom_confusion_dict.items():
                # 添加到分词器的自定义词典中
                self.model.add_word(k)
                self.model.add_word(word)

    def tokenize(self, unicode_sentence, mode="search"):
        """
        切词并返回切词位置, search mode用于错误扩召回
        :param unicode_sentence: query
        :param mode: search, default, ngram
        :param HMM: enable HMM
        :return: (w, start, start + width) model='default'
        """
        if mode == 'ngram':
            n = 2
            result_set = set()
            tokens = self.model.lcut(unicode_sentence)
            tokens_len = len(tokens)
            start = 0
            for i in range(0, tokens_len):
                w = tokens[i]
                width = len(w)
                result_set.add((w, start, start + width))
                for j in range(i, i + n):
                    gram = "".join(tokens[i:j + 1])
                    gram_width = len(gram)
                    if i + j > tokens_len:
                        break
                    result_set.add((gram, start, start + gram_width))
                start += width
            results = list(result_set)
            result = sorted(results, key=lambda x: x[-1])
        else:
            result = list(self.model.tokenize(unicode_sentence, mode=mode))
        return result


if __name__ == '__main__':
    text = "这个消息在北京城里不胫儿走，你好，我才来到这里。你呢？"
    print(text)

    t = Tokenizer()
    print('deault', t.tokenize(text, 'default'))
    print('search', t.tokenize(text, 'search'))
    print('ngram', t.tokenize(text, 'ngram'))

    paragraph = "The first time I heard that song was in Hawaii on radio. " \
                "I was just a kid, and loved it very much! What a fantastic song!"
    cutwords1 = whitespace_tokenize(paragraph)  # 分词
    print('【my分词结果：】', cutwords1)

    print('----\n', text)
    r = split_2_short_text(text, include_symbol=True)
    print('split_2_short_text:',r)
    r = split_text_by_maxlen(text, maxlen=4)
    print('split_text_by_maxlen:',r)