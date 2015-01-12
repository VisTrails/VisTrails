import numpy as np
import unittest
from vistrails.tests.utils import execute, intercept_results

from vistrails.packages.sklearn.init import (Digits, Iris, TrainTestSplit,
                                             Predict, Score)
from vistrails.packages.sklearn import identifier


class TestSklearn(unittest.TestCase):
    def test_digits(self):
        # check that the digits dataset can be loaded
        with intercept_results(Digits, 'data', Digits, 'target') as (data, target):
            self.assertFalse(execute([
                ('datasets|Digits', identifier, [])
            ]))
        data = np.vstack(data)
        target = np.hstack(target)
        self.assertEqual(data.shape, (1797, 64))
        self.assertEqual(target.shape, (1797,))

    def test_iris(self):
        # check that the iris dataset can be loaded
        with intercept_results(Iris, 'data', Iris, 'target') as (data, target):
            self.assertFalse(execute([
                ('datasets|Iris', identifier, [])
            ]))
        data = np.vstack(data)
        target = np.hstack(target)
        self.assertEqual(data.shape, (150, 4))
        self.assertEqual(target.shape, (150,))

    def test_train_test_split(self):
        # check that we can split the iris dataset
        with intercept_results(TrainTestSplit, 'training_data', TrainTestSplit,
                               'training_target', TrainTestSplit, 'test_data',
                               TrainTestSplit, 'test_target') as results:
            X_train, y_train, X_test, y_test = results
            self.assertFalse(execute(
                [
                    ('datasets|Iris', identifier, []),
                    ('cross-validation|TrainTestSplit', identifier,
                     [('test_size', [('Integer', '50')])])
                ],
                [
                    (0, 'data', 1, 'data'),
                    (0, 'target', 1, 'target')
                ]
            ))
        X_train = np.vstack(X_train)
        X_test = np.vstack(X_test)
        y_train = np.hstack(y_train)
        y_test = np.hstack(y_test)
        self.assertEqual(X_train.shape, (100, 4))
        self.assertEqual(X_test.shape, (50, 4))
        self.assertEqual(y_train.shape, (100,))
        self.assertEqual(y_test.shape, (50,))

    def test_classifier_training_predict(self):
        with intercept_results(Predict, 'prediction', Predict,
                               'decision_function', TrainTestSplit, 'test_target',
                               Score, 'score') as results:
            y_pred, decision_function, y_test, score = results
            self.assertFalse(execute(
                [
                    ('datasets|Iris', identifier, []),
                    ('cross-validation|TrainTestSplit', identifier,
                     [('test_size', [('Integer', '50')])]),
                    ('classifiers|LinearSVC', identifier, []),
                    ('Predict', identifier, []),
                    ('Score', identifier, []),

                ],
                [
                    # train test split
                    (0, 'data', 1, 'data'),
                    (0, 'target', 1, 'target'),
                    # fit LinearSVC on training data
                    (1, 'training_data', 2, 'training_data'),
                    (1, 'training_target', 2, 'training_target'),
                    # predict on test data
                    (2, 'model', 3, 'model'),
                    (1, 'test_data', 3, 'data'),
                    # score test data
                    (2, 'model', 4, 'model'),
                    (1, 'test_data', 4, 'data'),
                    (1, 'test_target', 4, 'target')
                ]
            ))
        y_pred = np.hstack(y_pred)
        decision_function = np.vstack(decision_function)
        y_test = np.hstack(y_test)
        self.assertEqual(y_pred.shape, (50,))
        self.assertTrue(np.all(np.unique(y_pred) == np.array([0, 1, 2])))
        self.assertEqual(decision_function.shape, (50, 3))
        # some accuracy
        self.assertTrue(np.mean(y_test == y_pred) > .5)
        self.assertEqual(np.mean(y_test == y_pred), score)

    def test_transformer_unsupervised_transform(self):
        pass

    def test_transformer_supervised_transform(self):
        pass

    def test_manifold_learning(self):
        pass

    def test_cross_val_score(self):
        pass

    def test_gridsearchcv(self):
        pass

    def test_pipeline(self):
        pass

    def test_scoring(self):
        pass
