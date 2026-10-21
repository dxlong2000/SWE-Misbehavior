# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Helper module for laplace smoothing counts."""

import copy
from typing import DefaultDict, List, Tuple


def laplace_smooth_cmd_counts(
    seq1_counts: DefaultDict[str, int],
    seq2_counts: DefaultDict[str, DefaultDict[str, int]],
    start_token: str,
    end_token: str,
    unk_token: str,
) -> Tuple[DefaultDict[str, int], DefaultDict[str, DefaultDict[str, int]]]:
    """
    Apply laplace smoothing to the input counts for the cmds.

    In particular, add 1 to each of the counts, including the unk_token. By including the
    unk_token, we can handle unseen commands.

    Parameters
    ----------
    seq1_counts: DefaultDict[str, int]
        individual command counts
    seq2_counts: DefaultDict[str, DefaultDict[str, int]]
        sequence command (length 2) counts
    start_token: str
        dummy command to signify the start of a session (e.g. "##START##")
    end_token: str
        dummy command to signify the end of a session (e.g. "##END##")
    unk_token: str
        dummy command to signify an unseen command (e.g. "##UNK##")

    Returns
    -------
    tuple of laplace smoothed counts:
        individual command counts,
        sequence command (length 2) counts

    """
    seq1_counts_ls = copy.deepcopy(seq1_counts)
    seq2_counts_ls = copy.deepcopy(seq2_counts)

    cmds: List[str] = list(seq1_counts_ls.keys()) + [unk_token]
    for cmd1 in cmds:
        for cmd2 in cmds:
            if cmd1 != end_token and cmd2 != start_token:
                seq1_counts_ls[cmd1] += 1
                seq2_counts_ls[cmd1][cmd2] += 1
                seq1_counts_ls[cmd2] += 1

    return seq1_counts_ls, seq2_counts_ls


def laplace_smooth_param_counts(
    cmds: List[str],
    param_counts: DefaultDict[str, int],
    cmd_param_counts: DefaultDict[str, DefaultDict[str, int]],
    unk_token: str,
) -> Tuple[DefaultDict[str, int], DefaultDict[str, DefaultDict[str, int]]]:
    """This function applies Laplace smoothing to the input counts for the parameters. It adds 1 to each of the counts, including the unk_token, to handle unseen parameters. it's used for smoothing individual parameter counts (param_counts) and parameter conditional on command counts (cmd_param_counts).
    Input-Output Arguments
    :param cmds: List[str]. List of all the possible commands (including the unk_token).
    :param param_counts: DefaultDict[str, int]. Individual parameter counts.
    :param cmd_param_counts: DefaultDict[str, DefaultDict[str, int]]. Parameter conditional on command counts.
    :param unk_token: str. Dummy command to signify an unseen command (e.g. "##UNK##").
    :return: Tuple[DefaultDict[str, int], DefaultDict[str, DefaultDict[str, int]]]. Individual parameter probabilities, parameter conditional on command probabilities.
    """


def laplace_smooth_value_counts(
    params: List[str],
    value_counts: DefaultDict[str, int],
    param_value_counts: DefaultDict[str, DefaultDict[str, int]],
    unk_token: str,
) -> Tuple[DefaultDict[str, int], DefaultDict[str, DefaultDict[str, int]]]:
    """
    Apply laplace smoothing to the input counts for the values.

    In particular, add 1 to each of the counts, including the unk_token. By including the
    unk_token, we can handle unseen values.

    Parameters
    ----------
    params: List[str]
        list of all possible params, including the unk_token
    value_counts: DefaultDict[str, int]
        individual value counts
    param_value_counts: DefaultDict[str, DefaultDict[str, int]]
        value conditional on param counts
    unk_token: str
        dummy command to signify an unseen command (e.g. "##UNK##")

    Returns
    -------
    Tuple:
        individual value probabilities,
        value conditional on param probabilities

    """
    value_counts_ls = copy.deepcopy(value_counts)
    param_value_counts_ls = copy.deepcopy(param_value_counts)

    values: List[str] = list(value_counts_ls.keys()) + [unk_token]
    for param in params:
        for value in values:
            if value in param_value_counts_ls[param] or value == unk_token:
                value_counts_ls[value] += 1
                param_value_counts_ls[param][value] += 1

    return value_counts_ls, param_value_counts_ls