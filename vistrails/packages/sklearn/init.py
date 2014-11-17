from vistrails.core.modules.config import ModuleSettings
from vistrails.core.modules.vistrails_module import Module

import numpy as np
from sklearn import datasets
from sklearn.svm import LinearSVC as _LinearSVC


###############################################################################
# Example datasets

class Digits(Module):
    """Example dataset: digits.
    """
    _settings = ModuleSettings(namespace="datasets")
    _output_ports = [("data", "basic:List"),
                     ("target", "basic:List")]

    def compute(self):
        data = datasets.load_digits()
        self.set_output("data", data.data)
        self.set_output("target", data.target)


class Iris(Module):
    """Example dataset: iris.
    """
    _settings = ModuleSettings(namespace="datasets")
    _output_ports = [("data", "basic:List"),
                     ("target", "basic:List")]

    def compute(self):
        data = datasets.load_iris()
        self.set_output("data", data.data)
        self.set_output("target", data.target)


###############################################################################
# Base classes for classification

class Classifier(Module):
    """Base class for sklearn classifiers.
    """
    _settings = ModuleSettings(abstract=True)
    _output_ports = [("classifier", "Classifier")]


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


###############################################################################
# Classifiers

class LinearSVC(Classifier):
    """Learns a linear support vector machine model from training data.
    """
    _input_ports = [("train_data", "basic:List", {}),
                    ("train_classes", "basic:List", {}),
                    ("C", "basic:Float", {"defaults": [1]})]

    def compute(self):
        train_data = np.vstack(self.get_input("train_data"))
        train_classes = self.get_input("train_classes")

        C = self.get_input("C")
        clf = _LinearSVC(C=C).fit(train_data, train_classes)
        self.set_output("classifier", clf)


_modules = [Digits, Iris,
            Classifier, Predict,
            LinearSVC]
