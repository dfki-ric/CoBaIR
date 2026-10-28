"""Tests for cobair.infer."""

# System imports
import itertools
import math

# 3rd party imports
import pytest

# local imports
from cobair.infer import Inference, InferenceResult, normalize
from cobair.model import Config

# end file header
__author__ = 'Adrian Lubitz'

SPEECH = 'speech commands'
ACTIVITY = 'human activity'
HOLDING = 'human holding object'
PICK = 'pick up tool'
HAND = 'hand over tool'


@pytest.fixture(scope='module')
def inference():
    """Inference for the small example.

    Returns:
        Inference: The inference.
    """
    return Inference(Config.load('small_example.yml'))


def brute_force(config: Config, evidence: dict) -> dict:
    """Infer P(intention | evidence) by summing over all unobserved contexts, without pgmpy.

    Args:
        config: A valid config.
        evidence: `{context: instantiation}` for some contexts of the config.

    Returns:
        dict: `{intention: unnormalized probability}`
    """
    cpts = config.cpts()
    probabilities = {}
    for intention in cpts.intentions:
        positive = cpts.intention_values[intention][1]
        total = 0.0
        for column, case in enumerate(itertools.product(
                *(cpts.states[context] for context in cpts.contexts))):
            weight = 1.0
            for context, instantiation in zip(cpts.contexts, case):
                if context in evidence:
                    weight *= evidence[context] == instantiation
                else:
                    weight *= config.contexts[context][instantiation]
            total += weight * positive[column]
        probabilities[intention] = total
    return probabilities


@pytest.mark.parametrize('evidence, expected', [
    # the 4.x test had 0.6028 / 0.3972 for no evidence, but never compared them
    ({}, {PICK: 0.6222014925373134, HAND: 0.3777985074626865}),
    ({SPEECH: 'pickup'}, {HAND: 0.23157894736842097, PICK: 0.768421052631579}),
    ({SPEECH: 'pickup', HOLDING: False, ACTIVITY: 'idle'},
     {HAND: 0.46153846153846145, PICK: 0.5384615384615384}),
    ({SPEECH: 'pickup', HOLDING: True, ACTIVITY: 'working'},
     {HAND: 0.04878048780487805, PICK: 0.9512195121951219}),
])
def test_known_values(inference, evidence, expected):
    """The values known from the 4.x tests."""
    result = inference.infer(evidence)
    assert result.probabilities == pytest.approx(expected, abs=1e-7)


@pytest.mark.parametrize('example', ['small_example.yml', 'small_example_altered.yml'])
def test_matches_brute_force(example):
    """Pgmpy agrees with the brute-force inference for every combination of evidence."""
    config = Config.load(example)
    config.add_combined_influence(HAND, (HOLDING, SPEECH), (True, 'other'), 2)
    config.add_combined_influence(HAND, (HOLDING, SPEECH), (False, 'other'), 5)
    inference = Inference(config)
    options = {context: [None, *instantiations]
               for context, instantiations in config.contexts.items()}
    for case in itertools.product(*options.values()):
        evidence = {context: value for context, value in zip(options, case) if value is not None}
        raw = inference.infer(evidence, normalized=False).probabilities
        assert raw == pytest.approx(brute_force(config, evidence), abs=1e-9), evidence


def test_result_unpacks_like_old_tuple(inference):
    """The result is a NamedTuple and unpacks like the tuple of BayesNet.infer."""
    result = inference.infer({SPEECH: 'pickup'})
    assert isinstance(result, InferenceResult)
    intention, threshold, probabilities = result
    assert intention is None  # 0.768 does not exceed the threshold 0.8
    assert threshold == 0.8
    assert probabilities is result.probabilities


def test_decision_threshold(inference):
    """The most likely intention is returned if it exceeds the threshold."""
    result = inference.infer({SPEECH: 'pickup'}, decision_threshold=0.7)
    assert result.intention == PICK
    assert result.decision_threshold == 0.7


def test_normalized(inference):
    """Normalized probabilities sum up to 1, raw ones don't."""
    assert math.isclose(sum(inference.infer({}).probabilities.values()), 1)
    assert not math.isclose(sum(inference.infer({}, normalized=False).probabilities.values()), 1)
    assert normalize({'a': 1, 'b': 3}) == {'a': 0.25, 'b': 0.75}


def test_warnings_for_ignored_evidence(inference):
    """Unknown contexts, unknown instantiations and None are ignored with a warning."""
    expected = inference.infer({}).probabilities
    for evidence in [{'unknown context': 'x'}, {SPEECH: 'unknown'}, {SPEECH: None}]:
        with pytest.warns(UserWarning):
            result = inference.infer(evidence)
        assert result.probabilities == pytest.approx(expected)


def test_unhashable_evidence(inference):
    """Unhashable instantiations of known contexts are errors."""
    with pytest.raises(ValueError, match='hashable'):
        inference.infer({SPEECH: {}})


def test_discretization_function():
    """Discretization functions are applied to evidence which is no instantiation."""
    inference = Inference(Config.load('small_example.yml'))
    inference.bind_discretization_function(HOLDING, lambda value: value > 0.5)
    with pytest.raises(ValueError):
        inference.bind_discretization_function('unknown', bool)
    assert inference.infer({HOLDING: 0.9}).probabilities == pytest.approx(
        inference.infer({HOLDING: True}).probabilities)
    assert inference.infer({HOLDING: 0.1}).probabilities == pytest.approx(
        inference.infer({HOLDING: False}).probabilities)
    # instantiations are used as they are
    assert inference.infer({HOLDING: False}).probabilities != pytest.approx(
        inference.infer({HOLDING: True}).probabilities)


def test_discretization_to_invalid_value():
    """A discretization function returning no instantiation ignores the evidence with a warning."""
    inference = Inference(Config.load('small_example.yml'))
    inference.bind_discretization_function(SPEECH, lambda value: 'crap')
    with pytest.warns(UserWarning, match='not a valid instantiation'):
        result = inference.infer({SPEECH: 'louder'})
    assert result.probabilities == pytest.approx(inference.infer({}).probabilities)
    # valid instantiations don't go through the function
    assert inference.infer({SPEECH: 'pickup'}).probabilities[PICK] > 0.7


def test_snapshot_of_config():
    """Editing the config after creating the inference does not change the inference."""
    config = Config.load('small_example.yml')
    inference = Inference(config)
    before = inference.infer({}).probabilities
    config.change_influence_value(PICK, SPEECH, 'other', 5)
    assert inference.infer({}).probabilities == before
    assert Inference(config).infer({}).probabilities != before


def test_invalid_config():
    """An inference needs a valid config."""
    with pytest.raises(ValueError, match='Invalid configuration'):
        Inference(Config())
