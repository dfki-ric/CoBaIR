"""Pages of the CoBaIR web GUI."""

# System imports

# 3rd party imports
import reflex as rx

# local imports
from .state import SCALE, CombinedPart, ContextView, EditorState, InfluenceRow, scale_label

# end file header
__author__ = 'Adrian Lubitz'

DOCS_URL = 'https://dfki-ric.github.io/CoBaIR/'
TUTORIAL_URL = f'{DOCS_URL}Tutorial/'
UPLOAD_ID = 'config_upload'

#: Help texts with the Tutorial section they link to (#178 - #181).
HELP = {
    'apriori': ('How likely each instantiation of a context is if the context is not observed. '
                'The values of a context must sum up to 1.', 'apriori-probabilities'),
    'influence': ('How strongly an instantiation of a context indicates an intention, '
                  'from 0 (not probable) to 5 (definitely probable).', 'influence-values'),
    'combined': ('An influence for a combination of instantiations. If all of them are '
                 'observed, it replaces the single influences of these contexts.',
                 'combined-context-influence'),
    'threshold': ('The probability the most likely intention must exceed to be recognized. '
                  'Below it, no intention is recognized.', 'decision-threshold'),
}

#: Reports unsaved changes to the browser when the page is closed or reloaded.
UNLOAD_GUARD = """
window.addEventListener('beforeunload', (event) => {
  if (window.cobairDirty) { event.preventDefault(); event.returnValue = ''; }
});
"""

#: Ctrl/Cmd+Z undoes, Ctrl/Cmd+Shift+Z and Ctrl/Cmd+Y redo. Text fields keep their own undo and
#: dialogs are left alone.
UNDO_KEYS = """
if (!window.cobairUndoKeys) {
  window.cobairUndoKeys = true;
  document.addEventListener('keydown', (event) => {
    if (!(event.ctrlKey || event.metaKey) || event.altKey) return;
    const key = event.key.toLowerCase();
    if (key !== 'z' && key !== 'y') return;
    const editing = event.target.closest &&
      event.target.closest('input, textarea, select, [contenteditable="true"]');
    if (editing || document.querySelector('[role="dialog"]')) return;
    const button = document.getElementById(key === 'y' || event.shiftKey ? 'redo' : 'undo');
    event.preventDefault();
    if (button && !button.disabled) button.click();
  });
}
"""


def info(topic: str) -> rx.Component:
    """Return an info icon with a help text that links to the Tutorial.

    Args:
        topic: A key of `HELP`.

    Returns:
        rx.Component: The icon with tooltip.
    """
    text, anchor = HELP[topic]
    return rx.tooltip(
        rx.link(rx.icon('info', size=16), href=f'{TUTORIAL_URL}#{anchor}', is_external=True,
                id=f'help-{topic}', aria_label=f'Help: {topic}'),
        content=f'{text} Click for more.',
    )


def foldable(header: rx.Component, *children, gap: str = '0.75em', **props) -> rx.Component:
    """Return content that is folded by clicking its header (folding happens in the browser).

    Buttons and links in the header keep working, they don't fold.

    Args:
        header: The always visible header row.
        *children: The foldable content.
        gap: Space between header and content.
        **props: Props of the surrounding `details` element.

    Returns:
        rx.Component: The open `details` element.
    """
    return rx.el.details(
        rx.el.summary(
            rx.hstack(rx.icon('chevron-down', size=18, class_name='fold-chevron'), header,
                      align='center', width='100%'),
            class_name='fold',
        ),
        rx.vstack(*children, width='100%', padding_top=gap),
        open=True,
        width='100%',
        **props,
    )


def section(title: str, *children, topic: str = None, actions: rx.Component = None,
            **props) -> rx.Component:
    """Return a titled section that can be folded.

    Args:
        title: The heading.
        *children: The content.
        topic: Optional help topic shown next to the heading.
        actions: Optional buttons on the right of the heading.
        **props: Props of the surrounding element.

    Returns:
        rx.Component: The section.
    """
    return foldable(
        rx.hstack(rx.heading(title, size='5'), info(topic) if topic else rx.fragment(),
                  rx.spacer(), actions or rx.fragment(), align='center', width='100%'),
        *children,
        **props,
    )


def toolbar() -> rx.Component:
    """Buttons for files and undo.

    Returns:
        rx.Component: The toolbar.
    """
    return rx.hstack(
        rx.button(rx.icon('file-plus', size=16), 'New', on_click=EditorState.new_config,
                  variant='soft', id='new-config'),
        rx.upload.root(
            rx.button(rx.icon('upload', size=16), 'Load YAML', variant='soft', id='load-yaml'),
            id=UPLOAD_ID,
            accept={'application/x-yaml': ['.yml', '.yaml'], 'text/yaml': ['.yml', '.yaml']},
            multiple=False,
            max_files=1,
            on_drop=EditorState.upload_config,
        ),
        rx.button('Load example', on_click=EditorState.load_example, variant='soft',
                  id='load-example'),
        rx.button(rx.icon('download', size=16), 'Download YAML',
                  on_click=EditorState.download_config, variant='soft', id='download'),
        rx.cond(EditorState.local_file != '',
                rx.button(rx.icon('save', size=16), 'Save', on_click=EditorState.save_config,
                          id='save')),
        rx.tooltip(rx.icon_button(rx.icon('undo-2', size=16), on_click=EditorState.undo,
                                   disabled=~EditorState.can_undo, variant='soft', id='undo',
                                   aria_label='Undo'),
                   content='Undo (Ctrl+Z)'),
        rx.tooltip(rx.icon_button(rx.icon('redo-2', size=16), on_click=EditorState.redo,
                                  disabled=~EditorState.can_redo, variant='soft', id='redo',
                                  aria_label='Redo'),
                   content='Redo (Ctrl+Shift+Z)'),
        rx.spacer(),
        rx.cond(EditorState.file_name != '',
                rx.badge(EditorState.file_name, id='file-name', size='2')),
        rx.cond(EditorState.dirty,
                rx.tooltip(rx.badge('unsaved changes', color_scheme='gray', id='dirty', size='2'),
                           content=f'Not saved to {EditorState.local_file} yet')),
        width='100%',
        align='center',
        wrap='wrap',
    )


def messages() -> rx.Component:
    """Error and info of the last action and the problems of the config.

    Returns:
        rx.Component: The callouts.
    """
    return rx.vstack(
        rx.cond(EditorState.error != '',
                rx.callout(EditorState.error, icon='triangle_alert', color_scheme='red',
                           id='error', width='100%')),
        rx.cond(EditorState.info != '',
                rx.callout(EditorState.info, icon='info', color_scheme='blue', id='info',
                           width='100%')),
        rx.cond(
            EditorState.problems.length() > 0,
            rx.callout.root(
                rx.callout.icon(rx.icon('list-checks')),
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


# ----------------------------------------------------------------------------------------------
# contexts and intentions

def context_card(context: ContextView, index: rx.Var) -> rx.Component:
    """A context with editable apriori probabilities.

    Args:
        context: The context.
        index: Position of the context.

    Returns:
        rx.Component: The card.
    """
    return rx.card(foldable(
        rx.hstack(
            rx.heading(context.name, size='3', class_name='context-name'),
            rx.text(f'{context.instantiations.length()} instantiations', size='1',
                    color_scheme='gray'),
            rx.spacer(),
            rx.icon_button(rx.icon('pencil', size=14), size='1', variant='ghost',
                           on_click=EditorState.open_edit_context(index),
                           class_name='edit-context', aria_label='Edit context'),
            rx.icon_button(rx.icon('trash-2', size=14), size='1', variant='ghost',
                           color_scheme='red', on_click=EditorState.delete_context(index),
                           class_name='delete-context', aria_label='Delete context'),
            align='center',
            width='100%',
        ),
        rx.foreach(
            context.instantiations,
            lambda instantiation, instantiation_index: rx.hstack(
                rx.text(instantiation.name, width='50%'),
                rx.input(
                    default_value=instantiation.apriori,
                    # recreated only if its own value changes (load, undo): a key that changes with
                    # every edit would recreate the input the user just tabbed into, losing focus
                    key=f'{index}-{instantiation_index}-{instantiation.apriori}',
                    id=f'apriori-{index}-{instantiation_index}',
                    on_blur=lambda text: EditorState.set_apriori(index, instantiation_index,
                                                                 text),
                    size='1',
                    width='50%',
                    class_name='apriori-input',
                    aria_label='Apriori probability',
                ),
                width='100%',
                align='center',
            ),
        ),
        gap='0.5em',
    ), class_name='context-card', width='100%')


def intention_card(intention: rx.Var, index: rx.Var) -> rx.Component:
    """An intention with rename and delete buttons.

    Args:
        intention: The name.
        index: Position of the intention.

    Returns:
        rx.Component: The card.
    """
    return rx.card(
        rx.hstack(
            rx.text(intention, class_name='intention-name'),
            rx.spacer(),
            rx.icon_button(rx.icon('pencil', size=14), size='1', variant='ghost',
                           on_click=EditorState.open_rename_intention(index),
                           class_name='rename-intention', aria_label='Rename intention'),
            rx.icon_button(rx.icon('trash-2', size=14), size='1', variant='ghost',
                           color_scheme='red', on_click=EditorState.delete_intention(index),
                           class_name='delete-intention', aria_label='Delete intention'),
            width='100%',
            align='center',
        ),
        class_name='intention-card',
        width='100%',
    )


# ----------------------------------------------------------------------------------------------
# influences

def scale_select(value: rx.Var, on_change, **trigger_props) -> rx.Component:
    """Return a select for an influence value with the human readable scale.

    Args:
        value: The current value as text.
        on_change: Event handler for the new value.
        **trigger_props: Props of the trigger (the select root renders no element).

    Returns:
        rx.Component: The select.
    """
    return rx.select.root(
        rx.select.trigger(width='100%', **trigger_props),
        rx.select.content(*[rx.select.item(scale_label(level), value=str(level))
                            for level in SCALE]),
        value=value,
        on_change=on_change,
        size='1',
    )


def influence_row(row: InfluenceRow, instantiation_index: rx.Var) -> rx.Component:
    """The influences of one instantiation on all intentions.

    Args:
        row: The instantiation and its influence values.
        instantiation_index: Position of the instantiation.

    Returns:
        rx.Component: The table row.
    """
    return rx.table.row(
        rx.table.row_header_cell(row.name),
        rx.foreach(
            row.influences,
            lambda value, intention_index: rx.table.cell(scale_select(
                value,
                lambda new: EditorState.set_influence(instantiation_index, intention_index, new),
                class_name='influence-select',
            )),
        ),
    )


def influences() -> rx.Component:
    """Table of the influences of the selected context on all intentions.

    Returns:
        rx.Component: The section.
    """
    return section(
        'Influences',
        rx.cond(
            (EditorState.contexts.length() > 0) & (EditorState.intentions.length() > 0),
            rx.vstack(
                rx.hstack(
                    rx.text('Influence of'),
                    rx.select.root(
                        rx.select.trigger(id='influence-context'),
                        rx.select.content(rx.foreach(
                            EditorState.contexts,
                            lambda context, index: rx.select.item(context.name,
                                                                  value=index.to_string()))),
                        value=EditorState.influence_context,
                        on_change=EditorState.select_influence_context,
                    ),
                    rx.text('on the intentions'),
                    align='center',
                ),
                rx.table.root(
                    rx.table.header(rx.table.row(
                        rx.table.column_header_cell('Instantiation'),
                        rx.foreach(EditorState.intentions, rx.table.column_header_cell),
                    )),
                    rx.table.body(rx.foreach(EditorState.influence_rows, influence_row)),
                    id='influence-table',
                    width='100%',
                ),
                width='100%',
            ),
            rx.text('Add contexts and intentions to set their influences.', color_scheme='gray'),
        ),
        topic='influence',
        id='influences-section',
    )


def combined_influences() -> rx.Component:
    """List of the combined influences.

    Returns:
        rx.Component: The section.
    """
    return section(
        'Combined influences',
        rx.cond(
            EditorState.combined.length() > 0,
            rx.table.root(
                rx.table.header(rx.table.row(
                    rx.table.column_header_cell('Intention'),
                    rx.table.column_header_cell('Combination'),
                    rx.table.column_header_cell('Influence'),
                    rx.table.column_header_cell(''),
                )),
                rx.table.body(rx.foreach(
                    EditorState.combined,
                    lambda combined, index: rx.table.row(
                        rx.table.cell(combined.intention),
                        rx.table.cell(combined.combination),
                        rx.table.cell(combined.value),
                        rx.table.cell(rx.icon_button(
                            rx.icon('trash-2', size=14), size='1', variant='ghost',
                            color_scheme='red', on_click=EditorState.remove_combined(index),
                            class_name='remove-combined', aria_label='Remove')),
                        class_name='combined-row',
                    ),
                )),
                width='100%',
            ),
            rx.text('No combined influences.', color_scheme='gray'),
        ),
        topic='combined',
        id='combined-section',
        actions=rx.button(rx.icon('plus', size=16), 'Add', size='1', variant='soft',
                          on_click=EditorState.open_combined_dialog, id='add-combined'),
    )


def threshold() -> rx.Component:
    """Input for the decision threshold.

    Returns:
        rx.Component: The section.
    """
    return section(
        'Decision threshold',
        rx.input(
            default_value=EditorState.decision_threshold,
            key=EditorState.decision_threshold,
            on_blur=EditorState.set_threshold,
            id='threshold',
            width='10em',
            aria_label='Decision threshold',
        ),
        topic='threshold',
        id='threshold-section',
    )


# ----------------------------------------------------------------------------------------------
# dialogs

def dialog_error(error: rx.Var, id_: str) -> rx.Component:
    """Return the error line of a dialog.

    Args:
        error: The error text.
        id_: The element id.

    Returns:
        rx.Component: The error text, if any.
    """
    return rx.cond(error != '', rx.text(error, color_scheme='red', id=id_))


def dialog_buttons(on_save, save_id: str, close_event) -> rx.Component:
    """Return Cancel / Save buttons.

    Args:
        on_save: Event of the save button.
        save_id: Id of the save button.
        close_event: Event closing the dialog.

    Returns:
        rx.Component: The buttons.
    """
    return rx.hstack(
        rx.button('Cancel', variant='soft', color_scheme='gray', on_click=close_event),
        rx.button('Save', on_click=on_save, id=save_id),
        justify='end',
        width='100%',
    )


def context_dialog() -> rx.Component:
    """Dialog to add or edit a context.

    Returns:
        rx.Component: The dialog.
    """
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(rx.cond(EditorState.context_dialog_index >= 0, 'Edit context',
                                    'New context')),
            rx.vstack(
                rx.input(value=EditorState.context_dialog_name,
                         on_change=EditorState.set_context_dialog_name,
                         placeholder='Context name', id='context-name', width='100%'),
                rx.hstack(rx.text('Instantiation', width='55%', weight='bold'),
                          rx.text('Apriori probability', weight='bold'), info('apriori'),
                          width='100%'),
                rx.foreach(
                    EditorState.context_dialog_rows,
                    lambda row, index: rx.hstack(
                        rx.input(value=row.name,
                                 on_change=lambda name: EditorState.set_context_row_name(
                                     index, name),
                                 placeholder='Instantiation', width='55%',
                                 class_name='instantiation-name'),
                        rx.input(value=row.apriori,
                                 on_change=lambda value: EditorState.set_context_row_apriori(
                                     index, value),
                                 width='30%', class_name='instantiation-apriori'),
                        rx.icon_button(rx.icon('x', size=14), size='1', variant='ghost',
                                       color_scheme='red',
                                       on_click=EditorState.remove_context_row(index),
                                       aria_label='Remove instantiation'),
                        width='100%',
                        align='center',
                    ),
                ),
                rx.button(rx.icon('plus', size=14), 'Instantiation', size='1', variant='soft',
                          on_click=EditorState.add_context_row, id='add-instantiation'),
                dialog_error(EditorState.context_dialog_error, 'context-dialog-error'),
                dialog_buttons(EditorState.save_context_dialog, 'save-context',
                               EditorState.set_context_dialog_open(False)),
                width='100%',
            ),
        ),
        open=EditorState.context_dialog_open,
        on_open_change=EditorState.set_context_dialog_open,
    )


def intention_dialog() -> rx.Component:
    """Dialog to add or rename an intention.

    Returns:
        rx.Component: The dialog.
    """
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(rx.cond(EditorState.intention_dialog_index >= 0, 'Rename intention',
                                    'New intention')),
            rx.vstack(
                rx.input(value=EditorState.intention_dialog_name,
                         on_change=EditorState.set_intention_dialog_name,
                         placeholder='Intention name', id='intention-name', width='100%'),
                dialog_error(EditorState.intention_dialog_error, 'intention-dialog-error'),
                dialog_buttons(EditorState.save_intention_dialog, 'save-intention',
                               EditorState.set_intention_dialog_open(False)),
                width='100%',
            ),
        ),
        open=EditorState.intention_dialog_open,
        on_open_change=EditorState.set_intention_dialog_open,
    )


def combined_part(part: CombinedPart, index: rx.Var) -> rx.Component:
    """A context and its instantiation in the combined influence dialog.

    Args:
        part: The selected context and instantiation.
        index: Position of the part.

    Returns:
        rx.Component: The row.
    """
    return rx.hstack(
        rx.select.root(
            rx.select.trigger(flex='1', min_width='0', class_name='combined-part-select'),
            rx.select.content(rx.foreach(
                EditorState.contexts,
                lambda context, context_index: rx.select.item(
                    context.name, value=context_index.to_string()))),
            value=part.context,
            on_change=lambda value: EditorState.set_combined_part_context(index, value),
        ),
        rx.text('='),
        rx.select.root(
            rx.select.trigger(flex='1', min_width='0', class_name='combined-part-select'),
            rx.select.content(rx.foreach(
                EditorState.contexts[part.context.to(int)].instantiations,
                lambda instantiation, instantiation_index: rx.select.item(
                    instantiation.name, value=instantiation_index.to_string()))),
            value=part.instantiation,
            on_change=lambda value: EditorState.set_combined_part_instantiation(index, value),
        ),
        rx.icon_button(rx.icon('x', size=14), size='1', variant='ghost', color_scheme='red',
                       on_click=EditorState.remove_combined_part(index),
                       aria_label='Remove context'),
        width='100%',
        align='center',
        class_name='combined-part',
    )


def combined_dialog() -> rx.Component:
    """Dialog to add a combined influence.

    Returns:
        rx.Component: The dialog.
    """
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title('New combined influence'),
            rx.vstack(
                rx.hstack(rx.text('Influence on'), info('combined'), align='center'),
                rx.select.root(
                    rx.select.trigger(width='100%', id='combined-intention'),
                    rx.select.content(rx.foreach(
                        EditorState.intentions,
                        lambda intention, index: rx.select.item(intention,
                                                                value=index.to_string()))),
                    value=EditorState.combined_intention,
                    on_change=EditorState.set_combined_intention,
                ),
                rx.text('if all of these are observed'),
                rx.foreach(EditorState.combined_parts, combined_part),
                rx.button(rx.icon('plus', size=14), 'Context', size='1', variant='soft',
                          on_click=EditorState.add_combined_part, id='add-combined-part'),
                rx.text('is'),
                scale_select(EditorState.combined_value, EditorState.set_combined_value,
                             id='combined-value'),
                dialog_error(EditorState.combined_error, 'combined-dialog-error'),
                dialog_buttons(EditorState.save_combined_dialog, 'save-combined',
                               EditorState.set_combined_dialog_open(False)),
                width='100%',
            ),
        ),
        open=EditorState.combined_dialog_open,
        on_open_change=EditorState.set_combined_dialog_open,
    )


# ----------------------------------------------------------------------------------------------
# page

def index() -> rx.Component:
    """The editor page.

    Returns:
        rx.Component: The page.
    """
    return rx.container(
        rx.script(UNLOAD_GUARD),
        rx.script(UNDO_KEYS),
        rx.vstack(
            rx.hstack(
                rx.image(src='/logo.png', alt='CoBaIR logo', height='2.2em', width='auto',
                         align_self='center', id='logo'),
                rx.heading('CoBaIR', size='7'),
                rx.text('Context Based Intention Recognition', color_scheme='gray'),
                rx.spacer(),
                rx.link('Documentation', href=DOCS_URL, is_external=True),
                align='baseline',
                width='100%',
            ),
            toolbar(),
            messages(),
            rx.grid(
                section(
                    'Contexts',
                    rx.foreach(EditorState.contexts, context_card),
                    topic='apriori',
                    actions=rx.button(rx.icon('plus', size=16), 'Add', size='1', variant='soft',
                                      on_click=EditorState.open_new_context, id='add-context'),
                    id='contexts',
                ),
                section(
                    'Intentions',
                    rx.foreach(EditorState.intentions, intention_card),
                    actions=rx.button(rx.icon('plus', size=16), 'Add', size='1', variant='soft',
                                      on_click=EditorState.open_new_intention,
                                      id='add-intention'),
                    id='intentions',
                ),
                columns=rx.breakpoints(initial='1', md='2'),
                spacing='4',
                width='100%',
            ),
            influences(),
            combined_influences(),
            threshold(),
            spacing='5',
            width='100%',
            padding_bottom='4em',
        ),
        context_dialog(),
        intention_dialog(),
        combined_dialog(),
        size='4',
    )


app = rx.App(stylesheets=['/editor.css'],
             head_components=[rx.el.link(rel='icon', type='image/png', href='/logo.png')])
app.add_page(index, title='CoBaIR', on_load=EditorState.on_load)
