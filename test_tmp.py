'''
Tests for adding context variables
'''

# System imports
import unittest
from collections import defaultdict
from tests import N


# 3rd party imports

# local imports
from CoBaBIR.bayes_net import BayesNet, load_config, config_to_default_dict
# end file header
__author__ = 'Adrian Lubitz'


class TestAddContext(unittest.TestCase):
    def test_add_n_to_existing(self, n=N):
        """
        Test adding n contexts to an existing config
        """
        config = load_config('small_example.yml')
        bn = BayesNet(config)
        for i in range(n):
            bn.add_context(f'context_{i}', {
                'inst_a': 0.3, 'inst_b': 0.3, 'inst_c': 0.4})
        bn.save('load_multi_context_add.yml')


if __name__ == '__main__':
    unittest.main()
