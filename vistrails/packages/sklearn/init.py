from vistrails.core.modules.config import ModuleSettings
from vistrails.core.modules.vistrails_module import Module

import numpy as np
from sklearn.svm import LinearSVC as _LinearSVC


class Predict(Module):
    """Apply a learned scikit-learn classifier model to test data.
    """
    # TODO : data depth=1
    _input_ports = [("classifier", "Classifier"),
                    ("data", "basic:List")]
    _output_ports = [("prediction", "basic:List"),
                     ("decision_function", "basic:List")]

    def compute(self):
        clf = self.get_input("classifier")
        data = self.get_input("data")
        predictions = clf.predict(data)
        decision_function = clf.decision_function(data)
        self.set_output("prediction", predictions)
        self.set_output("decision_function", decision_function)


class Classifier(Module):
    """Base class for sklearn classifiers.
    """
    _settings = ModuleSettings(abstract=True)
    _output_ports = [("classifier", "Classifier")]


class LinearSVC(Classifier):
    """LinearSVC learns a linear support vector machine model from training data."""
    _input_ports = [("X_train", "basic:List", {}),
                    ("y_train", "basic:List", {}),
                    ("C", "basic:Float", {"defaults": [1]})]

    def compute(self):
        X_train = np.vstack(self.get_input("X_train"))
        y_train = self.get_input("y_train")

        C = self.get_input("C")
        est = _LinearSVC(C=C).fit(X_train, y_train)
        self.set_output("classifier", est)


_modules = [Classifier, Predict,
            LinearSVC]
