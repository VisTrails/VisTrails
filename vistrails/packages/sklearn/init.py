from core.modules.vistrails_module import Module  # , ModuleError

import numpy as np
from sklearn.svm import LinearSVC as _LinearSVC


class SklearnClassifierPrediction(Module):
    """Apply a learned scikit-learn classifier model to test data."""
    _input_ports = [("classifier", "SklearnClassifier"),
                    ("data", "basic:List")]
    _output_ports = [("prediction", "basic:List"), ("decision_function",
                                                    "basic:List")]

    def compute(self):
        clf = self.get_input("classifier")
        X = self.get_input("data")
        y_pred = clf.predict(X)
        decision_function = clf.decision_function(X)
        self.set_output("prediction", y_pred)
        self.set_output("decision_function", decision_function)


class SklearnClassifier(Module):
    pass


class LinearSVC(SklearnClassifier):
    """LinearSVC learns a linear support vector machine model from training data."""
    _input_ports = [("X_train", "basic:List", {}),
                    ("y_train", "basic:List", {}),
                    ("C", "basic:Float", {'defaults': [1]})]

    _output_ports = [('classifier', "SklearnClassifier")]

    def compute(self):
        X_train = np.vstack(self.get_input("X_train"))
        y_train = self.get_input("y_train")

        C = self.get_input("C")
        est = _LinearSVC(C=C).fit(X_train, y_train)
        self.set_output("classifier", est)


def initialize(*args, **keywords):
    pass


_modules = [SklearnClassifier, SklearnClassifierPrediction,
            LinearSVC]
