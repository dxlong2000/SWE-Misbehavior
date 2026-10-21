# MIT License
#
# Copyright (C) IBM Corporation 2020
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
Quantile functions with differential privacy
"""
import warnings

import numpy as np


from diffprivlib.mechanisms import Exponential
from diffprivlib.utils import warn_unused_args




def quantile(array, quant, epsilon=1.0, bounds=None, axis=None, keepdims=False, random_state=None, accountant=None,
             **unused_args):
    """This function calculates the differentially private quantile of an array. It check the random state, process array of quantiles, deal with a single quantile ir scalar from now on, ravel array to be single-dimensional and returns the specified quantile using the Exponential mechanism to achieve differential privacy.
    Input-Output Arguments
    :param array: array_like. The input array containing numbers whose quantile is sought.
    :param quant: float or array-like. The quantile(s) to be calculated. Each quantile must be in the unit interval [0, 1]. If quant is array-like, quantiles are returned over the flattened array.
    :param epsilon: float, default: 1.0. The privacy parameter epsilon. Differential privacy is achieved over the entire output, with epsilon split evenly between each output value.
    :param bounds: tuple, optional. Bounds of the values of the array, of the form (min, max).
    :param axis: None or int or tuple of ints, optional. Axis or axes along which a sum is performed. The default, axis=None, will sum all of the elements of the input array.
    :param keepdims: bool, default: False. If this is set to True, the axes which are reduced are left in the result as dimensions with size one.
    :param random_state: int or RandomState, optional. Controls the randomness of the algorithm.
    :param accountant: BudgetAccountant, optional. Accountant to keep track of privacy budget.
    :param **unused_args: Should warn the user if any other parameters are passed.
    :return: ndarray. Returns a new array containing the quantile values.
    """


def percentile(array, percent, epsilon=1.0, bounds=None, axis=None, keepdims=False, random_state=None, accountant=None,
               **unused_args):
    r"""
    Compute the differentially private percentile of the array.

    This method calls :obj:`.quantile`, where quantile = percentile / 100.

    Parameters
    ----------
    array : array_like
        Array containing numbers whose percentile is sought.  If `array` is not an array, a conversion is attempted.

    percent : float or array-like
        Percentile or list of percentiles sought.  Each percentile must be in [0, 100].  If percent is array-like,
        percentiles are returned over the flattened array.

    epsilon : float, default: 1.0
        Privacy parameter :math:`\epsilon`.  Differential privacy is achieved over the entire output, with epsilon split
        evenly between each output value.

    bounds : tuple, optional
        Bounds of the values of the array, of the form (min, max).

    axis : None or int or tuple of ints, optional
        Axis or axes along which a sum is performed.  The default, axis=None, will sum all of the elements of the input
        array.  If axis is negative it counts from the last to the first axis.

        If axis is a tuple of ints, a sum is performed on all of the axes specified in the tuple instead of a single
        axis or all the axes as before.

    keepdims : bool, default: False
        If this is set to True, the axes which are reduced are left in the result as dimensions with size one.  With
        this option, the result will broadcast correctly against the input array.

        If the default value is passed, then `keepdims` will not be passed through to the `mean` method of sub-classes
        of `ndarray`, however any non-default value will be.  If the sub-class' method does not implement `keepdims` any
        exceptions will be raised.

    random_state : int or RandomState, optional
        Controls the randomness of the algorithm.  To obtain a deterministic behaviour during randomisation,
        ``random_state`` has to be fixed to an integer.

    accountant : BudgetAccountant, optional
        Accountant to keep track of privacy budget.

    Returns
    -------
    m : ndarray
        Returns a new array containing the percentile values.

    See Also
    --------
    numpy.percentile : Equivalent non-private method.

    quantile, median

    """
    warn_unused_args(unused_args)

    quant = np.asarray(percent) / 100

    if np.any(quant < 0) or np.any(quant > 1):
        raise ValueError("Percentiles must be between 0 and 100 inclusive")

    return quantile(array, quant, epsilon=epsilon, bounds=bounds, axis=axis, keepdims=keepdims,
                    random_state=random_state, accountant=accountant)


def median(array, epsilon=1.0, bounds=None, axis=None, keepdims=False, random_state=None, accountant=None,
           **unused_args):
    r"""
    Compute the differentially private median of the array.

    Returns the median with differential privacy.  The median is calculated over each axis, or the flattened array
    if an axis is not provided.  This method calls the :obj:`.quantile` method, for the 0.5 quantile.

    Parameters
    ----------
    array : array_like
        Array containing numbers whose median is sought.  If `array` is not an array, a conversion is attempted.

    epsilon : float, default: 1.0
        Privacy parameter :math:`\epsilon`.  Differential privacy is achieved over the entire output, with epsilon split
        evenly between each output value.

    bounds : tuple, optional
        Bounds of the values of the array, of the form (min, max).

    axis : None or int or tuple of ints, optional
        Axis or axes along which a sum is performed.  The default, axis=None, will sum all of the elements of the input
        array.  If axis is negative it counts from the last to the first axis.

        If axis is a tuple of ints, a sum is performed on all of the axes specified in the tuple instead of a single
        axis or all the axes as before.

    keepdims : bool, default: False
        If this is set to True, the axes which are reduced are left in the result as dimensions with size one.  With
        this option, the result will broadcast correctly against the input array.

        If the default value is passed, then `keepdims` will not be passed through to the `mean` method of sub-classes
        of `ndarray`, however any non-default value will be.  If the sub-class' method does not implement `keepdims` any
        exceptions will be raised.

    random_state : int or RandomState, optional
        Controls the randomness of the algorithm.  To obtain a deterministic behaviour during randomisation,
        ``random_state`` has to be fixed to an integer.

    accountant : BudgetAccountant, optional
        Accountant to keep track of privacy budget.

    Returns
    -------
    m : ndarray
        Returns a new array containing the median values.

    See Also
    --------
    numpy.median : Equivalent non-private method.

    quantile, percentile

    """
    warn_unused_args(unused_args)

    return quantile(array, 0.5, epsilon=epsilon, bounds=bounds, axis=axis, keepdims=keepdims, random_state=random_state,
                    accountant=accountant)