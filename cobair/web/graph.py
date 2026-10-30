"""Interactive graph of the two-layer Bayesian net, drawn with React Flow.

`build_graph` computes the nodes and edges in Python, the `ReactFlow` component only renders them.
Node ids: `c:<context>` for contexts, `i:<context>:<instantiation>` for instantiations,
`t:<intention>` for intentions and `k:<n>` for combined influences, all as positions in the config.
"""

# System imports
from __future__ import annotations

# 3rd party imports
import reflex as rx
from reflex_base.vars.base import Var

# local imports
from ..model import Config

# end file header
__author__ = 'Adrian Lubitz'

REACT_FLOW = '@xyflow/react@12.12.0'

CONTEXT_X = 0
COMBINED_X = 330
INTENTION_X = 620
ROW_HEIGHT = 70
INSTANTIATION_HEIGHT = 48
NODE_WIDTH = 190

ACCENT = (247, 107, 21)  # orange, like the theme
GRAY = (200, 200, 200)


def _mix(value: float) -> str:
    """Return the color between gray (0) and the accent color (1).

    Args:
        value: Between 0 and 1.

    Returns:
        str: A CSS rgb color.
    """
    red, green, blue = (round(gray + (accent - gray) * value)
                        for gray, accent in zip(GRAY, ACCENT))
    return f'rgb({red}, {green}, {blue})'


def edge_style(influence: float) -> dict:
    """Return the style of an edge for an influence value.

    Args:
        influence: Influence value (or mean influence) between 0 and 5.

    Returns:
        dict: The React Flow edge style.
    """
    if influence <= 0:
        return {'stroke': _mix(0), 'strokeWidth': 1, 'strokeDasharray': '4 4'}
    return {'stroke': _mix(influence / 5), 'strokeWidth': round(1 + influence * 1.6, 1)}


def _node(node_id: str, label: str, x: float, y: float, kind: str, **style) -> dict:
    """Return a React Flow node.

    Args:
        node_id: The id.
        label: The text.
        x: The x position.
        y: The y position.
        kind: `input` (only outgoing edges), `output` (only incoming) or `default`.
        **style: CSS style of the node.

    Returns:
        dict: The node.
    """
    return {
        'id': node_id,
        'type': kind,
        'data': {'label': label},
        'position': {'x': x, 'y': y},
        'sourcePosition': 'right',
        'targetPosition': 'left',
        'className': f'graph-node graph-{node_id[0]}',
        'style': {'width': NODE_WIDTH, 'fontSize': 13, **style},
    }


def build_graph(config: Config, expanded: list = (), evidence: dict = None,
                probabilities: list = None) -> tuple[list, list]:
    """Compute the nodes and edges of the graph of a config.

    Args:
        config: The config.
        expanded: Positions of the contexts shown with their instantiations.
        evidence: `{context position: instantiation position}` of observed contexts.
        probabilities: The probability of every intention, colors the intention nodes.

    Returns:
        tuple[list, list]: React Flow nodes and edges.
    """
    evidence = evidence or {}
    contexts = list(config.contexts)
    intentions = list(config.intentions)
    nodes, edges = [], []
    # source node of every (context, instantiation), the context node if folded
    sources = {}
    y = 0
    for c_index, context in enumerate(contexts):
        instantiations = list(config.contexts[context])
        observed = c_index in evidence
        style = {'borderColor': _mix(1), 'borderWidth': 2} if observed else {}
        if c_index in expanded:
            nodes.append(_node(f'c:{c_index}', f'{context} ▾', CONTEXT_X - 30, y, 'default',
                               fontWeight='bold', **style))
            y += INSTANTIATION_HEIGHT
            for i_index, instantiation in enumerate(instantiations):
                node_id = f'i:{c_index}:{i_index}'
                active = evidence.get(c_index) == i_index
                nodes.append(_node(node_id, str(instantiation), CONTEXT_X, y, 'input',
                                   **({'background': _mix(0.35), 'fontWeight': 'bold'}
                                      if active else {})))
                sources[(context, instantiation)] = node_id
                y += INSTANTIATION_HEIGHT
            y += ROW_HEIGHT - INSTANTIATION_HEIGHT
        else:
            label = str(context)
            if observed:
                label = f'{context} = {instantiations[evidence[c_index]]}'
            nodes.append(_node(f'c:{c_index}', f'{label} ▸', CONTEXT_X, y, 'input', **style))
            for instantiation in instantiations:
                sources[(context, instantiation)] = f'c:{c_index}'
            y += ROW_HEIGHT
    context_height = y

    intention_y = max(0, (context_height - len(intentions) * ROW_HEIGHT * 1.5) / 2)
    for t_index, intention in enumerate(intentions):
        style = {}
        label = str(intention)
        if probabilities is not None:
            probability = probabilities[t_index]
            label = f'{intention} {probability:.0%}'
            style = {'background': _mix(probability), 'fontWeight': 'bold'}
        nodes.append(_node(f't:{t_index}', label, INTENTION_X,
                           intention_y + t_index * ROW_HEIGHT * 1.5, 'output', **style))

    combined_y = 0
    combined_index = 0
    for t_index, intention in enumerate(intentions):
        influences = config.intentions[intention]
        for c_index, context in enumerate(contexts):
            values = influences.get(context, {})
            if c_index in expanded:
                for instantiation in config.contexts[context]:
                    edges.append(_edge(sources[(context, instantiation)], f't:{t_index}',
                                       values.get(instantiation, 0)))
            else:
                instantiations = config.contexts[context]
                mean = (sum(values.get(instantiation, 0) for instantiation in instantiations)
                        / len(instantiations)) if instantiations else 0
                edges.append(_edge(f'c:{c_index}', f't:{t_index}', mean))
        for names, combinations in influences.items():
            if not isinstance(names, tuple):
                continue
            for combination, value in combinations.items():
                node_id = f'k:{combined_index}'
                combined_index += 1
                text = ' ∧ '.join(str(instantiation) for instantiation in combination)
                nodes.append(_node(node_id, text, COMBINED_X, combined_y, 'default',
                                   fontSize=11, borderStyle='dashed', width=150))
                combined_y += ROW_HEIGHT
                for context, instantiation in zip(names, combination):
                    # the parts are different contexts, so their sources never repeat
                    source = sources.get((context, instantiation))
                    if source is not None:
                        edges.append({'id': f'{source}->{node_id}', 'source': source,
                                      'target': node_id, 'style': {
                                          'stroke': _mix(0.2), 'strokeDasharray': '2 3'}})
                edges.append(_edge(node_id, f't:{t_index}', value))
    return nodes, edges


def _edge(source: str, target: str, influence: float) -> dict:
    """Return an influence edge.

    Args:
        source: Id of the source node.
        target: Id of the target node.
        influence: The (mean) influence value.

    Returns:
        dict: The React Flow edge.
    """
    return {'id': f'{source}->{target}', 'source': source, 'target': target,
            'style': edge_style(influence), 'data': {'influence': influence}}


class _ReactFlowLib(rx.Component):
    """Base of the React Flow components."""

    library = REACT_FLOW

    def add_imports(self) -> dict:
        """Import the React Flow stylesheet.

        Returns:
            dict: The imports.
        """
        return {'': '@xyflow/react/dist/style.css'}


def _id_of_second_arg(_event: Var, item: Var) -> tuple[Var[str]]:
    """Event spec passing only the id of the clicked node or edge.

    Args:
        _event: The mouse event (not serializable, dropped).
        item: The node or edge.

    Returns:
        tuple[Var[str]]: The id.
    """
    return (item.to(dict)['id'].to(str),)


class ReactFlow(_ReactFlowLib):
    """The React Flow graph."""

    tag = 'ReactFlow'

    nodes: Var[list[dict]]
    edges: Var[list[dict]]
    fit_view: Var[bool]
    nodes_draggable: Var[bool]
    nodes_connectable: Var[bool]
    elements_selectable: Var[bool]
    zoom_on_scroll: Var[bool]
    prevent_scrolling: Var[bool]
    min_zoom: Var[float]
    max_zoom: Var[float]

    on_node_click: rx.EventHandler[_id_of_second_arg]
    on_edge_click: rx.EventHandler[_id_of_second_arg]


class Background(_ReactFlowLib):
    """The dotted background."""

    tag = 'Background'


class Controls(_ReactFlowLib):
    """Zoom buttons."""

    tag = 'Controls'
    show_interactive: Var[bool]


react_flow = ReactFlow.create
background = Background.create
controls = Controls.create
