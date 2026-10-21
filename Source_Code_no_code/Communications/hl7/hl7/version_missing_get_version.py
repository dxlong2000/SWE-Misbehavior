# -*- coding: utf-8 -*-

"""
Primary version number source.

Forth element can be 'dev' < 'a' < 'b' < 'rc' < 'final'. An empty 4th
element is equivalent to 'final'.
"""
VERSION = (0, 4, 5, "final")


def get_version():
    """This function provides the version number of the software. It follows the verlib format specified in PEP 386. It constructs the version number based on the elements in the version list. If the length of version is less than four or the version type is final, it return the main version. If the type of version is dev, tht output format is "{the main version}.dev". In other condition, the ouput format is "{the main version}{the type of version}".
    Input-Output Arguments
    :param: No input parameters.
    :return: String. The version number of the software.
    """