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
        probabilities = {'pick up tool': 0.602803738317757,
                         'hand over tool': 0.397196261682243}

        inference = self.bn.infer({})
        for intention, probability in inference.items():
            self.assertAlmostEqual(probability, probabilities[intention])

    def test_infer_unrelated_evidence(self):
        """
        Test inference with unrelated evidence of different types
        """
        probabilities = {'pick up tool': 0.602803738317757,
                         'hand over tool': 0.397196261682243}

        inference = self.bn.infer({'some context': 'is not important', 'another context': '',
                                  'unhashable context': {}, 'int context': 1, 'obj context': self.bn})
        for intention, probability in inference.items():
            self.assertAlmostEqual(probability, probabilities[intention])

    def test_infer_single_evidence(self):
        """
        Test inference with single evidence context present
        """
        probabilities = {'pick up tool': 0.7821782178217822,
                         'hand over tool': 0.21782178217821785}

        inference = self.bn.infer(
            {'speech commands': 'pickup', 'unhashable context': {}})
        for intention, probability in inference.items():
            self.assertAlmostEqual(probability, probabilities[intention])

    def test_infer_multiple_evidence(self):
        """
        Test inference with multiple evidence context present
        """
        probabilities = {'hand over tool': 0.3797468354430379,
                         'pick up tool': 0.620253164556962}

        inference = self.bn.infer(
            {'speech commands': 'pickup', 'human holding object': False, 'human activity': 'idle', 'unhashable context': {}})
        for intention, probability in inference.items():
            self.assertAlmostEqual(probability, probabilities[intention])

    def test_infer_combined_evidence(self):
        """
        Test inference for the combined case
        """
        probabilities = {'hand over tool': 0.26229508196721313,
                         'pick up tool': 0.7377049180327869}

        inference = self.bn.infer(
            {'speech commands': 'pickup', 'human holding object': True, 'human activity': 'idle', 'unhashable context': {}})
        for intention, probability in inference.items():
            self.assertAlmostEqual(probability, probabilities[intention])

    def test_infer_overlapping_combined_evidence(self):
        """
        Test inference for combined case if two combinations are overlapping - not implemented yet!
        """
        # probabilities = {'hand over tool': 0.26229508196721313,
        #                  'pick up tool': 0.7377049180327869}

        # inference = self.bn.infer(
        #     {'speech commands': 'pickup', 'human holding object': True, 'human activity': 'idle', 'unhashable context': {}})
        # print(inference)
        # for intention, probability in inference.items():
        #     self.assertAlmostEqual(probability, probabilities[intention])
        pass

    def test_infer_invalid_evidence(self):
        """
        Test inference
        """
        probabilities = {'pick up tool': 0.7821782178217822,
                         'hand over tool': 0.21782178217821785}

        with self.assertRaises(ValueError):
            self.bn.infer(
                {'speech commands': 'ERROR', 'unhashable context': {}})


if __name__ == '__main__':
    unittest.main()
