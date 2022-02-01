'''
Tests for adding intention variables
'''

# System imports
from copy import deepcopy
import unittest

# 3rd party imports

# local imports
from tests import N
from CoBaIR.bayes_net import BayesNet, default_to_regular, load_config
# end file header
__author__ = 'Adrian Lubitz'


class TestCreateBayesNet(unittest.TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.bn = BayesNet()
        self.bn.load('small_example.yml')

    def test_infer_no_evidence(self):
        """
        Test inference without evidence
        """
        probabilities = {'pick up tool': 0.5873786407766991,
                         'hand over tool': 0.412621359223301}

        inference = self.bn.infer({})
        for intention, probability in inference.items():
            self.assertAlmostEqual(probability, probabilities[intention])

    def test_infer_unrelated_evidence(self):
        """
        Test inference with unrelated evidence of different types
        """
        probabilities = {'pick up tool': 0.5873786407766991,
                         'hand over tool': 0.412621359223301}

        inference = self.bn.infer({'some context': 'is not important', 'another context': '',
                                  'unhashable context': {}, 'int context': 1, 'obj context': self.bn})
        for intention, probability in inference.items():
            self.assertAlmostEqual(probability, probabilities[intention])

    def test_infer_evidence(self):
        """
        Test inference
        """
        probabilities = {'pick up tool': 0.7490494296577948,
                         'hand over tool': 0.25095057034220536}

        inference = self.bn.infer(
            {'speech commands': 'pickup', 'unhashable context': {}})
        for intention, probability in inference.items():
            self.assertAlmostEqual(probability, probabilities[intention])

    def test_infer_invalid_evidence(self):
        """
        Test inference
        """
        probabilities = {'pick up tool': 0.7490494296577948,
                         'hand over tool': 0.25095057034220536}

        with self.assertRaises(ValueError):
            self.bn.infer(
                {'speech commands': 'ERROR', 'unhashable context': {}})


if __name__ == '__main__':
    unittest.main()
