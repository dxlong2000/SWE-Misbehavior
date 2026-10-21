#!/usr/bin/env python


def guess_format(filename):
    """This function tries to guess a file's format based on its extension (or lack thereof). It checks the file extension(in ['csv', 'dbf', 'fixed', 'xls', 'xlsx', 'json']) and returns the corresponding format. 'json' will be returned if the extension is 'js'.
    Input-Output Arguments
    :param filename: String. The name of the file.
    :return: String. The guessed format of the file based on its extension. If the extension is not recognized, it returns None.
    """