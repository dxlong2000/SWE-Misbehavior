# -*- coding: utf-8 -*-
"""Contains a couple of fairly trivial templating methods used for constructing
the loaders and the output filename. Any instances of {{variable_name}} will be
replaced by the corresponding values."""

import os


parent_directory = os.path.dirname(os.path.realpath(__file__))
template_directory = os.path.join(parent_directory, 'templates')


def render_template(string, **context):
    """This function replaces the placeholders in the input string with the corresponding values from the context dictionary.
    Input-Output Arguments
    :param string: String. The input string containing placeholders.
    :param context: Dictionary. The key-value pairs to replace the placeholders in the input string.
    :return: String. The modified string after replacing the placeholders.
    """


def render_template_file(filename, **context):
    if not os.path.isabs(filename):
        filename = os.path.join(template_directory, filename)
    with open(filename, 'r') as f:
        return render_template(f.read(), **context)