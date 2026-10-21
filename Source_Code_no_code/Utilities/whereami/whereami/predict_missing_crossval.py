import json
from collections import Counter

from access_points import get_scanner

from whereami.get_data import get_train_data, get_external_sample
from whereami.get_data import sample
from whereami.pipeline import get_model
from whereami.get_data import aps_to_dict
from whereami.compat import cross_val_score


def predict_proba(input_path=None, model_path=None, device=""):
    lp = get_model(model_path)
    data_sample = sample(device) if input_path is None else get_external_sample(input_path)
    print(json.dumps(dict(zip(lp.classes_, lp.predict_proba(data_sample)[0]))))


def predict(input_path=None, model_path=None, device=""):
    lp = get_model(model_path)
    data_sample = sample(device) if input_path is None else get_external_sample(input_path)
    return lp.predict(data_sample)[0]


def crossval(clf=None, X=None, y=None, folds=10, n=5, path=None):
    """Perform cross-validation on a given classifier using the specified data. First, if the input data X or labels y are not provided, the function will retrieve them from a given path. Then, if the number of samples in X is less than the number of folds, it will raise a ValueError 'There are not enough samples ({length of X}). Need at least {folds number}.'.
    Next, if no classifier model is provided, it will obtain one from the given path.
    It then prints "KFold folds={folds number}, running {n} times". The function then performs cross-validation by iterating n times. In each iteration, it  evaluate the performance of the classifier on each fold, and calculates the average accuracy. After each iteration, it prints "{iteration number (starting from 1)}/{n}: {average accuracy of the iteration}". Finally, after all iterations are complete, it prints "-------- total --------" and then prints the total average accuracy obtained from all iterations and returns this value.
    Input-Output Arguments
    :param clf: Classifier. The classifier to be used for cross-validation. If not provided, it retrieves the classifier from the specified path.
    :param X: Array-like. The input data features. If not provided, it retrieves the training data features from the specified path.
    :param y: Array-like. The target variable. If not provided, it retrieves the training data target variable from the specified path.
    :param folds: Integer. The number of folds to be used in cross-validation. Defaults to 10.
    :param n: Integer. The number of times to run cross-validation. Defaults to 5.
    :param path: String. The path to the training data. If not provided, the data is assumed to be already provided in X and y.
    :return: Float. The average score obtained from cross-validation.
    """


def locations(path=None):
    _, y = get_train_data(path)
    if len(y) == 0:  # pragma: no cover
        msg = "No location samples available. First learn a location, e.g. with `whereami learn -l kitchen`."
        print(msg)
    else:
        occurrences = Counter(y)
        for key, value in occurrences.items():
            print("{}: {}".format(key, value))


class Predicter():
    def __init__(self, model=None, device=""):
        self.model = model
        self.device = device
        self.clf = get_model(model)
        self.wifi_scanner = get_scanner(device)
        self.predicted_value = None

    def predict(self):
        aps = self.wifi_scanner.get_access_points()
        self.predicted_value = self.clf.predict(aps_to_dict(aps))[0]
        return self.predicted_value

    def refresh(self):
        self.clf = get_model(self.model)
        self.wifi_scanner = get_scanner(self.device)