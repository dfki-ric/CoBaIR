'''
Tests for adding intention variables
'''

# System imports
import unittest
from collections import defaultdict

# 3rd party imports

# local imports
from tests import N
from CoBaBIR.bayes_net import BayesNet, load_config
# end file header
__author__ = 'Adrian Lubitz'

# TODO: add more negative cases


class TestAddIntention(unittest.TestCase):
    def test_add_to_empty(self):
        """
        Test adding an intention to an empty config
        """
        config = {'intentions': defaultdict(lambda: defaultdict(
            lambda: defaultdict(int))), 'contexts': defaultdict(lambda: defaultdict(float))}
        intention = 'some intention'

        config['intentions'][intention] = {}
        bn = BayesNet()
        # I assume this will throw an Error!
        with self.assertRaises(AssertionError):
            bn.add_intention('some intention')
        # Making sure tmp_config will be maintained
        self.assertEqual(bn.config, config)

    def test_add_n_to_empty(self, n=N):
        """
        Test adding n intentions to an empty config
        """
        config = {'intentions': defaultdict(lambda: defaultdict(
            lambda: defaultdict(int))), 'contexts': defaultdict(lambda: defaultdict(float))}
        intention = 'intention'
        bn = BayesNet()
        # I assume this will throw an Error!
        for i in range(n):
            config['intentions'][f'{intention}_{i}'] = {}
            with self.assertRaises(AssertionError):
                bn.add_intention(f'{intention}_{i}')
        # Making sure tmp_config will be maintained
        self.assertEqual(bn.config, config)

    def test_add_to_existing(self):
        """
        Test adding an intention to an existing config
        """
        config = load_config('small_example.yml')
        bn = BayesNet(config)
        bn.add_intention('some intention')

    def test_add_n_to_existing(self, n=N):
        """
        Test adding n intentions to an existing config
        """
        config = load_config('small_example.yml')
        bn = BayesNet(config)
        for i in range(n):
            bn.add_intention(f'intention_{i}')

    def test_add_to_existing_loaded(self):
        """
        Test adding an intention to an existing config
        """
        bn = BayesNet()
        bn.load('small_example.yml')
        bn.add_intention('some intention')

    def test_add_n_to_existing_loaded(self, n=N):
        """
        Test adding n intentions to an existing config
        """
        bn = BayesNet()
        bn.load('small_example.yml')
        for i in range(n):
            bn.add_intention(f'intention_{i}')


if __name__ == '__main__':
    unittest.main()
