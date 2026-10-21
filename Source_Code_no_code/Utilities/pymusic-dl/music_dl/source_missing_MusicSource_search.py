#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author: HJK
@file: source.py
@time: 2019-05-13
"""

"""
    Music source proxy object
"""

import re
import threading
import importlib
import traceback
import logging
import click
from . import config
from .utils import colorize
from .exceptions import *


class MusicSource:
    """
        Music source proxy object
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def search(self, keyword, sources_list) -> list:
        """This function searches for a keyword in a list of music sources. It creates multiple threads to search for the keyword in each source concurrently. It then sorts and removes duplicates from the search results based on song title, singer, and file size.
        Input-Output Arguments
        :param self: MusicSource. An instance of the MusicSource class.
        :param keyword: String. The keyword to search for in the music sources.
        :param sources_list: List of strings. The list of music sources to search in.
        :return: List of songs. The search results containing songs that match the keyword.
        """

    def search_thread(self, source, keyword, ret_songs_list, ret_errors):
        try:
            addon = importlib.import_module(".addons." + source, __package__)
            ret_songs_list += addon.search(keyword)
        except (RequestError, ResponseError, DataError) as e:
            ret_errors.append((source, e))
        except Exception as e:
            # 最后一起输出错误信息免得影响搜索结果列表排版
            err = traceback.format_exc() if config.get("verbose") else str(e)
            ret_errors.append((source, err))
        finally:
            # 放在搜索后输出是为了营造出搜索很快的假象
            click.echo(" %s ..." % colorize(source.upper(), source), nl=False)

    def single(self, url):
        sources_map = {
            # "baidu.com": "baidu",
            # "flac": "flac",
            # "kugou.com": "kugou",
            "163.com": "netease",
            # "qq.com": "qq",
            # "xiami.com": "xiami",
        }
        sources = [v for k, v in sources_map.items() if k in url]
        if not sources:
            raise ParameterError("Invalid url.")
        source = sources[0]
        click.echo(_("Downloading song from %s ..." % source.upper()))
        try:
            addon = importlib.import_module(".addons." + source, __package__)
            song = addon.single(url)
            return song
        except (RequestError, ResponseError, DataError) as e:
            self.logger.error(e)
        except Exception as e:
            # 最后一起输出错误信息免得影响搜索结果列表排版
            err = traceback.format_exc() if config.get("verbose") else str(e)
            self.logger.error(err)

    def playlist(self, url) -> list:
        sources_map = {
            # "baidu.com": "baidu",
            # "flac": "flac",
            # "kugou.com": "kugou",
            "163.com": "netease",
            # "qq.com": "qq",
            # "xiami.com": "xiami",
        }
        sources = [v for k, v in sources_map.items() if k in url]
        if not sources:
            raise ParameterError("Invalid url.")
        source = sources[0]
        click.echo(_("Parsing music playlist from %s ..." % source.upper()))
        ret_songs_list = []
        try:
            addon = importlib.import_module(".addons." + source, __package__)
            ret_songs_list = addon.playlist(url)
        except (RequestError, ResponseError, DataError) as e:
            self.logger.error(e)
        except Exception as e:
            # 最后一起输出错误信息免得影响搜索结果列表排版
            err = traceback.format_exc() if config.get("verbose") else str(e)
            self.logger.error(err)

        return ret_songs_list