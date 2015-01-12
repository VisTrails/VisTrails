import numpy as np
import unittest
from vistrails.tests.utils import execute, intercept_results

from vistrails.packages.sklearn.init import Digits, Iris, TrainTestSplit
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
                               TrainTestSplit, 'test_target') as (
                                   X_train, y_train, X_test, y_test):
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
        pass

    def test_regressor_training_predict(self):
        pass

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
