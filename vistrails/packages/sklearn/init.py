###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice,
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the New York University nor the names of its
##    contributors may be used to endorse or promote products derived from
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

from __future__ import division

from vistrails.core.modules.config import ModuleSettings
from vistrails.core.modules.vistrails_module import Module

import numpy as np
from sklearn.base import ClassifierMixin
from sklearn import datasets
from sklearn.cross_validation import train_test_split, cross_val_score
from sklearn.metrics import SCORERS, roc_curve
from sklearn.grid_search import GridSearchCV as _GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.utils.testing import all_estimators


def try_convert(input_string):
    if not isinstance(input_string, basestring):
        # already converted
        return input_string
    if input_string.isdigit():
        return int(input_string)
    try:
        return float(input_string)
    except ValueError:
        return input_string

# backport of odd estimators that we don't want to include
dont_test = ['SparseCoder', 'EllipticEnvelope', 'DictVectorizer',
             'LabelBinarizer', 'LabelEncoder', 'MultiLabelBinarizer',
             'TfidfTransformer', 'IsotonicRegression', 'OneHotEncoder',
             'RandomTreesEmbedding', 'FeatureHasher', 'DummyClassifier',
             'DummyRegressor', 'TruncatedSVD', 'PolynomialFeatures']


###############################################################################
# Example datasets

class Digits(Module):
    """Example dataset: digits.
    """
    _settings = ModuleSettings(namespace="datasets")
    _output_ports = [("data", "basic:List", {'shape': 'circle'}),
                     ("target", "basic:List", {'shape': 'circle'})]

    def compute(self):
        data = datasets.load_digits()
        self.set_output("data", data.data)
        self.set_output("target", data.target)


class Iris(Module):
    """Example dataset: iris.
    """
    _settings = ModuleSettings(namespace="datasets")
    _output_ports = [("data", "basic:List", {'shape': 'circle'}),
                     ("target", "basic:List", {'shape': 'circle'})]

    def compute(self):
        data = datasets.load_iris()
        self.set_output("data", data.data)
        self.set_output("target", data.target)


###############################################################################
# Base classes

class Estimator(Module):
    """Base class for all sklearn estimators.
    """
    _settings = ModuleSettings(abstract=True)
    _output_ports = [("model", "Estimator", {'shape': 'diamond'})]


class SupervisedEstimator(Estimator):
    """Base class for all sklearn classifier modules."""
    _settings = ModuleSettings(abstract=True)

    def compute(self):
        # get parameters, try to convert strings to float / int
        params = dict([(p, try_convert(self.get_input(p))) for p in self.inputPorts
                       if p not in ["training_data", "training_target"]])
        clf = self._estimator_class(**params)
        if "training_data" in self.inputPorts:
            training_data = np.vstack(self.get_input("training_data"))
            training_target = self.get_input("training_target")
            clf.fit(training_data, training_target)
        self.set_output("model", clf)


class UnsupervisedEstimator(Estimator):
    """Base class for all sklearn transformer modules."""
    _settings = ModuleSettings(abstract=True)

    def compute(self):
        params = dict([(p, try_convert(self.get_input(p))) for p in self.inputPorts
                       if p not in ["training_data", "training_target"]])
        trans = self._estimator_class(**params)
        if "training_data" in self.inputPorts:
            training_data = np.vstack(self.get_input("training_data"))
            trans.fit(training_data)
        self.set_output("model", trans)


class Predict(Module):
    """Apply a learned scikit-learn classifier model to test data.
    """
    # TODO : data depth=1
    _input_ports = [("model", "Estimator", {'shape': 'diamond'}),
                    ("data", "basic:List", {'shape': 'circle'})]
    _output_ports = [("prediction", "basic:List", {'shape': 'circle'}),
                     ("decision_function", "basic:List")]

    def compute(self):
        clf = self.get_input("model")
        data = self.get_input("data")
        predictions = clf.predict(data)
        decision_function = clf.decision_function(data)
        self.set_output("prediction", predictions)
        self.set_output("decision_function", decision_function)


class Transform(Module):
    """Apply a learned scikit-learn transformer to test data.
    """
    _input_ports = [("model", "Estimator", {'shape': 'diamond'}),
                    ("data", "basic:List", {'shape': 'circle'})]
    _output_ports = [("transformed_data", "basic:List", {'shape': 'circle'})]

    def compute(self):
        trans = self.get_input("model")
        data = self.get_input("data")
        transformed_data = trans.transform(data)
        self.set_output("transformed_data", transformed_data)


###############################################################################
# Cross-validation


class TrainTestSplit(Module):
    """Split data into training and testing randomly."""
    _settings = ModuleSettings(namespace="cross-validation")
    _input_ports = [("data", "basic:List", {'shape': 'circle'}),
                    ("target", "basic:List", {'shape': 'circle'}),
                    ("test_size", "basic:Float", {"defaults": [.25]})]
    _output_ports = [("training_data", "basic:List", {'shape': 'circle'}),
                     ("training_target", "basic:List", {'shape': 'circle'}),
                     ("test_data", "basic:List", {'shape': 'circle'}),
                     ("test_target", "basic:List", {'shape': 'circle'})]

    def compute(self):
        X_train, X_test, y_train, y_test = \
            train_test_split(self.get_input("data"), self.get_input("target"),
                             test_size=try_convert(self.get_input("test_size")))
        self.set_output("training_data", X_train)
        self.set_output("training_target", y_train)
        self.set_output("test_data", X_test)
        self.set_output("test_target", y_test)


class CrossValScore(Module):
    """Split data into training and testing randomly."""
    _settings = ModuleSettings(namespace="cross-validation")
    _input_ports = [("model", "Estimator", {'shape': 'diamond'}),
                    ("data", "basic:List", {'shape': 'circle'}),
                    ("target", "basic:List", {'shape': 'circle'}),
                    ("metric", "basic:String", {"defaults": ["accuracy"]}),
                    ("folds", "basic:Integer", {"defaults": ["3"]})]
    _output_ports = [("scores", "basic:List")]

    def compute(self):
        model = self.get_input("model")
        data = self.get_input("data")
        target = self.get_input("target")
        metric = self.get_input("metric")
        folds = self.get_input("folds")
        scores = cross_val_score(model, data, target, scoring=metric, cv=folds)
        self.set_output("scores", scores)

###############################################################################
# Meta Estimators


class GridSearchCV(Estimator):
    """Perform cross-validated grid-search over a parameter grid."""
    _input_ports = [("model", "Estimator", {'shape': 'diamond'}),
                    ("parameters", "basic:Dictionary"),
                    ("data", "basic:List", {'shape': 'circle'}),
                    ("target", "basic:List", {'shape': 'circle'}),
                    ("metric", "basic:String", {"defaults": ["accuracy"]}),
                    ("folds", "basic:Integer", {"defaults": ["3"]})]
    _output_ports = [("scores", "basic:List"), ("model", "Estimator", {'shape': 'diamond'}),
                     ("best_parameters", "basic:Dictionary"),
                     ("best_score", "basic:Float")]

    def compute(self):
        base_model = self.get_input("model")
        grid = _GridSearchCV(base_model,
                             param_grid=self.get_input("parameters"),
                             cv=self.get_input("folds"),
                             scoring=self.get_input("metric"))
        if "data" in self.inputPorts:
            data = np.vstack(self.get_input("data"))
            target = self.get_input("target")
            grid.fit(data, target)
            self.set_output("scores", grid.grid_scores_)
            self.set_output("best_parameters", grid.best_params_)
            self.set_output("best_score", grid.best_score_)
        self.set_output("model", grid)


class Pipeline(Estimator):
    """Chain estimators to form a pipeline."""
    _input_ports = [("training_data", "basic:List", {'shape': 'circle'}),
                    ("training_target", "basic:List", {'shape': 'circle'}),("model1", "Estimator", {'shape': 'diamond'}),
                    ("model2", "Estimator", {'optional': True, 'shape': 'diamond'}),
                    ("model3", "Estimator", {'optional': True, 'shape': 'diamond'}),
                    ("model4", "Estimator", {'optional': True, 'shape': 'diamond'})]

    def compute(self):
        models = ["model%d" % d for d in range(1, 5)]
        steps = [self.get_input(model) for model in models if model in self.inputPorts]
        pipeline = make_pipeline(*steps)
        if "training_data" in self.inputPorts:
            training_data = np.vstack(self.get_input("training_data"))
            training_target = self.get_input("training_target")
            pipeline.fit(training_data, training_target)
        self.set_output("model", pipeline)

###############################################################################
# Metrics


class Score(Module):
    """Compute a model performance metric."""
    _settings = ModuleSettings()
    _input_ports = [("model", "Estimator", {'shape': 'diamond'}),
                    ("data", "basic:List", {'shape': 'circle'}),
                    ("target", "basic:List", {'shape': 'circle'}),
                    ("metric", "basic:String", {"defaults": ["accuracy"]})]
    _output_ports = [("score", "basic:Float")]

    def compute(self):
        scorer = SCORERS[self.get_input("metric")]
        score = scorer(self.get_input("model"), self.get_input("data"), self.get_input("target"))
        self.set_output("score", score)


class ROCCurve(Module):
    """Compute a ROC curve."""
    _settings = ModuleSettings(namespace="metrics")
    _input_ports = [("model", "Estimator", {'shape': 'diamond'}),
                    ("data", "basic:List", {'shape': 'circle'}),
                    ("target", "basic:List", {'shape': 'circle'})]
    _output_ports = [("fpr", "basic:List"),
                     ("tpr", "basic:List")]

    def compute(self):
        model = self.get_input("model")
        data = self.get_input("data")
        if hasattr(model, "decision_function"):
            dec = model.decision_function(data)
        else:
            dec = model.predict_proba(data)[:, 1]
        fpr, tpr, _ = roc_curve(self.get_input("target"), dec)
        self.set_output("fpr", fpr)
        self.set_output("tpr", tpr)


###############################################################################<F2>
# Classifiers and Regressors

def make_module(name, Estimator, namespace, supervised=False, Base=None):
    input_ports = [("training_data", "basic:List", {'shape': 'circle'})]
    if supervised:
        input_ports.append(("training_target", "basic:List", {'shape': 'circle'}))
    est = Estimator()
    input_ports.extend([(param, "basic:String", {'optional': True}) for param
                        in est.get_params()])
    _settings = ModuleSettings(namespace=namespace)
    if Base is None:
        if supervised:
            Base = SupervisedEstimator
        else:
            Base = UnsupervisedEstimator
    new_class = type(name, (Base,),
                     {'_input_ports': input_ports, '_settings': _settings,
                      '_estimator_class': Estimator, '__doc__':
                      Estimator.__doc__})
    return new_class


def discover_supervised():
    classifiers = all_estimators(type_filter="classifier")
    regressors = all_estimators(type_filter="regressor")
    classes = []
    for name, Est in classifiers + regressors:
        if issubclass(Est, ClassifierMixin):
            namespace = "classifiers"
        else:
            namespace = "regressors"
        classes.append(make_module(name, Est, namespace, supervised=True))
    return classes


###############################################################################<F2>
# Clustering

def discover_clustering():
    return [make_module(name, Est, "clustering") for (name, Est) in
            all_estimators(type_filter="cluster")]


###############################################################################
# Transformers

def discover_unsupervised_transformers():
    # also: random tree embedding
    transformers = all_estimators(type_filter="transformer")
    classes = []
    for name, Est in transformers:
        if name in dont_test:
            continue
        module = Est.__module__.split(".")[1]
        if module not in ['decomposition', 'kernel_approximation',
                          'neural_network', 'preprocessing', 'random_projection']:
            # the manifold module does not really provide transformers and is
            # handled elsewhere (there is usually no transform method).
            continue
        classes.append(make_module(name, Est, namespace=module))
    return classes


def discover_feature_selection():
    # also: random tree embedding
    transformers = all_estimators(type_filter="transformer")
    classes = []
    for name, Est in transformers:
        if name in dont_test:
            continue
        module = Est.__module__.split(".")[1]
        if module != "feature_selection" or name == "GenericUnivariateSelect":
            continue
        classes.append(make_module(name, Est, namespace=module, supervised=True))
    return classes


###############################################################################
# Manifold learning
# unfortunately this has a sightly different interface due to the fact that
# most manifold algorithms can't generalize to new data.
class ManifoldLearner(Module):
    """Base class for all sklearn manifold modules.
    """
    _settings = ModuleSettings(abstract=True)
    _output_ports = [("transformed_data", "basic:List", {'shape': 'circle'})]

    def compute(self):
        params = dict([(p, try_convert(self.get_input(p))) for p in self.inputPorts
                       if p not in ["training_data"]])
        trans = self._estimator_class(**params)
        training_data = np.vstack(self.get_input("training_data"))
        transformed_data = trans.fit_transform(training_data)
        self.set_output("transformed_data", transformed_data)


def discover_manifold_learning():
    # also: random tree embedding
    transformers = all_estimators()
    classes = []
    for name, Est in transformers:
        if name in dont_test:
            continue
        module = Est.__module__.split(".")[1]
        if module != "manifold":
            continue
        classes.append(make_module(name, Est, namespace=module, Base=ManifoldLearner))
    return classes


_modules = [Digits, Iris, Estimator, SupervisedEstimator,
            UnsupervisedEstimator, ManifoldLearner, Predict, Transform,
            TrainTestSplit, Score, ROCCurve, CrossValScore, GridSearchCV,
            Pipeline]
_modules.extend(discover_supervised())
_modules.extend(discover_clustering())
_modules.extend(discover_unsupervised_transformers())
_modules.extend(discover_feature_selection())
_modules.extend(discover_manifold_learning())
