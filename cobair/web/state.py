"""State of the CoBaIR web GUI.

The config is kept as `cobair.model.Config` in a backend-only var (its tuple keys can't be sent to
the browser). After every change `_sync()` derives the plain vars the frontend renders.
Contexts, instantiations and intentions are addressed by their position, because their labels are
not unique (e.g. the instantiations `True` and `"True"`).
"""

# System imports
from __future__ import annotations

import dataclasses
import json
import os
from importlib import resources
from pathlib import Path

# 3rd party imports
import reflex as rx

# local imports
from ..model import INFLUENCE_TO_PROBABILITY, Config

# end file header
__author__ = 'Adrian Lubitz'

EXAMPLE_FILE = 'small_example.yml'
#: Environment variable with the config file `cobair-web` was started with.
FILE_ENV = 'COBAIR_WEB_FILE'
MAX_UNDO = 100

#: Human readable influence scale (#144).
SCALE = {
    0: 'not probable',
    1: 'not very probable',
    2: 'somewhat probable',
    3: 'even probability',
    4: 'very probable',
    5: 'definitely probable',
}


def scale_label(value: int) -> str:
    """Return the label of an influence value, e.g. `4 - very probable (75 %)`.

    Args:
        value: The influence value 0 - 5.

    Returns:
        str: The label.
    """
    return f'{value} - {SCALE[value]} ({INFLUENCE_TO_PROBABILITY[value]:.0%})'


def read_example() -> str:
    """Return the YAML text of the example config shipped with the package.

    Returns:
        str: The example config.
    """
    return resources.files('cobair.web').joinpath('examples', EXAMPLE_FILE).read_text(
        encoding='utf-8')


def label(value) -> str:
    """Return the text shown for a context, instantiation or intention.

    Args:
        value: A key of the config (str, bool, int, ...).

    Returns:
        str: The label.
    """
    return str(value)


def show_value(element_id: str, value: str):
    """Put a value into an input again, e.g. after rejected text.

    The inputs are uncontrolled and only recreated when their value changes. `rx.set_value` needs a
    ref, which inputs with a dynamic id in `rx.foreach` don't get.

    Args:
        element_id: The id of the input.
        value: The value to show.

    Returns:
        The event.
    """
    return rx.call_script(f'(document.getElementById({json.dumps(element_id)}) || {{}}).value = '
                          f'{json.dumps(value)}')


def parse_probability(text: str) -> float:
    """Parse an apriori probability or decision threshold.

    Args:
        text: The text of the input, `,` is accepted as decimal separator.

    Returns:
        float: The number.

    Raises:
        ValueError: If the text is not a number.
    """
    try:
        return float(text.strip().replace(',', '.'))
    except ValueError:
        raise ValueError(f'"{text}" is not a number') from None


@dataclasses.dataclass
class InstantiationView:
    """An instantiation of a context as shown in the editor."""

    name: str = ''
    apriori: str = ''


@dataclasses.dataclass
class ContextView:
    """A context as shown in the editor."""

    name: str = ''
    instantiations: list[InstantiationView] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class InfluenceRow:
    """The influences of one instantiation on all intentions."""

    name: str = ''
    influences: list[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class CombinedView:
    """A combined influence as shown in the editor."""

    intention: str = ''
    combination: str = ''
    value: str = ''


@dataclasses.dataclass
class CombinedPart:
    """A context and one of its instantiations in the combined influence dialog."""

    context: str = '0'
    instantiation: str = '0'


class EditorState(rx.State):
    """The config being edited and everything the editor shows of it."""

    # backend only
    _config: Config | None = None
    _saved: Config | None = None
    _undo: list = []
    _redo: list = []
    _combined_keys: list = []
    _initialized: bool = False

    #: Name of the loaded or last saved file.
    file_name: str = ''
    #: Path of the file `cobair-web` was started with, empty in the browser-only mode.
    local_file: str = ''
    #: The contexts with their instantiations and apriori probabilities.
    contexts: list[ContextView] = []
    #: Names of the intentions.
    intentions: list[str] = []
    #: The decision threshold as text.
    decision_threshold: str = '0.0'
    #: Problems of the config, empty if valid.
    problems: list[str] = []
    #: Error of the last action (e.g. a file that could not be loaded).
    error: str = ''
    #: Information about the last action (e.g. a restored draft).
    info: str = ''
    #: Changes not saved to `local_file` yet. Without a file it stays False: nothing is written to
    #: disk and the draft in the browser storage keeps the changes.
    dirty: bool = False
    can_undo: bool = False
    can_redo: bool = False

    #: Index of the context shown in the influence table.
    influence_context: str = '0'
    influence_rows: list[InfluenceRow] = []
    combined: list[CombinedView] = []

    #: Draft of the config in the browser storage.
    draft: str = rx.LocalStorage('', name='cobair_draft', sync=False)

    # context dialog
    context_dialog_open: bool = False
    context_dialog_index: int = -1
    context_dialog_name: str = ''
    context_dialog_rows: list[InstantiationView] = []
    context_dialog_error: str = ''

    # intention dialog
    intention_dialog_open: bool = False
    intention_dialog_index: int = -1
    intention_dialog_name: str = ''
    intention_dialog_error: str = ''

    # combined influence dialog
    combined_dialog_open: bool = False
    combined_intention: str = '0'
    combined_parts: list[CombinedPart] = []
    combined_value: str = '5'
    combined_error: str = ''

    # ------------------------------------------------------------------------------------------
    # config handling

    def _model(self) -> Config:
        """Return the config being edited.

        Returns:
            Config: The config.
        """
        if self._config is None:
            self._config = Config()
        return self._config

    def _context_key(self, index) -> object:
        """Return the context at a position.

        Args:
            index: The position (int or str).

        Returns:
            The context key.
        """
        return list(self._model().contexts)[int(index)]

    def _instantiation_key(self, context, index) -> object:
        """Return the instantiation of a context at a position.

        Args:
            context: The context key.
            index: The position (int or str).

        Returns:
            The instantiation key.
        """
        return list(self._model().contexts[context])[int(index)]

    def _intention_key(self, index) -> object:
        """Return the intention at a position.

        Args:
            index: The position (int or str).

        Returns:
            The intention key.
        """
        return list(self._model().intentions)[int(index)]

    def _set_config(self, config: Config, file_name: str = '', saved: bool = True) -> None:
        """Replace the config and clear the undo history.

        Args:
            config: The new config.
            file_name: Name of the file the config came from.
            saved: The config is saved (e.g. just loaded), else it counts as changed.
        """
        self._config = config
        self._saved = config.copy() if saved else None
        self._undo = []
        self._redo = []
        self.file_name = file_name
        self._sync()

    def _sync(self) -> None:
        """Derive the frontend vars from the config."""
        config = self._model()
        self.contexts = [
            ContextView(label(context), [InstantiationView(label(instantiation), label(apriori))
                                         for instantiation, apriori in instantiations.items()])
            for context, instantiations in config.contexts.items()]
        self.intentions = [label(intention) for intention in config.intentions]
        self.decision_threshold = label(config.decision_threshold)
        self.problems = config.validate()
        self.can_undo = bool(self._undo)
        self.can_redo = bool(self._redo)
        self.dirty = bool(self.local_file) and (self._saved is None or config != self._saved)
        self.draft = config.dumps() if config != Config() else ''
        self._sync_influences()
        self._sync_combined()

    def _sync_influences(self) -> None:
        """Derive the influence table of the selected context."""
        config = self._model()
        if not config.contexts:
            self.influence_context = '0'
            self.influence_rows = []
            return
        if int(self.influence_context) >= len(config.contexts):
            self.influence_context = '0'
        context = self._context_key(self.influence_context)
        self.influence_rows = [
            InfluenceRow(label(instantiation),
                         [str(influences.get(context, {}).get(instantiation, 0))
                          for influences in config.intentions.values()])
            for instantiation in config.contexts[context]]

    def _sync_combined(self) -> None:
        """Derive the list of combined influences."""
        self._combined_keys = []
        self.combined = []
        for intention, influences in self._model().intentions.items():
            for contexts, combinations in influences.items():
                if not isinstance(contexts, tuple):
                    continue
                for combination, value in combinations.items():
                    self._combined_keys.append((intention, contexts, combination))
                    text = ', '.join(f'{label(context)} = {label(instantiation)}'
                                     for context, instantiation in zip(contexts, combination))
                    self.combined.append(CombinedView(label(intention), text, str(value)))

    def _edit(self, method: str, *args) -> bool:
        """Apply an editing method of `Config` with undo support.

        Args:
            method: Name of the `Config` method.
            *args: Arguments of the method.

        Returns:
            bool: True if the change was applied, else `error` explains why.
        """
        before = self._model().copy()
        try:
            getattr(self._model(), method)(*args)
        except (ValueError, KeyError, IndexError) as error:
            self._config = before
            self.error = str(error).strip('"\'')
            self._sync()
            return False
        self.error = ''
        self.info = ''
        self._undo = [*self._undo, before][-MAX_UNDO:]
        self._redo = []
        self._sync()
        return True

    def _unload_guard(self):
        """Return the script that tells the page if leaving it would lose changes.

        Returns:
            The event setting `window.cobairDirty`.
        """
        return rx.call_script(f'window.cobairDirty = {str(self.dirty).lower()}')

    # ------------------------------------------------------------------------------------------
    # page and files

    @rx.event
    def on_load(self):
        """Open the file `cobair-web` was started with or restore the draft, once per session.

        Yields:
            The unload guard.
        """
        if self._initialized:
            return
        self._initialized = True
        local_file = os.environ.get(FILE_ENV, '')
        if local_file:
            self.local_file = local_file
            path = Path(local_file)
            if path.exists():
                self._load_text(path.read_text(encoding='utf-8'), path.name)
            else:
                self._set_config(Config(), path.name, saved=False)
                self.info = f'{path.name} does not exist yet, it is created on save.'
            return
        if self.draft:
            try:
                self._set_config(Config.loads(self.draft), saved=False)
                self.info = 'Your unsaved draft was restored.'
            except ValueError:
                self.draft = ''
        yield self._unload_guard()

    def _load_text(self, text: str, file_name: str) -> None:
        """Load a config from YAML text, keeping the current config if it fails.

        Args:
            text: The YAML text.
            file_name: The name of the file.
        """
        try:
            config = Config.loads(text)
        except Exception as error:  # pylint: disable=broad-exception-caught
            self.error = f'Could not load {file_name}: {error}'
            return
        self.error = ''
        self.info = ''
        self._set_config(config, file_name)

    @rx.event
    async def upload_config(self, files: list[rx.UploadFile]):
        """Load the uploaded YAML file.

        Args:
            files: The uploaded files, only the first one is used.

        Yields:
            The unload guard.
        """
        if not files:
            return
        upload = files[0]
        data = await upload.read()
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            self.error = f'Could not load {upload.filename}: not a text file'
            return
        self._load_text(text, upload.filename or 'config.yml')
        yield self._unload_guard()

    @rx.event
    def load_example(self):
        """Load the example config.

        Yields:
            The unload guard.
        """
        self._load_text(read_example(), EXAMPLE_FILE)
        yield self._unload_guard()

    @rx.event
    def new_config(self):
        """Start with an empty config.

        Yields:
            The unload guard.
        """
        self.error = ''
        self.info = ''
        self._set_config(Config())
        yield self._unload_guard()

    @rx.event
    def download_config(self):
        """Download the config as YAML file.

        This doesn't count as saving: the file `cobair-web` was started with is not changed.

        Returns:
            The download event.
        """
        text = self._model().dumps()
        file_name = self.file_name or 'cobair_config.yml'
        return rx.download(data=text, filename=file_name)

    @rx.event
    def save_config(self):
        """Save the config to the file `cobair-web` was started with.

        Yields:
            The unload guard.
        """
        if not self.local_file:
            self.error = 'Saving to disk is only possible when cobair-web was started with a file'
            return
        try:
            self._model().save(self.local_file)
        except OSError as error:
            self.error = f'Could not save {self.local_file}: {error}'
            return
        self._saved = self._model().copy()
        self.error = ''
        self.info = f'Saved {self.local_file}'
        self._sync()
        yield self._unload_guard()

    # ------------------------------------------------------------------------------------------
    # undo

    @rx.event
    def undo(self):
        """Undo the last change.

        Yields:
            The unload guard.
        """
        if not self._undo:
            return
        self._redo = [*self._redo, self._model().copy()]
        self._config = self._undo[-1]
        self._undo = self._undo[:-1]
        self.error = ''
        self._sync()
        yield self._unload_guard()

    @rx.event
    def redo(self):
        """Redo the last undone change.

        Yields:
            The unload guard.
        """
        if not self._redo:
            return
        self._undo = [*self._undo, self._model().copy()]
        self._config = self._redo[-1]
        self._redo = self._redo[:-1]
        self.error = ''
        self._sync()
        yield self._unload_guard()

    # ------------------------------------------------------------------------------------------
    # values

    @rx.event
    def set_apriori(self, context_index: int, instantiation_index: int, text: str):
        """Change an apriori probability.

        Args:
            context_index: Position of the context.
            instantiation_index: Position of the instantiation.
            text: The new value.

        Yields:
            The unload guard, or the old value for the input if the text is no probability.
        """
        context = self._context_key(context_index)
        instantiation = self._instantiation_key(context, instantiation_index)
        try:
            value = parse_probability(text)
        except ValueError as error:
            self.error = f'Apriori probability of {label(context)}.{label(instantiation)}: {error}'
            yield show_value(f'apriori-{context_index}-{instantiation_index}',
                             label(self._model().contexts[context][instantiation]))
            return
        if value != self._model().contexts[context][instantiation]:
            self._edit('change_context_apriori_value', context, instantiation, value)
        yield self._unload_guard()

    @rx.event
    def set_threshold(self, text: str):
        """Change the decision threshold.

        Args:
            text: The new value.

        Yields:
            The unload guard, or the old value for the input if the text is no probability.
        """
        try:
            value = parse_probability(text)
        except ValueError as error:
            self.error = f'Decision threshold: {error}'
            yield show_value('threshold', label(self._model().decision_threshold))
            return
        if value != self._model().decision_threshold:
            self._edit('change_decision_threshold', value)
        yield self._unload_guard()

    @rx.event
    def select_influence_context(self, index: str):
        """Show the influences of another context.

        Args:
            index: Position of the context.
        """
        self.influence_context = index
        self._sync_influences()

    @rx.event
    def set_influence(self, instantiation_index: int, intention_index: int, value: str):
        """Change the influence of an instantiation of the selected context on an intention.

        Args:
            instantiation_index: Position of the instantiation.
            intention_index: Position of the intention.
            value: The new influence value as text.

        Yields:
            The unload guard.
        """
        context = self._context_key(self.influence_context)
        instantiation = self._instantiation_key(context, instantiation_index)
        intention = self._intention_key(intention_index)
        self._edit('change_influence_value', intention, context, instantiation, int(value))
        yield self._unload_guard()

    # ------------------------------------------------------------------------------------------
    # context dialog

    @rx.event
    def open_new_context(self):
        """Open the dialog for a new context."""
        self.context_dialog_index = -1
        self.context_dialog_name = ''
        self.context_dialog_rows = [InstantiationView('', '0.5'), InstantiationView('', '0.5')]
        self.context_dialog_error = ''
        self.context_dialog_open = True

    @rx.event
    def open_edit_context(self, index: int):
        """Open the dialog to edit a context.

        Args:
            index: Position of the context.
        """
        view = self.contexts[int(index)]
        self.context_dialog_index = int(index)
        self.context_dialog_name = view.name
        self.context_dialog_rows = [InstantiationView(row.name, row.apriori)
                                    for row in view.instantiations]
        self.context_dialog_error = ''
        self.context_dialog_open = True

    @rx.event
    def set_context_dialog_open(self, is_open: bool):
        """Open or close the context dialog.

        Args:
            is_open: True to open.
        """
        self.context_dialog_open = is_open

    @rx.event
    def set_context_dialog_name(self, name: str):
        """Change the name in the context dialog.

        Args:
            name: The name.
        """
        self.context_dialog_name = name

    @rx.event
    def set_context_row_name(self, index: int, name: str):
        """Change the name of an instantiation in the context dialog.

        Args:
            index: Position of the row.
            name: The name.
        """
        rows = list(self.context_dialog_rows)
        rows[int(index)] = InstantiationView(name, rows[int(index)].apriori)
        self.context_dialog_rows = rows

    @rx.event
    def set_context_row_apriori(self, index: int, apriori: str):
        """Change the apriori probability of an instantiation in the context dialog.

        Args:
            index: Position of the row.
            apriori: The apriori probability.
        """
        rows = list(self.context_dialog_rows)
        rows[int(index)] = InstantiationView(rows[int(index)].name, apriori)
        self.context_dialog_rows = rows

    @rx.event
    def add_context_row(self):
        """Add an instantiation to the context dialog."""
        self.context_dialog_rows = [*self.context_dialog_rows, InstantiationView('', '0')]

    @rx.event
    def remove_context_row(self, index: int):
        """Remove an instantiation from the context dialog.

        Args:
            index: Position of the row.
        """
        rows = list(self.context_dialog_rows)
        del rows[int(index)]
        self.context_dialog_rows = rows

    def _dialog_instantiations(self, context) -> dict:
        """Read the instantiations of the context dialog.

        Instantiations keep their original key (e.g. the bool `True`) if their label is unchanged,
        new or renamed ones are strings.

        Args:
            context: The edited context or None for a new one.

        Returns:
            dict: `{instantiation: apriori}`

        Raises:
            ValueError: If a name is empty or used twice or an apriori value is no number.
        """
        originals = {} if context is None else {
            label(instantiation): instantiation
            for instantiation in self._model().contexts[context]}
        instantiations = {}
        for row in self.context_dialog_rows:
            name = row.name.strip()
            if not name:
                raise ValueError('Instantiations need a name')
            key = originals.get(name, name)
            if key in instantiations:
                raise ValueError(f'Instantiation "{name}" is used twice')
            instantiations[key] = parse_probability(row.apriori)
        if not instantiations:
            raise ValueError('At least one instantiation is required')
        return instantiations

    @rx.event
    def save_context_dialog(self):
        """Add or change the context of the dialog.

        Yields:
            The unload guard.
        """
        name = self.context_dialog_name.strip()
        if not name:
            self.context_dialog_error = 'The context needs a name'
            return
        editing = self.context_dialog_index >= 0
        context = self._context_key(self.context_dialog_index) if editing else None
        try:
            instantiations = self._dialog_instantiations(context)
        except ValueError as error:
            self.context_dialog_error = str(error)
            return
        if editing:
            new_name = context if label(context) == name else name
            applied = self._edit('edit_context', context, instantiations, new_name)
        else:
            applied = self._edit('add_context', name, instantiations)
        if not applied:
            self.context_dialog_error = self.error
            self.error = ''
            return
        self.context_dialog_open = False
        yield self._unload_guard()

    @rx.event
    def delete_context(self, index: int):
        """Delete a context.

        Args:
            index: Position of the context.

        Yields:
            The unload guard.
        """
        self._edit('del_context', self._context_key(index))
        yield self._unload_guard()

    # ------------------------------------------------------------------------------------------
    # intention dialog

    @rx.event
    def open_new_intention(self):
        """Open the dialog for a new intention."""
        self.intention_dialog_index = -1
        self.intention_dialog_name = ''
        self.intention_dialog_error = ''
        self.intention_dialog_open = True

    @rx.event
    def open_rename_intention(self, index: int):
        """Open the dialog to rename an intention.

        Args:
            index: Position of the intention.
        """
        self.intention_dialog_index = int(index)
        self.intention_dialog_name = self.intentions[int(index)]
        self.intention_dialog_error = ''
        self.intention_dialog_open = True

    @rx.event
    def set_intention_dialog_open(self, is_open: bool):
        """Open or close the intention dialog.

        Args:
            is_open: True to open.
        """
        self.intention_dialog_open = is_open

    @rx.event
    def set_intention_dialog_name(self, name: str):
        """Change the name in the intention dialog.

        Args:
            name: The name.
        """
        self.intention_dialog_name = name

    @rx.event
    def save_intention_dialog(self):
        """Add or rename the intention of the dialog.

        Yields:
            The unload guard.
        """
        name = self.intention_dialog_name.strip()
        if not name:
            self.intention_dialog_error = 'The intention needs a name'
            return
        if self.intention_dialog_index >= 0:
            intention = self._intention_key(self.intention_dialog_index)
            applied = label(intention) == name or self._edit('edit_intention', intention, name)
        else:
            applied = self._edit('add_intention', name)
        if not applied:
            self.intention_dialog_error = self.error
            self.error = ''
            return
        self.intention_dialog_open = False
        yield self._unload_guard()

    @rx.event
    def delete_intention(self, index: int):
        """Delete an intention.

        Args:
            index: Position of the intention.

        Yields:
            The unload guard.
        """
        self._edit('del_intention', self._intention_key(index))
        yield self._unload_guard()

    # ------------------------------------------------------------------------------------------
    # combined influences

    @rx.event
    def open_combined_dialog(self):
        """Open the dialog for a new combined influence."""
        if not self.intentions or len(self.contexts) < 2:
            self.error = 'Combined influences need an intention and at least two contexts'
            return
        self.combined_intention = '0'
        self.combined_parts = [CombinedPart('0', '0'), CombinedPart('1', '0')]
        self.combined_value = '5'
        self.combined_error = ''
        self.combined_dialog_open = True

    @rx.event
    def set_combined_dialog_open(self, is_open: bool):
        """Open or close the combined influence dialog.

        Args:
            is_open: True to open.
        """
        self.combined_dialog_open = is_open

    @rx.event
    def set_combined_intention(self, index: str):
        """Choose the intention of the combined influence.

        Args:
            index: Position of the intention.
        """
        self.combined_intention = index

    @rx.event
    def set_combined_value(self, value: str):
        """Choose the value of the combined influence.

        Args:
            value: The influence value as text.
        """
        self.combined_value = value

    @rx.event
    def set_combined_part_context(self, index: int, context_index: str):
        """Choose the context of a part of the combination.

        Args:
            index: Position of the part.
            context_index: Position of the context.
        """
        parts = list(self.combined_parts)
        parts[int(index)] = CombinedPart(context_index, '0')
        self.combined_parts = parts

    @rx.event
    def set_combined_part_instantiation(self, index: int, instantiation_index: str):
        """Choose the instantiation of a part of the combination.

        Args:
            index: Position of the part.
            instantiation_index: Position of the instantiation.
        """
        parts = list(self.combined_parts)
        parts[int(index)] = CombinedPart(parts[int(index)].context, instantiation_index)
        self.combined_parts = parts

    @rx.event
    def add_combined_part(self):
        """Add another context to the combination."""
        used = {part.context for part in self.combined_parts}
        free = [str(index) for index in range(len(self.contexts)) if str(index) not in used]
        if free:
            self.combined_parts = [*self.combined_parts, CombinedPart(free[0], '0')]

    @rx.event
    def remove_combined_part(self, index: int):
        """Remove a context from the combination.

        Args:
            index: Position of the part.
        """
        parts = list(self.combined_parts)
        del parts[int(index)]
        self.combined_parts = parts

    @rx.event
    def save_combined_dialog(self):
        """Add the combined influence of the dialog.

        Yields:
            The unload guard.
        """
        if len(self.combined_parts) < 2:
            self.combined_error = 'Combine at least two contexts'
            return
        if len({part.context for part in self.combined_parts}) < len(self.combined_parts):
            self.combined_error = 'Every context can only be used once'
            return
        contexts = tuple(self._context_key(part.context) for part in self.combined_parts)
        instantiations = tuple(self._instantiation_key(context, part.instantiation)
                               for context, part in zip(contexts, self.combined_parts))
        if not self._edit('add_combined_influence', self._intention_key(self.combined_intention),
                          contexts, instantiations, int(self.combined_value)):
            self.combined_error = self.error
            self.error = ''
            return
        self.combined_dialog_open = False
        yield self._unload_guard()

    @rx.event
    def remove_combined(self, index: int):
        """Remove a combined influence.

        Args:
            index: Position in the list of combined influences.

        Yields:
            The unload guard.
        """
        intention, contexts, combination = self._combined_keys[int(index)]
        self._edit('del_combined_influence', intention, contexts, combination)
        yield self._unload_guard()
