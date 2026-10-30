"""Pages of the CoBaIR web GUI."""

# System imports

# 3rd party imports
import reflex as rx

# local imports
from .state import ContextView, EditorState, InstantiationView

# end file header
__author__ = 'Adrian Lubitz'

DOCS_URL = 'https://dfki-ric.github.io/CoBaIR/'
UPLOAD_ID = 'config_upload'


def toolbar() -> rx.Component:
    """Buttons to create, upload and load configs.

    Returns:
        rx.Component: The toolbar.
    """
    return rx.hstack(
        rx.button('New', on_click=EditorState.new_config, variant='soft', id='new-config'),
        rx.upload.root(
            rx.button('Load YAML', variant='soft', id='load-yaml'),
            id=UPLOAD_ID,
            accept={'application/x-yaml': ['.yml', '.yaml'], 'text/yaml': ['.yml', '.yaml']},
            multiple=False,
            max_files=1,
            on_drop=EditorState.upload_config,
        ),
        rx.button('Load example', on_click=EditorState.load_example, variant='soft',
                  id='load-example'),
        rx.spacer(),
        rx.cond(EditorState.file_name != '',
                rx.badge(EditorState.file_name, id='file-name', size='2')),
        width='100%',
        align='center',
    )


def instantiation_row(instantiation: InstantiationView) -> rx.Component:
    """One instantiation with its apriori probability.

    Args:
        instantiation: The instantiation.

    Returns:
        rx.Component: The table row.
    """
    return rx.table.row(
        rx.table.cell(instantiation.name),
        rx.table.cell(instantiation.apriori),
    )


def context_card(context: ContextView) -> rx.Component:
    """A context with its instantiations.

    Args:
        context: The context.

    Returns:
        rx.Component: The card.
    """
    return rx.card(
        rx.heading(context.name, size='3'),
        rx.table.root(
            rx.table.header(rx.table.row(
                rx.table.column_header_cell('Instantiation'),
                rx.table.column_header_cell('Apriori probability'),
            )),
            rx.table.body(rx.foreach(context.instantiations, instantiation_row)),
            size='1',
        ),
        class_name='context-card',
        width='100%',
    )


def problems() -> rx.Component:
    """Error of the last action and the problems of the config.

    Returns:
        rx.Component: The callouts.
    """
    return rx.vstack(
        rx.cond(EditorState.error != '',
                rx.callout(EditorState.error, icon='triangle_alert', color_scheme='red',
                           id='error', width='100%')),
        rx.cond(
            EditorState.problems.length() > 0,
            rx.callout.root(
                rx.callout.icon(rx.icon('info')),
                rx.vstack(rx.foreach(EditorState.problems, rx.text), spacing='1'),
                color_scheme='orange',
                id='problems',
                width='100%',
            ),
            rx.cond(EditorState.contexts.length() > 0,
                    rx.callout('The config is valid.', icon='check', color_scheme='green',
                               id='valid', width='100%')),
        ),
        width='100%',
    )


def index() -> rx.Component:
    """The editor page.

    Returns:
        rx.Component: The page.
    """
    return rx.container(
        rx.vstack(
            rx.hstack(
                rx.heading('CoBaIR', size='7'),
                rx.text('Context Based Intention Recognition', color_scheme='gray'),
                rx.spacer(),
                rx.link('Documentation', href=DOCS_URL, is_external=True),
                align='baseline',
                width='100%',
            ),
            toolbar(),
            problems(),
            rx.grid(
                rx.vstack(
                    rx.heading('Contexts', size='5'),
                    rx.foreach(EditorState.contexts, context_card),
                    id='contexts',
                    width='100%',
                ),
                rx.vstack(
                    rx.heading('Intentions', size='5'),
                    rx.foreach(EditorState.intentions,
                               lambda intention: rx.card(intention, class_name='intention-card',
                                                         width='100%')),
                    id='intentions',
                    width='100%',
                ),
                columns=rx.breakpoints(initial='1', md='2'),
                spacing='4',
                width='100%',
            ),
            spacing='4',
            width='100%',
        ),
        size='4',
    )


app = rx.App(theme=rx.theme(accent_color='orange'))
app.add_page(index, title='CoBaIR')
