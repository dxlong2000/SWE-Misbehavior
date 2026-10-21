#!/usr/bin/env python

import pandas as pd


def df2mat(data, return_labels=False):
    """This function transforms a single-level Pandas DataFrame into a Numpy array with binarized text columns. It uses the Pandas.DataFrame.get_dummies function to transform text columns into binary vectors.
    Input-Output Arguments
    :param data: Pandas DataFrame. The DataFrame that needs to be converted. It only works with single-level (not Multi-level indices).
    :param return_labels: Bool. Whether to return a list of column labels for the numpy array. Defaults to False.
    :return: Numpy array. A Numpy array where text columns are turned into binary vectors.
    :labels: List. A list of column labels for the numpy array. Only returned if return_labels is set to True.
    """