'''
Tests for adding context variables
'''

# System imports
import unittest
from collections import defaultdict

# 3rd party imports

# local imports
from tests import N
from bayesian_intention_recognition.bayes_net import BayesNet, load_config
# end file header
__author__ = 'Adrian Lubitz'

# TODO: add more negative cases


class TestAddContext(unittest.TestCase):
    def test_add_to_empty(self):
        """
        Test adding a context to an empty config
        """
        config = {'intentions': defaultdict(lambda: defaultdict(
            lambda: defaultdict(int))), 'contexts': defaultdict(lambda: defaultdict(float))}
        context = 'the context'
        instantiations = {
            'inst_a': 0.3, 'inst_b': 0.3, 'inst_c': 0.4}

        config['contexts'][context] = instantiations

        bn = BayesNet()
        # I assume this will throw an Error!
        with self.assertRaises(AssertionError):
            bn.add_context(context, instantiations)
        # Making sure tmp_config will be maintained
        self.assertEqual(bn.config, config)

    def test_add_n_to_empty(self, n=N):
        """
        Test adding n contexts to an empty config
        """
        config = {'intentions': defaultdict(lambda: defaultdict(
            lambda: defaultdict(int))), 'contexts': defaultdict(lambda: defaultdict(float))}
        context = 'context'
        instantiations = {
            'inst_a': 0.3, 'inst_b': 0.3, 'inst_c': 0.4}

        bn = BayesNet()
        # I assume this will throw an Error!
        for i in range(n):
            config['contexts'][f'{context}_{i}'] = instantiations
            with self.assertRaises(AssertionError):
                bn.add_context(f'{context}_{i}', instantiations)
        # Making sure tmp_config will be maintained
        self.assertEqual(bn.config, config)

    def test_add_to_existing(self):
        """
        Test adding a context to an existing config
        """
        config = load_config('small_example.yml')
        bn = BayesNet(config)
        bn.add_context('the context', {
                       'inst_a': 0.3, 'inst_b': 0.3, 'inst_c': 0.4})

    def test_add_n_to_existing(self, n=N):
        """
        Test adding n contexts to an existing config
        """
        config = load_config('small_example.yml')
        bn = BayesNet(config)
        for i in range(n):
            bn.add_context(f'context_{i}', {
                'inst_a': 0.3, 'inst_b': 0.3, 'inst_c': 0.4})

    def test_add_to_existing_loaded(self):
        """
        Test adding a context to an existing config - with empty init and load
        """
        bn = BayesNet()
        bn.load('small_example.yml')
        bn.add_context('the context', {
                       'inst_a': 0.3, 'inst_b': 0.3, 'inst_c': 0.4})

    def test_add_n_to_existing_loaded(self, n=N):
        """
        Test adding n contexts to an existing config - with empty init and load
        """
        bn = BayesNet()
        bn.load('small_example.yml')
        for i in range(n):
            bn.add_context(f'context_{i}', {
                'inst_a': 0.3, 'inst_b': 0.3, 'inst_c': 0.4})


if __name__ == '__main__':
    unittest.main()
