"""
Module `chatette.terminal_writer`.
Contains a wrapper of the output of commands, that can write to the terminal
(stdout) or to a file.
"""

from __future__ import print_function
import io
import os.path
from enum import Enum


class RedirectionType(Enum):  # QUESTION is it possible to merge this with relevant strings?
    truncate = 1
    append = 2
    quiet = 3


class TerminalWriter(object):
    """Wrapper of `print` that can write to stdout or to a file."""
    def __init__(self, redirection_type=RedirectionType.append,
                 redirection_file_path=None):
        self.redirection_file_path = redirection_file_path
        self.buffered_text = None

        self._file_mode = None
        self.set_redirection_type(redirection_type)

    def reset(self):
        self.redirection_file_path = None
        self.buffered_text = None
    def set_redirection_type(self, redirection_type):
        """
        Sets redirection type.
        @pre: `redirection_type` is of type `RedirectionType`.
        """
        if redirection_type == RedirectionType.append:
            self._file_mode = 'a+'
        elif redirection_type == RedirectionType.truncate:
            self._file_mode = 'w+'
        elif redirection_type == RedirectionType.quiet:
            self._file_mode = 'quiet'

    def get_redirection(self):
        """
        Returns a 2-tuple containing the type and file path of the redirection.
        If this wrapper doesn't redirect to any file (or ignore prints),
        returns `None`.
        """
        if self._file_mode is None:
            return None
        if self._file_mode == 'quiet':
            return (RedirectionType.quiet, None)
        if self._file_mode == 'a+':
            return (RedirectionType.append, self.redirection_file_path)
        if self._file_mode == 'w+':
            return (RedirectionType.truncate, self.redirection_file_path)
        return None


    def write(self, text):
        """This function writes the given text to the terminal. If a redirection file path is not specified and the file mode is not set to "quiet", it prints the text to the terminal. If the file mode is set to "quiet", it does nothing. If a redirection file path is specified, it buffers the text and appends it to the existing buffered text.
        Input-Output Arguments
        :param self: TerminalWriter. An instance of the TerminalWriter class.
        :param text: String. The text to be written to the terminal.
        :return: No return values.
        """

    def error_log(self, text):
        processed_text = ''.join(['\t' + line + '\n'
                                  for line in text.split('\n')])
        self.write("[ERROR]"+processed_text[:-1])


    def flush(self):
        """
        Flushes the buffered text to the redirection file
        if such a file is provided.
        """
        if self.redirection_file_path is not None:
            # Create file if it doesn't exist
            if not os.path.isfile(self.redirection_file_path):
                io.open(self.redirection_file_path, 'w+').close()
            # Write to the file if needed
            if self.buffered_text is not None:
                with io.open(self.redirection_file_path, self._file_mode) as f:
                    print(self.buffered_text, '\n', sep='', file=f)
        self.buffered_text = None