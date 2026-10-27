"""State of the CoBaIR web GUI.

The config is kept as `cobair.model.Config` in a backend-only var (its tuple keys can't be sent to
the browser). After every change `_sync()` derives the plain vars the frontend renders.
"""

# System imports
from __future__ import annotations

import dataclasses
from importlib import resources

# 3rd party imports
import reflex as rx

# local imports
from ..model import Config

# end file header
__author__ = 'Adrian Lubitz'

EXAMPLE_FILE = 'small_example.yml'


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


class EditorState(rx.State):
    """The config being edited and everything the editor shows of it."""

    # backend only: the config itself
    _config: Config | None = None

    #: Name of the loaded or last saved file.
    file_name: str = ''
    #: The contexts with their instantiations and apriori probabilities.
    contexts: list[ContextView] = []
    #: Names of the intentions.
    intentions: list[str] = []
    #: Problems of the config, empty if valid.
    problems: list[str] = []
    #: Error of the last action (e.g. a file that could not be loaded).
    error: str = ''

    def _model(self) -> Config:
        """Return the config being edited.

        Returns:
            Config: The config.
        """
        if self._config is None:
            self._config = Config()
        return self._config

    def _set_config(self, config: Config, file_name: str = '') -> None:
        """Replace the config.

        Args:
            config: The new config.
            file_name: Name of the file the config came from.
        """
        self._config = config
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
        self.problems = config.validate()

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
        self._set_config(config, file_name)

    @rx.event
    async def upload_config(self, files: list[rx.UploadFile]):
        """Load the uploaded YAML file.

        Args:
            files: The uploaded files, only the first one is used.
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

    @rx.event
    def load_example(self):
        """Load the example config."""
        self._load_text(read_example(), EXAMPLE_FILE)

    @rx.event
    def new_config(self):
        """Start with an empty config."""
        self.error = ''
        self._set_config(Config())
