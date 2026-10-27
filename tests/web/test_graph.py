"""Tests for the graph of the web GUI (`cobair.web.graph`)."""

# System imports

# 3rd party imports
import pytest

pytest.importorskip('reflex')

# local imports
from cobair.model import Config  # noqa: E402
from cobair.web.graph import build_graph, edge_style  # noqa: E402

# end file header
__author__ = 'Adrian Lubitz'


@pytest.fixture
def config():
    """The small example.

    Returns:
        Config: The config.
    """
    return Config.load('small_example.yml')


def by_id(items: list) -> dict:
    """Index nodes or edges by id.

    Args:
        items: Nodes or edges.

    Returns:
        dict: `{id: item}`
    """
    return {item['id']: item for item in items}


def test_folded_graph(config):
    """Contexts, intentions and the combined influence are nodes, edges use the mean influence."""
    nodes, edges = build_graph(config)
    nodes, edges = by_id(nodes), by_id(edges)
    assert set(nodes) == {'c:0', 'c:1', 'c:2', 't:0', 't:1', 'k:0'}
    assert nodes['c:0']['data']['label'].startswith('human activity')
    assert nodes['t:1']['data']['label'] == 'pick up tool'
    assert nodes['k:0']['data']['label'] == 'pickup ∧ working'
    # human activity on hand over tool: idle 4, working 1 -> mean 2.5
    assert edges['c:0->t:0']['data']['influence'] == 2.5
    assert edges['c:0->t:0']['style']['strokeWidth'] == 5.0
    # combined influence: from both contexts to the combination, from there to the intention
    assert {'c:2->k:0', 'c:0->k:0', 'k:0->t:1'} <= set(edges)
    assert edges['k:0->t:1']['data']['influence'] == 5
    assert len(edges) == 3 * 2 + 3


def test_contexts_on_the_left_intentions_on_the_right(config):
    """Two layers: contexts left, combined influences in the middle, intentions right."""
    nodes = by_id(build_graph(config)[0])
    assert nodes['c:0']['position']['x'] < nodes['k:0']['position']['x'] < \
        nodes['t:0']['position']['x']
    assert nodes['c:0']['type'] == 'input' and nodes['t:0']['type'] == 'output'


def test_expanded_context(config):
    """An expanded context shows its instantiations with their own influences."""
    nodes, edges = build_graph(config, expanded=[2])
    nodes, edges = by_id(nodes), by_id(edges)
    assert {'i:2:0', 'i:2:1', 'i:2:2'} <= set(nodes)
    assert nodes['i:2:2']['data']['label'] == 'pickup'
    assert 'c:2->t:1' not in edges
    assert edges['i:2:2->t:1']['data']['influence'] == 4
    assert edges['i:2:1->t:1']['style']['strokeDasharray'] == '4 4'  # other: 0
    # the combination starts at the instantiation now
    assert 'i:2:2->k:0' in edges and 'c:2->k:0' not in edges


@pytest.mark.parametrize('influence, dashed, width', [(0, True, 1), (1, False, 2.6),
                                                      (5, False, 9.0)])
def test_edge_style(influence, dashed, width):
    """Thicker and more colored edges for more influence, dashed for none."""
    style = edge_style(influence)
    assert ('strokeDasharray' in style) == dashed
    assert style['strokeWidth'] == width


def test_evidence_and_probabilities(config):
    """Evidence highlights instantiations, probabilities color the intentions (#207)."""
    nodes = by_id(build_graph(config, expanded=[2], evidence={1: 1, 2: 2},
                              probabilities=[0.25, 0.75])[0])
    assert nodes['c:1']['data']['label'].startswith('human holding object = True')
    assert nodes['i:2:2']['style']['fontWeight'] == 'bold'
    assert 'fontWeight' not in nodes['i:2:0']['style']
    assert nodes['t:1']['data']['label'] == 'pick up tool 75%'
    assert nodes['t:1']['style']['background'] != nodes['t:0']['style']['background']


def test_empty_config():
    """An empty config has an empty graph."""
    assert build_graph(Config()) == ([], [])
