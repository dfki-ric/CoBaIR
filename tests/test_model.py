"""Tests for cobair.model."""

# System imports
import warnings

# 3rd party imports
import pytest
import yaml

# local imports
from cobair.model import FORMAT_VERSION, HEADER, Config

# end file header
__author__ = 'Adrian Lubitz'

SPEECH = 'speech commands'
ACTIVITY = 'human activity'
HOLDING = 'human holding object'
PICK = 'pick up tool'
HAND = 'hand over tool'


@pytest.fixture
def config():
    """The small example config.

    Returns:
        Config: The config.
    """
    return Config.load('small_example.yml')


def simple_config():
    """A valid config with two contexts and one intention.

    Returns:
        Config: The config.
    """
    config = Config(decision_threshold=0.5)
    config.add_context('a', {'x': 0.5, 'y': 0.5})
    config.add_context('b', {True: 0.3, False: 0.7})
    config.add_intention('i')
    return config


# ----------------------------------------------------------------------------------------------
# loading, saving, conversion

def test_load_small_example(config):
    """The small example is loaded with tuples and bools as keys and is valid."""
    assert list(config.contexts) == [ACTIVITY, HOLDING, SPEECH]
    assert config.contexts[HOLDING] == {False: 0.6, True: 0.4}
    assert config.intentions[PICK][(SPEECH, ACTIVITY)] == {('pickup', 'working'): 5}
    assert config.decision_threshold == 0.8
    assert config.validate() == []
    assert config.valid


def test_save_and_load_roundtrip(config, tmp_path):
    """A saved config loads as the same config and keeps the order."""
    config.add_combined_influence(HAND, (HOLDING, SPEECH), (True, 'other'), 2)
    path = tmp_path / 'config.yml'
    config.save(path)
    loaded = Config.load(path)
    assert loaded == config
    assert list(loaded.contexts[SPEECH]) == list(config.contexts[SPEECH])
    assert list(loaded.intentions[PICK]) == list(config.intentions[PICK])


def test_header(config):
    """Saved configs start with the header comment and the format keys."""
    text = config.dumps()
    assert text.startswith(HEADER)
    lines = text[len(HEADER):].splitlines()
    assert lines[0] == f'format_version: {FORMAT_VERSION}'
    assert lines[1].startswith('created_with: cobair ')


def test_header_ignored_by_old_loader(config):
    """The 4.x loader only copies contexts, intentions and decision_threshold."""
    from cobair.bayes_net import load_config  # pylint: disable=import-outside-toplevel
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', DeprecationWarning)
        old = load_config('small_example.yml')
    assert set(old) == {'contexts', 'intentions', 'decision_threshold'}
    assert Config.loads(config.dumps()) == config


def test_load_newer_format_version():
    """Configs of a newer format version are rejected."""
    with pytest.raises(ValueError, match='format version'):
        Config.loads(f'format_version: {FORMAT_VERSION + 1}\ncontexts: {{}}\n')


@pytest.mark.parametrize('text', ['- a\n- b\n', 'just text'])
def test_load_no_mapping(text):
    """A YAML file which is not a mapping is no config."""
    with pytest.raises(ValueError, match='mapping'):
        Config.loads(text)


def test_load_empty():
    """An empty file is an empty (invalid) config."""
    config = Config.loads('')
    assert config == Config()
    assert not config.valid


def test_unsafe_yaml_is_rejected():
    """Only tuples are allowed as python tags."""
    with pytest.raises(yaml.constructor.ConstructorError):
        Config.loads('contexts: !!python/object/apply:os.system ["echo hi"]\n')


def test_from_dict_copies():
    """Changing the dict after creating the config doesn't change the config."""
    contexts = {'a': {'x': 0.5, 'y': 0.5}}
    config = Config(contexts)
    contexts['a']['x'] = 1.0
    assert config.contexts['a']['x'] == 0.5
    data = config.to_dict()
    data['contexts']['a']['x'] = 1.0
    assert config.contexts['a']['x'] == 0.5


def test_copy_and_equality(config):
    """A copy is equal but independent."""
    copy = config.copy()
    assert copy == config
    copy.change_decision_threshold(0.1)
    assert copy != config
    assert config != 'not a config'


# ----------------------------------------------------------------------------------------------
# validation

def test_validate_empty():
    """An empty config has no contexts and no intentions."""
    problems = Config().validate()
    assert 'No contexts defined' in problems
    assert 'No intentions defined' in problems


@pytest.mark.parametrize('threshold', [-0.1, 1, 1.5, 'high', None, True])
def test_validate_threshold(threshold):
    """The decision threshold must be a number in [0, 1)."""
    config = simple_config()
    config.change_decision_threshold(threshold)
    assert config.validate() == ['Decision threshold must be a number between 0 and 1']


@pytest.mark.parametrize('threshold', [0, 0.0, 0.99])
def test_validate_threshold_valid(threshold):
    """Integers are numbers as well."""
    config = simple_config()
    config.change_decision_threshold(threshold)
    assert config.valid


def test_validate_apriori_sum():
    """Apriori probabilities must sum up to 1, with a tolerance for float errors."""
    config = simple_config()
    config.edit_context('a', {'x': 0.1, 'y': 0.2, 'z': 0.7})
    assert config.valid
    config.change_context_apriori_value('a', 'z', 0.6)
    problems = config.validate()
    assert len(problems) == 1
    assert problems[0].startswith('The sum of probabilities for context instantiations must be 1')


def test_validate_apriori_not_a_number():
    """Apriori probabilities must be numbers."""
    config = simple_config()
    config.change_context_apriori_value('a', 'x', 'half')
    assert config.validate() == ['Apriori probability of context "a.x" is not a number']


@pytest.mark.parametrize('value', [6, -1, 2.5, True])
def test_validate_influence_value(value):
    """Influences must be integers between 0 and 5."""
    config = simple_config()
    config.change_influence_value('i', 'a', 'x', value)
    assert len(config.validate()) == 1
    assert 'must be an integer between 0 and 5' in config.validate()[0]


def test_validate_unknown_context_and_instantiation():
    """Influences of unknown contexts or instantiations are reported."""
    config = Config.from_dict({
        'contexts': {'a': {'x': 0.5, 'y': 0.5}},
        'intentions': {'i': {'a': {'x': 1, 'y': 1, 'z': 1}, 'b': {'u': 1},
                             ('a', 'b'): {('x', 'u'): 1}, ('a',): {('z',): 2}}},
        'decision_threshold': 0.5})
    problems = config.validate()
    assert any('i.a.z does not fit' in problem for problem in problems)
    assert any("Context influence b of i" in problem for problem in problems)
    assert any("Context influence ('a', 'b') of i" in problem for problem in problems)
    assert any("('z',) is not a valid combination" in problem for problem in problems)
    assert len(problems) == 4


def test_missing_influences_count_as_zero():
    """Like in 4.x, missing influences are valid and count as 0."""
    config = Config.from_dict({'contexts': {'a': {'x': 0.5, 'y': 0.5}},
                               'intentions': {'i': {'a': {'x': 5}}, 'j': {}},
                               'decision_threshold': 0.5})
    assert config.valid
    assert config.cpts().intention_values['i'][1] == [0.95, 0.0]
    assert config.cpts().intention_values['j'][1] == [0.0, 0.0]


# ----------------------------------------------------------------------------------------------
# editing

def test_add_context_sets_zero_influences():
    """A new context gets the influence 0 for all intentions."""
    config = simple_config()
    config.add_context('c', {1: 0.5, 2: 0.5})
    assert config.intentions['i']['c'] == {1: 0, 2: 0}
    with pytest.raises(ValueError):
        config.add_context('c', {1: 1.0})


def test_add_intention_sets_zero_influences():
    """A new intention gets the influence 0 for all contexts."""
    config = simple_config()
    assert config.intentions['i'] == {'a': {'x': 0, 'y': 0}, 'b': {True: 0, False: 0}}
    with pytest.raises(ValueError):
        config.add_intention('i')


def test_edit_context_instantiations(config):
    """Removed instantiations lose their (combined) influences, new ones get 0."""
    config.change_influence_value(PICK, SPEECH, 'other', 3)
    config.edit_context(SPEECH, {'pickup': 0.5, 'other': 0.3, 'stop': 0.2})
    assert config.intentions[PICK][SPEECH] == {'pickup': 4, 'other': 3, 'stop': 0}
    assert (SPEECH, ACTIVITY) in config.intentions[PICK]
    config.edit_context(SPEECH, {'other': 0.5, 'stop': 0.5})
    assert (SPEECH, ACTIVITY) not in config.intentions[PICK]
    assert config.valid


def test_edit_context_rename_keeps_combined_influences(config):
    """Renaming a context renames it in the combined influences (lost in 4.x)."""
    config.edit_context(SPEECH, config.contexts[SPEECH], new_name='speech')
    assert 'speech' in config.contexts and SPEECH not in config.contexts
    assert config.intentions[PICK][('speech', ACTIVITY)] == {('pickup', 'working'): 5}
    assert config.intentions[HAND]['speech'] == {'handover': 4, 'other': 0, 'pickup': 0}
    assert list(config.contexts) == [ACTIVITY, HOLDING, 'speech']
    assert config.valid


def test_edit_context_errors(config):
    """Editing unknown contexts or renaming onto another context fails."""
    with pytest.raises(ValueError):
        config.edit_context('unknown', {'a': 1.0})
    with pytest.raises(ValueError, match='exists already'):
        config.edit_context(SPEECH, config.contexts[SPEECH], new_name=ACTIVITY)
    before = config.copy()
    config.edit_context(SPEECH, config.contexts[SPEECH], new_name=SPEECH)
    assert config == before


def test_edit_other_context_keeps_combined_influences(config):
    """Editing an unrelated context doesn't remove combined influences (it did in 4.x)."""
    config.edit_context(HOLDING, {True: 0.5, False: 0.5})
    assert config.intentions[PICK][(SPEECH, ACTIVITY)] == {('pickup', 'working'): 5}


def test_del_context(config):
    """Deleting a context removes its influences and the combined influences using it."""
    config.del_context(ACTIVITY)
    assert ACTIVITY not in config.contexts
    assert ACTIVITY not in config.intentions[HAND]
    assert config.combined_influences(PICK) == {}
    assert config.valid
    with pytest.raises(ValueError):
        config.del_context(ACTIVITY)


def test_edit_and_del_intention(config):
    """Intentions can be renamed (keeping the order) and deleted."""
    config.edit_intention(HAND, 'give tool')
    assert list(config.intentions) == ['give tool', PICK]
    with pytest.raises(ValueError):
        config.edit_intention('unknown', 'x')
    with pytest.raises(ValueError):
        config.edit_intention('give tool', PICK)
    config.del_intention('give tool')
    assert list(config.intentions) == [PICK]
    with pytest.raises(ValueError):
        config.del_intention('give tool')


def test_change_values(config):
    """Apriori and influence values can only be changed if they exist."""
    config.change_context_apriori_value(SPEECH, 'other', 0.4)
    assert config.contexts[SPEECH]['other'] == 0.4
    config.change_influence_value(PICK, SPEECH, 'other', 2)
    assert config.intentions[PICK][SPEECH]['other'] == 2
    config.change_influence_value(PICK, (SPEECH, ACTIVITY), ('pickup', 'working'), 1)
    assert config.intentions[PICK][(SPEECH, ACTIVITY)] == {('pickup', 'working'): 1}
    with pytest.raises(ValueError):
        config.change_context_apriori_value(SPEECH, 'unknown', 0.1)
    with pytest.raises(ValueError):
        config.change_context_apriori_value('unknown', 'other', 0.1)
    with pytest.raises(ValueError):
        config.change_influence_value(PICK, SPEECH, 'unknown', 1)
    with pytest.raises(ValueError):
        config.change_influence_value('unknown', SPEECH, 'other', 1)


def test_combined_influences(config):
    """Several combinations per context tuple can be added and removed one by one."""
    config.add_combined_influence(PICK, [SPEECH, ACTIVITY], ['other', 'idle'], 1)
    assert config.combined_influences(PICK) == {
        (SPEECH, ACTIVITY): {('pickup', 'working'): 5, ('other', 'idle'): 1}}
    config.del_combined_influence(PICK, (SPEECH, ACTIVITY), ('pickup', 'working'))
    assert config.combined_influences(PICK) == {(SPEECH, ACTIVITY): {('other', 'idle'): 1}}
    config.del_combined_influence(PICK, (SPEECH, ACTIVITY), ('other', 'idle'))
    assert config.combined_influences(PICK) == {}
    with pytest.raises(ValueError):
        config.del_combined_influence(PICK, (SPEECH, ACTIVITY), ('other', 'idle'))


@pytest.mark.parametrize('intention, contexts, instantiations', [
    (PICK, (), ()),
    ('unknown', (SPEECH,), ('pickup',)),
    (PICK, (SPEECH, ACTIVITY), ('pickup', 'sleeping')),
    (PICK, (SPEECH, 'unknown'), ('pickup', 'working')),
    (PICK, (SPEECH, ACTIVITY), ('pickup',)),
])
def test_add_combined_influence_errors(config, intention, contexts, instantiations):
    """Combined influences need an existing intention and existing instantiations."""
    with pytest.raises(ValueError):
        config.add_combined_influence(intention, contexts, instantiations, 3)


# ----------------------------------------------------------------------------------------------
# conditional probability tables

def test_cpts_structure(config):
    """The CPTs have one column per combination of context instantiations."""
    cpts = config.cpts()
    assert cpts.contexts == [ACTIVITY, HOLDING, SPEECH]
    assert cpts.cards == [2, 2, 3]
    assert cpts.context_priors[SPEECH] == [0.2, 0.6, 0.2]
    for negative, positive in cpts.intention_values.values():
        assert len(positive) == 12
        assert all(abs(n + p - 1) < 1e-12 for n, p in zip(negative, positive))


def test_cpts_values():
    """The probability is the average of the influence probabilities."""
    config = simple_config()
    config.change_influence_value('i', 'a', 'x', 5)  # 0.95
    config.change_influence_value('i', 'b', False, 3)  # 0.5
    # columns: (x, True), (x, False), (y, True), (y, False)
    assert config.cpts().intention_values['i'][1] == pytest.approx(
        [0.475, 0.725, 0.0, 0.25])


def test_cpts_combined_influence_replaces_single_influences():
    """A matching combination replaces the influences of all its contexts."""
    config = simple_config()
    config.add_combined_influence('i', ('a', 'b'), ('y', True), 4)  # 0.75 for a and b
    assert config.cpts().intention_values['i'][1] == pytest.approx([0, 0, 0.75, 0])


def test_cpts_second_combination_counts():
    """All combinations of a context tuple count (4.x only used the first one)."""
    config = simple_config()
    config.add_combined_influence('i', ('a', 'b'), ('y', True), 4)
    config.add_combined_influence('i', ('a', 'b'), ('x', False), 2)
    assert config.cpts().intention_values['i'][1] == pytest.approx([0, 0.25, 0.75, 0])


def test_cpts_invalid_config():
    """CPTs can only be computed for valid configs."""
    with pytest.raises(ValueError, match='Invalid configuration'):
        Config().cpts()
