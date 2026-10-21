# MIT License
#
# Copyright (C) IBM Corporation 2019
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
Gaussian Naive Bayes classifier satisfying differential privacy
"""
import warnings

import numpy as np
import sklearn.naive_bayes as sk_nb
from sklearn.utils.multiclass import _check_partial_fit_first_call

from diffprivlib.accountant import BudgetAccountant
from diffprivlib.mechanisms import LaplaceBoundedDomain, GeometricTruncated, LaplaceTruncated
from diffprivlib.utils import PrivacyLeakWarning, warn_unused_args, check_random_state
from diffprivlib.validation import DiffprivlibMixin


class GaussianNB(sk_nb.GaussianNB, DiffprivlibMixin):
    r"""Gaussian Naive Bayes (GaussianNB) with differential privacy

    Inherits the :class:`sklearn.naive_bayes.GaussianNB` class from Scikit Learn and adds noise to satisfy differential
    privacy to the learned means and variances.  Adapted from the work presented in [VSB13]_.

    Parameters
    ----------
    epsilon : float, default: 1.0
        Privacy parameter :math:`\epsilon` for the model.

    bounds :  tuple, optional
        Bounds of the data, provided as a tuple of the form (min, max).  `min` and `max` can either be scalars, covering
        the min/max of the entire data, or vectors with one entry per feature.  If not provided, the bounds are computed
        on the data when ``.fit()`` is first called, resulting in a :class:`.PrivacyLeakWarning`.

    priors : array-like, shape (n_classes,)
        Prior probabilities of the classes.  If specified the priors are not adjusted according to the data.

    var_smoothing : float, default: 1e-9
        Portion of the largest variance of all features that is added to variances for calculation stability.

    random_state : int or RandomState, optional
        Controls the randomness of the model.  To obtain a deterministic behaviour during randomisation,
        ``random_state`` has to be fixed to an integer.

    accountant : BudgetAccountant, optional
        Accountant to keep track of privacy budget.

    Attributes
    ----------
    class_prior_ : array, shape (n_classes,)
        probability of each class.

    class_count_ : array, shape (n_classes,)
        number of training samples observed in each class.

    theta_ : array, shape (n_classes, n_features)
        mean of each feature per class

    var_ : array, shape (n_classes, n_features)
        variance of each feature per class

    epsilon_ : float
        absolute additive value to variances (unrelated to ``epsilon`` parameter for differential privacy)

    References
    ----------
    .. [VSB13] Vaidya, Jaideep, Basit Shafiq, Anirban Basu, and Yuan Hong. "Differentially private naive bayes
        classification." In 2013 IEEE/WIC/ACM International Joint Conferences on Web Intelligence (WI) and Intelligent
        Agent Technologies (IAT), vol. 1, pp. 571-576. IEEE, 2013.

    """

    def __init__(self, *, epsilon=1.0, bounds=None, priors=None, var_smoothing=1e-9, random_state=None,
                 accountant=None):
        super().__init__(priors=priors, var_smoothing=var_smoothing)

        self.epsilon = epsilon
        self.bounds = bounds
        self.random_state = random_state
        self.accountant = BudgetAccountant.load_default(accountant)

    def _partial_fit(self, X, y, classes=None, _refit=False, sample_weight=None):
        self.accountant.check(self.epsilon, 0)

        if sample_weight is not None:
            warn_unused_args("sample_weight")

        random_state = check_random_state(self.random_state)

        X, y = self._validate_data(X, y)

        if self.bounds is None:
            warnings.warn("Bounds have not been specified and will be calculated on the data provided. This will "
                          "result in additional privacy leakage. To ensure differential privacy and no additional "
                          "privacy leakage, specify bounds for each dimension.", PrivacyLeakWarning)
            self.bounds = (np.min(X, axis=0), np.max(X, axis=0))

        self.bounds = self._check_bounds(self.bounds, shape=X.shape[1])
        X = self._clip_to_bounds(X, self.bounds)

        self.epsilon_ = self.var_smoothing

        if _refit:
            self.classes_ = None

        if _check_partial_fit_first_call(self, classes):
            n_features = X.shape[1]
            n_classes = len(self.classes_)
            self.theta_ = np.zeros((n_classes, n_features))
            self.var_ = np.zeros((n_classes, n_features))

            self.class_count_ = np.zeros(n_classes, dtype=np.float64)

            if self.priors is not None:
                priors = np.asarray(self.priors)

                if len(priors) != n_classes:
                    raise ValueError("Number of priors must match number of classes.")
                if not np.isclose(priors.sum(), 1.0):
                    raise ValueError("The sum of the priors should be 1.")
                if (priors < 0).any():
                    raise ValueError("Priors must be non-negative.")
                self.class_prior_ = priors
            else:
                # Initialize the priors to zeros for each class
                self.class_prior_ = np.zeros(len(self.classes_), dtype=np.float64)
        else:
            if X.shape[1] != self.theta_.shape[1]:
                raise ValueError(f"Number of features {X.shape[1]} does not match previous "
                                 f"data {self.theta_.shape[1]}.")
            # Put epsilon back in each time
            self.var_[:, :] -= self.epsilon_

        classes = self.classes_

        unique_y = np.unique(y)
        unique_y_in_classes = np.in1d(unique_y, classes)

        if not np.all(unique_y_in_classes):
            raise ValueError(f"The target label(s) {unique_y[~unique_y_in_classes]} in y do not exist in the initial "
                             f"classes {classes}")

        noisy_class_counts = self._noisy_class_counts(y, random_state=random_state)

        for _i, y_i in enumerate(unique_y):
            i = classes.searchsorted(y_i)
            X_i = X[y == y_i, :]

            n_i = noisy_class_counts[_i]

            new_theta, new_var = self._update_mean_variance(self.class_count_[i], self.theta_[i, :], self.var_[i, :],
                                                            X_i, random_state=random_state, n_noisy=n_i)

            self.theta_[i, :] = new_theta
            self.var_[i, :] = new_var
            self.class_count_[i] += n_i

        self.var_[:, :] += self.epsilon_

        # Update if only no priors is provided
        if self.priors is None:
            # Empirical prior, with sample_weight taken into account
            self.class_prior_ = self.class_count_ / self.class_count_.sum()

        self.accountant.spend(self.epsilon, 0)

        return self

    def _update_mean_variance(self, n_past, mu, var, X, random_state, sample_weight=None, n_noisy=None):
        """This function computes the online update of the Gaussian mean and variance. It takes the starting sample count, mean, and variance, and a new set of points X, and returns the updated mean and variance. Each dimension in X is treated as independent, so it calculates the variance, not the covariance. It can update a scalar mean and variance or a vector mean and variance to simultaneously update multiple independent Gaussians.
        Input-Output Arguments
        :param self: GaussianNB. An instance of the GaussianNB class.
        :param n_past: int. The number of samples represented in the old mean and variance. If sample weights were given, this should contain the sum of sample weights represented in the old mean and variance.
        :param mu: array-like, shape (number of Gaussians,). The means for Gaussians in the original set.
        :param var: array-like, shape (number of Gaussians,). The variances for Gaussians in the original set.
        :param X: array-like, shape (n_samples, n_features). The new set of points to update the mean and variance with.
        :param random_state: RandomState. Controls the randomness of the model.
        :param sample_weight: ignored. Ignored in diffprivlib.
        :param n_noisy: int, optional. Noisy count of the given class, satisfying differential privacy.
        :return: (total_mu) array-like, shape (number of Gaussians,) and (total_var) array-like, shape (number of Gaussians,). The updated mean for each Gaussian over the combined set and the updated variance for each Gaussian over the combined set.
        """

    def _noisy_class_counts(self, y, random_state):
        unique_y = np.unique(y)
        n_total = y.shape[0]

        # Use 1/3 of total epsilon budget for getting noisy class counts
        mech = GeometricTruncated(epsilon=self.epsilon / 3, sensitivity=1, lower=1, upper=n_total,
                                  random_state=random_state)
        noisy_counts = np.array([mech.randomise((y == y_i).sum()) for y_i in unique_y])

        argsort = np.argsort(noisy_counts)
        i = 0 if noisy_counts.sum() > n_total else len(unique_y) - 1

        while np.sum(noisy_counts) != n_total:
            _i = argsort[i]
            sgn = np.sign(n_total - noisy_counts.sum())
            noisy_counts[_i] = np.clip(noisy_counts[_i] + sgn, 1, n_total)

            i = (i - sgn) % len(unique_y)

        return noisy_counts

    @property
    def sigma_(self):
        """Variance of each feature per class."""
        # Todo: Consider removing when sklearn v1.0 is required
        return self.var_