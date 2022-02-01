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
    def test_edit_context_from_empty(self):
        """
        Test editing on a non existing config
        """
        bn = BayesNet()
        # I assume this will throw an Error!
        with self.assertRaises(ValueError):
            bn.edit_context('the context', {
                'inst_a': 0.3, 'inst_b': 0.3, 'inst_c': 0.4})

    def test_edit_context_from_existing_new_name(self):
        """
        Test editing on an existing config - only changing the name of the context
        """
        bn = BayesNet()
        bn.load('small_example.yml')
        new_name = 'commandos de speechos'
        old_context = 'speech commands'
        old_config = deepcopy(bn.config)
        # I assume this will throw an Error!
        instantiations = deepcopy(bn.config['contexts'][old_context])
        bn.edit_context(old_context, instantiations, new_name=new_name)
        self.assertIn(new_name, bn.config['contexts'])
        self.assertNotIn(old_context, bn.config['contexts'])
        self.assertEqual(instantiations, bn.config['contexts'][new_name])
        for intention in bn.config['intentions']:
            self.assertIn(new_name, bn.config['intentions'][intention])
            self.assertNotIn(old_context, bn.config['intentions'][intention])
            self.assertEqual(old_config['intentions'][intention]
                             [old_context], bn.config['intentions'][intention][new_name])

    def test_edit_context_from_existing_new_instantiations(self):
        """
        Test editing on an existing config - changing the names and values of the instantiations
        """
        bn = BayesNet()
        bn.load('small_example.yml')
        context = 'speech commands'
        old_config = deepcopy(bn.config)
        # I assume this will throw an Error!
        instantiations = {
            'inst_a': 0.3, 'inst_b': 0.3, 'inst_c': 0.4}
        bn.edit_context(context, instantiations)

        self.assertIn(context, bn.config['contexts'])
        self.assertEqual(instantiations, bn.config['contexts'][context])
        for intention in bn.config['intentions']:
            self.assertIn(context, bn.config['intentions'][intention])
            # all influence values will be set to zero because I don't know if the instantiation is a total new or just corrected a typo
            for instantiation in instantiations:
                self.assertIn(
                    instantiation, bn.config['intentions'][intention][context])
                self.assertEqual(
                    0, bn.config['intentions'][intention][context][instantiation])

    def test_edit_context_from_existing_adjust_instantiations(self):
        """
        Test editing on an existing config - changing one name of the instantiations
        """
        bn = BayesNet()
        bn.load('small_example.yml')
        context = 'speech commands'
        old_config = deepcopy(bn.config)
        old_instantiation_name = 'pickup'
        new_instantiation_name = 'pick up'
        # I assume this will throw an Error!
        instantiations = deepcopy(bn.config['contexts'][context])
        old_value = instantiations[old_instantiation_name]
        del(instantiations[old_instantiation_name])
        instantiations[new_instantiation_name] = old_value
        bn.edit_context(context, instantiations)

        self.assertIn(context, bn.config['contexts'])
        self.assertEqual(instantiations, bn.config['contexts'][context])
        for intention in bn.config['intentions']:
            self.assertIn(context, bn.config['intentions'][intention])
            # all influence values will be set to zero because I don't know if the instantiation is a total new or just corrected a typo
            for instantiation in instantiations:
                self.assertIn(
                    instantiation, bn.config['intentions'][intention][context])
                if instantiation != new_instantiation_name:
                    self.assertEqual(old_config['intentions'][intention][context][instantiation],
                                     bn.config['intentions'][intention][context][instantiation])
                else:
                    self.assertEqual(
                        bn.config['intentions'][intention][context][instantiation], 0)

    def test_edit_context_from_existing_new_instantiations_and_new_name(self):
        """
        Test editing on an existing config - changing the names and values of the instantiations and the context name
        """
        bn = BayesNet()
        bn.load('small_example.yml')
        new_name = 'commandos de speechos'
        old_context = 'speech commands'
        old_config = deepcopy(bn.config)
        # I assume this will throw an Error!
        instantiations = {
            'inst_a': 0.3, 'inst_b': 0.3, 'inst_c': 0.4}
        bn.edit_context(old_context, instantiations, new_name=new_name)
        self.assertIn(new_name, bn.config['contexts'])
        self.assertEqual(instantiations, bn.config['contexts'][new_name])

        for intention in bn.config['intentions']:
            self.assertIn(new_name, bn.config['intentions'][intention])
            # all influence values will be set to zero because I don't know if the instantiation is a total new or just corrected a typo
            for instantiation in instantiations:
                self.assertIn(
                    instantiation, bn.config['intentions'][intention][new_name])
                self.assertEqual(
                    0, bn.config['intentions'][intention][new_name][instantiation])

    def test_edit_context_from_existing_adjust_instantiations(self):
        """
        Test editing on an existing config - changing one name of the instantiations and the context name
        """
        bn = BayesNet()
        bn.load('small_example.yml')
        new_name = 'commandos de speechos'
        old_context = 'speech commands'
        old_config = deepcopy(bn.config)
        old_instantiation_name = 'pickup'
        new_instantiation_name = 'pick up'
        # I assume this will throw an Error!
        instantiations = deepcopy(bn.config['contexts'][old_context])
        old_value = instantiations[old_instantiation_name]
        del(instantiations[old_instantiation_name])
        instantiations[new_instantiation_name] = old_value
        bn.edit_context(old_context, instantiations, new_name=new_name)

        self.assertIn(new_name, bn.config['contexts'])
        self.assertEqual(instantiations, bn.config['contexts'][new_name])
        for intention in bn.config['intentions']:
            self.assertIn(new_name, bn.config['intentions'][intention])
            # all influence values will be set to zero because I don't know if the instantiation is a total new or just corrected a typo
            for instantiation in instantiations:
                self.assertIn(
                    instantiation, bn.config['intentions'][intention][new_name])
                if instantiation != new_instantiation_name:
                    self.assertEqual(old_config['intentions'][intention][old_context][instantiation],
                                     bn.config['intentions'][intention][new_name][instantiation])
                else:
                    self.assertEqual(
                        bn.config['intentions'][intention][new_name][instantiation], 0)


if __name__ == '__main__':
    unittest.main()
