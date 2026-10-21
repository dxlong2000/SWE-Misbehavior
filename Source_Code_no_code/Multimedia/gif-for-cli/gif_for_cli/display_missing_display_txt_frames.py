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
import time

from .constants import STORED_CELL_CHAR
from .utils import get_sorted_filenames


def display_txt_frames(txt_frames, stdout, num_loops, seconds_per_frame):
    """This function displays a sequence of text frames on the standard output. It iterates through the given text frames and prints each frame on a new line. It also allows for a specified number of loops and a delay between frames. A KeyboardInterrupt will be raised if there is any exception.
    Input-Output Arguments
    :param txt_frames: List of strings. The text frames to be displayed.
    :param stdout: Standard output. The output stream where the frames will be printed.
    :param num_loops: Integer. The number of times the frames should be displayed. If not specified, the frames will be displayed indefinitely.
    :param seconds_per_frame: Float. The delay in seconds between each frame.
    :return: No return values.
    """


def get_txt_frames(display_dirname, cell_char):
    return [
        open('{}/{}'.format(display_dirname, filename)).read().replace(STORED_CELL_CHAR, cell_char)
        for filename in get_sorted_filenames(display_dirname, 'txt')
    ]


def display(display_dirname, stdout, num_loops, cell_char, seconds_per_frame):
    txt_frames = get_txt_frames(display_dirname, cell_char)

    display_txt_frames(txt_frames, stdout, num_loops, seconds_per_frame)