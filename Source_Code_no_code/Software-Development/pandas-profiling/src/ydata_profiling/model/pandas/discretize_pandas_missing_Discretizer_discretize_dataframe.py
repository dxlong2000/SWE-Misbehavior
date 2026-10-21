from enum import Enum
from typing import List

import numpy as np
import pandas as pd


class DiscretizationType(Enum):
    UNIFORM = "uniform"
    QUANTILE = "quantile"


class Discretizer:
    """
    A class which enables the discretization of a pandas dataframe.
    Perform this action when you want to convert a continuous variable
    into a categorical variable.

    Attributes:

    method (DiscretizationType): this attribute controls how the buckets
    of your discretization are formed. A uniform discretization type forms
    the bins to be of equal width whereas a quantile discretization type
    forms the bins to be of equal size.

    n_bins (int): number of bins
    reset_index (bool): instruction to reset the index of
                        the dataframe after the discretization
    """

    def __init__(
        self, method: DiscretizationType, n_bins: int = 10, reset_index: bool = False
    ) -> None:
        self.discretization_type = method
        self.n_bins = n_bins
        self.reset_index = reset_index

    def discretize_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """This function takes a pandas DataFrame as input and discretizes the numerical columns in the DataFrame. It creates a copy of the input DataFrame and applies the discretization process to each numerical column. The discretized DataFrame is then returned.
        Input-Output Arguments
        :param self: Discretizer. An instance of the Discretizer class.
        :param dataframe: pd.DataFrame. The input pandas DataFrame.
        :return: pd.DataFrame. The discretized DataFrame.
        """

    def _discretize_column(self, column: pd.Series) -> pd.Series:
        if self.discretization_type == DiscretizationType.QUANTILE:
            return self._descritize_quantile(column)

        elif self.discretization_type == DiscretizationType.UNIFORM:
            return self._descritize_uniform(column)

    def _descritize_quantile(self, column: pd.Series) -> pd.Series:
        return pd.qcut(
            column, q=self.n_bins, labels=False, retbins=False, duplicates="drop"
        ).values

    def _descritize_uniform(self, column: pd.Series) -> pd.Series:
        return pd.cut(
            column, bins=self.n_bins, labels=False, retbins=True, duplicates="drop"
        )[0].values

    def _get_numerical_columns(self, dataframe: pd.DataFrame) -> List[str]:
        return dataframe.select_dtypes(include=np.number).columns.tolist()