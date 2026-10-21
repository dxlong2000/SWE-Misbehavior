# -*- coding: utf-8 -*-

# -------------------------------------------#
# author: sean lee                           #
# email: xmlee97@gmail.com                   #
# -------------------------------------------#

import os
import re
import concurrent.futures as futures
from functools import partial
from typing import Any, Callable, List, Generator

import numpy as np


re_line_skip = re.compile('[\r\n]')
re_delimiter = re.compile('[，。？！；]')


def split_text(doc: str) -> List[str]:
    sents = []
    for line in re_line_skip.split(doc):
        line = line.strip()
        if not line:
            continue
        for sent in re_delimiter.split(line):
            sent = sent.strip()
            if not sent:
                continue
            sents.append(sent)
    return sents


def filelist(path: str) -> Generator[str, None, None]:
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            if not dirs:
                for f in files:
                    yield os.sep.join([root, f])
    else:
        yield path


def load_stopword(fpath: str) -> List[str]:
    """load stopwords from file """
    stopwords = set()
    for fname in filelist(fpath):
        with open(fname, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                stopwords.add(line)
    return stopwords


def rematch(offsets):
    """ rematch bert token
    """
    mapping = []
    for offset in offsets:
        if offset[0] == 0 and offset[1] == 0:
            mapping.append([])
        else:
            mapping.append([i for i in range(offset[0], offset[1])])
    return mapping


def topK(matrix, K, axis=1):
    """ numpy topK
    """
    if axis == 0:
        row_index = np.arange(matrix.shape[1 - axis])
        topk_index = np.argpartition(-matrix, K, axis=axis)[0:K, :]
        topk_data = matrix[topk_index, row_index]
        topk_index_sort = np.argsort(-topk_data, axis=axis)
        topk_data_sort = topk_data[topk_index_sort, row_index]
        topk_index_sort = topk_index[0:K, :][topk_index_sort, row_index]
    else:
        column_index = np.arange(matrix.shape[1 - axis])[:, None]
        topk_index = np.argpartition(-matrix, K, axis=axis)[:, 0:K]
        topk_data = matrix[column_index, topk_index]
        topk_index_sort = np.argsort(-topk_data, axis=axis)
        topk_data_sort = topk_data[column_index, topk_index_sort]
        topk_index_sort = topk_index[:, 0:K][column_index, topk_index_sort]
    return topk_data_sort, topk_index_sort


def parallel_handler(callback: Callable, texts: List[str], n_jobs: int = 2, **kwargs) -> Generator[
    List[Any], None, None
]:
    """This function is a parallel handler that takes a callback function and a list of texts as input. It then processes the texts using the callback function in parallel using a thread pool executor. If the input `texts` is not a list, raise a ValueError("You should pass a list of texts").
    Input-Output Arguments
    :param callback: Callable. The callback function to be applied to the list of texts.
    :param texts: List[str]. The list of texts to be processed.
    :param n_jobs: int. The pool size of threads. Defaults to 2.
    :param kwargs: Any additional keyword arguments to be passed to the callback function.
    :return: Generator[List[Any], None, None]. A generator that yields the results of applying the callback function to the texts in parallel.
    """