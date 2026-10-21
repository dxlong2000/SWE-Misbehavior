"""
Copyright 2018 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import math
import os
from json.decoder import JSONDecodeError
from statistics import mean

import requests
from x256 import x256

from .x256fgbg_utils import top_2_colors
from ..constants import X256FGBG_CHARS, STORED_CELL_CHAR
from ..utils import memoize


@memoize
def get_gray(*rgb):
    return mean(rgb)


@memoize
def get_256_cell(r, g, b):
    return u'\u001b[38;5;{}m{}'.format(x256.from_rgb(r, g, b), STORED_CELL_CHAR)


@memoize
def get_256fgbg_cell(r, g, b):
    best, second = top_2_colors(r, g, b)
    # if the best color is an exact match, use a blank space for the FG color.
    char = ' '
    if best['distance'] != 0:
        # The bigger the distance of the best color, the more we want the FG
        # color to show up.
        # Cases:
        # best and second are equal - 50BG/50FG - largest X256FGBG_CHARS
        # best is close, second is far away - 90BG/10FG - smaller X256FGBG_CHARS
        ratio = best['distance'] / second['distance']
        char = X256FGBG_CHARS[math.floor(ratio * (len(X256FGBG_CHARS) - 1))]

    return u'\u001b[48;5;{}m\u001b[38;5;{}m{}'.format(
        best['index'],
        second['index'],
        char,
    )


@memoize
def get_truecolor_cell(r, g, b):
    return u'\u001b[38;2;{};{};{}m{}'.format(r, g, b, STORED_CELL_CHAR)


def get_avg_for_em(px, x, y, cell_height, cell_width):
    pixels = [
        px[sx, sy]
        for sy in range(y, y + cell_height)
        for sx in range(x, x + cell_width)
    ]
    return [round(n) for n in map(mean, zip(*pixels))]


def process_input_source(input_source, api_key):
    """This function processes the input source to get the GIF URL. It first checks if the input source is a Tenor GIF URL by checking the input source start with "https://tenor.com/view/". If it is, it extracts the GIF ID and uses it to get the GIF URL. If the input source is not a URL, it sends a request to the Tenor GIF API to get the GIF URL based on the input source.
    Input-Output Arguments
    :param input_source: String. The input source, which can be a Tenor GIF URL, a local file path, or a search query.
    :param api_key: String. The API key for accessing the Tenor GIF API.
    :return: String. The GIF URL obtained from the input source.
    """