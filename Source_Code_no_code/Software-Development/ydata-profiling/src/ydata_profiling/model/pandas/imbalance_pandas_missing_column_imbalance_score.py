from typing import Union

import pandas as pd
from numpy import log2
from scipy.stats import entropy


def column_imbalance_score(
    value_counts: pd.Series, n_classes: int
) -> Union[float, int]:
    """This function calculates the class balance score for categorical and boolean variables using entropy to calculate a bounded score between 0 and 1. A perfectly uniform distribution would return a score of 0, and a perfectly imbalanced distribution would return a score of 1.
    Input-Output Arguments
    :param value_counts: pd.Series. Frequency of each category.
    :param n_classes: int. Number of classes.
    :return: Union[float, int]. Float or integer bounded between 0 and 1 inclusively.
    """