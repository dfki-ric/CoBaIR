'''
Tests for adding intention variables
'''

# System imports
import pytest

# local imports
from tests import N
from CoBaIR.bayes_net import BayesNet, default_to_regular, load_config

# end file header
__author__ = 'Adrian Lubitz'
bn = BayesNet()
bn.load('small_example.yml')


def test_infer_no_evidence():
    """
    Test inference without evidence
    """
    probabilities = {'pick up tool': 0.602803738317757,
                     'hand over tool': 0.397196261682243}

    max_intention, decision_threshold, inference = bn.infer({})
    assert inference is not None, "No intention was inferred"
    if max_intention is not None:
        assert decision_threshold > 0
        assert round(abs(inference - probabilities[max_intention]), 7) == 0


def test_infer_unrelated_evidence():
    """
    Test inference with unrelated evidence of different types
    """
    probabilities = {'pick up tool': 0.602803738317757,
                     'hand over tool': 0.397196261682243}

    with pytest.warns(UserWarning):
        max_intention, decision_threshold, inference = bn.infer({'some context': 'is not important',
                                                                'another context': '',
                                                                 'unhashable context': {},
                                                                 'int context': 1,
                                                                 'obj context': bn})

    if max_intention is not None:
        assert decision_threshold > 0
        assert round(abs(inference - probabilities[max_intention]), 7) == 0


def test_infer_single_evidence():
    """
    Test inference with single evidence context present
    """
    probabilities = {'hand over tool': 0.23157894736842097,
                     'pick up tool': 0.768421052631579}

    max_intention, decision_threshold, inference = bn.infer(
        {'speech commands': 'pickup'})
    for intention, probability in inference.items():
        assert round(abs(probability-probabilities[intention]), 7) == 0


def test_infer_multiple_evidence():
    """
    Test inference with multiple evidence context present
    """
    probabilities = {'hand over tool': 0.46153846153846145,
                     'pick up tool': 0.5384615384615384}
    with pytest.warns(UserWarning):
        max_intention, decision_threshold, inference = bn.infer({
            'speech commands': 'pickup',
            'human holding object': False,
            'human activity': 'idle',
            'unhashable context': {}
        })
    for intention, probability in inference.items():
        assert round(abs(probability-probabilities[intention]), 7) == 0


def test_infer_combined_evidence():
    """
    Test inference for the combined case
    """
    probabilities = {'hand over tool': 0.04878048780487805,
                     'pick up tool': 0.9512195121951219}

    with pytest.warns(UserWarning):
        max_intention, decision_threshold, inference = bn.infer({
            'speech commands': 'pickup',
            'human holding object': True,
            'human activity': 'working',
            'unhashable context': {}
        })
    for intention, probability in inference.items():
        assert round(abs(probability-probabilities[intention]), 7) == 0


def test_infer_overlapping_combined_evidence():
    """
    Test inference for combined case if two combinations are overlapping - not implemented yet!
    """
    # probabilities = {'hand over tool': 0.26229508196721313,
    #                  'pick up tool': 0.7377049180327869}

    # inference = self.bn.infer(
    #     {'speech commands': 'pickup',
    # 'human holding object': True, 'human activity': 'idle', 'unhashable context': {}})
    # print(inference)
    # for intention, probability in inference.items():
    #     self.assertAlmostEqual(probability, probabilities[intention])
    pass


def test_infer_invalid_evidence():
    """
    Test inference with unhashable context instantiation
    """
    probabilities = {'pick up tool': 0.7821782178217822,
                     'hand over tool': 0.21782178217821785}

    with pytest.raises(ValueError):
        bn.infer(
            {'speech commands': {}, })


def test_infer_warning_evidence():
    """
    Test inference with context instantiation that cause warnings 'this context': 'will be ignored anyways'
    """
    probabilities = {'pick up tool': 0.7821782178217822,
                     'hand over tool': 0.21782178217821785}

    with pytest.warns(UserWarning):
        bn.infer(
            {'speech commands': 'something not related', 'this context': 'will be ignored anyways'})
