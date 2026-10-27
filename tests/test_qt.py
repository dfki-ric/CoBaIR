"""Smoke tests for the Qt configurator, run headless with the offscreen platform."""

# System imports
import os
import warnings

# 3rd party imports
import pytest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
pytest.importorskip('PyQt5')
pytest.importorskip('pyqtgraph')

# local imports
from cobair.model import Config  # noqa: E402
from cobair.qt import Configurator, main  # noqa: E402
from cobair.qt.configurator import NewIntentionDialog  # noqa: E402

# end file header
__author__ = 'Adrian Lubitz'

SPEECH = 'speech commands'
ACTIVITY = 'human activity'
PICK = 'pick up tool'


@pytest.fixture
def configurator():
    """A configurator with the small example loaded.

    Yields:
        Configurator: The configurator.
    """
    window = Configurator(file='small_example.yml')
    yield window
    window.original_config = window.config.copy()  # no "unsaved changes" dialog on close
    window.close()


def test_load_file(configurator):
    """Loading a file fills the dropdowns, the advanced table and the title."""
    assert configurator.config == Config.load('small_example.yml')
    assert configurator.context_selection.count() == 3
    assert configurator.intention_dropdown.count() == 2
    assert configurator.windowTitle() == 'CoBaIR - small_example.yml '
    assert configurator.error_label.text() == ''


@pytest.mark.parametrize('config', [Config.load('small_example.yml'),
                                    Config.load('small_example.yml').to_dict()])
def test_config_argument(config):
    """The config can be given as Config or dict, like in 4.x."""
    window = Configurator(config=config)
    assert window.config == Config.load('small_example.yml')
    assert window.windowTitle() == 'CoBaIR - New Configuration'
    window.close()


def test_edit_marks_title_and_saves(configurator, tmp_path):
    """Edits mark the title as modified and are written on save."""
    configurator.decision_threshold_entry.setText('0.5')
    assert configurator.config.decision_threshold == 0.5
    assert configurator.windowTitle().endswith('*')
    configurator.current_file_name = tmp_path / 'saved.yml'
    configurator.save()
    assert Config.load(tmp_path / 'saved.yml') == configurator.config
    assert not configurator.windowTitle().endswith('*')


def test_invalid_input_shows_warning(configurator):
    """Problems of the config are shown in the error label."""
    with warnings.catch_warnings():
        warnings.simplefilter('always')
        configurator.decision_threshold_entry.setText('2')
    assert configurator.error_label.text() == 'Decision threshold must be a number between 0 and 1'
    configurator.decision_threshold_entry.setText('abc')
    assert configurator.error_label.text() == 'Decision Threshold must be a number'


def test_apriori_and_influence_widgets(configurator):
    """The line edits and sliders change the config."""
    configurator.context_selection.setCurrentText(SPEECH)
    _, line_edit = configurator.context_instantiations[SPEECH]['pickup']
    line_edit.setText('0.3')
    assert configurator.config.contexts[SPEECH]['pickup'] == 0.3

    configurator.intention_dropdown.setCurrentText(PICK)
    configurator.influencing_context_selection.setCurrentText(SPEECH)
    widgets = configurator.intention_instantiations[PICK][SPEECH]['other']
    slider, slider_label = widgets[2], widgets[4]
    slider.setValue(1)
    assert configurator.config.intentions[PICK][SPEECH]['other'] == 1
    assert slider_label.text() == 'very low'


def test_new_intention_dialog(configurator, monkeypatch):
    """A new intention from the dialog is added and selected."""
    def fill_and_ok(dialog):
        """Fill the dialog and press OK instead of showing it."""
        dialog.intention_entry.setText('fetch tool')
        dialog.ok_button.click()
    monkeypatch.setattr(NewIntentionDialog, 'exec_', fill_and_ok)
    configurator.new_intention()
    assert 'fetch tool' in configurator.config.intentions
    assert configurator.intention_dropdown.currentText() == 'fetch tool'


def test_context_edits(configurator):
    """Context edits through the window keep combined influences (#191)."""
    configurator.context_selection.setCurrentText(SPEECH)
    configurator._edit('edit_context', SPEECH, configurator.config.contexts[SPEECH], 'speech')
    configurator.create_fields()
    assert configurator.context_selection.findText('speech') >= 0
    assert ('speech', ACTIVITY) in configurator.config.intentions[PICK]
    configurator.context_selection.setCurrentText(ACTIVITY)
    configurator.delete_context()
    assert ACTIVITY not in configurator.config.contexts
    assert configurator.context_selection.count() == 2


def test_advanced_table_shows_every_combination(configurator):
    """Every combination gets its own row with its own value and remove button."""
    configurator._edit('add_combined_influence', PICK, (SPEECH, ACTIVITY), ('other', 'idle'), 2)
    configurator.fill_advanced_table()
    labels = [widget.text() for widget in configurator.advanced_table.findChildren(
        type(configurator.error_label))]
    assert 'speech commands=pickup, human activity=working' in labels
    assert 'speech commands=other, human activity=idle' in labels
    assert '5' in labels and '2' in labels
    configurator.remove_combined_influence(PICK, (SPEECH, ACTIVITY), ('pickup', 'working'))
    assert configurator.config.combined_influences(PICK) == {
        (SPEECH, ACTIVITY): {('other', 'idle'): 2}}


def test_reset(configurator):
    """New starts with an empty config."""
    configurator.reset()
    assert configurator.config == Config()
    assert configurator.windowTitle() == 'CoBaIR - New Configuration'


def test_main_parses_file(monkeypatch):
    """`cobair-qt -f file` opens the file."""
    windows = []

    def exec_and_record(app):
        """Record the windows instead of running the event loop.

        Returns:
            int: Exit code 0.
        """
        windows.extend(widget for widget in app.topLevelWidgets()
                       if isinstance(widget, Configurator))
        return 0
    from PyQt5 import QtWidgets  # pylint: disable=import-outside-toplevel
    monkeypatch.setattr(QtWidgets.QApplication, 'exec_', exec_and_record)
    assert main(['-f', 'small_example.yml']) == 0
    assert any(window.config == Config.load('small_example.yml') for window in windows)
    for window in windows:
        window.close()


def test_deprecated_module_alias():
    """`cobair.configurator` still works with a DeprecationWarning."""
    import importlib  # pylint: disable=import-outside-toplevel
    import sys  # pylint: disable=import-outside-toplevel
    sys.modules.pop('cobair.configurator', None)
    with pytest.warns(DeprecationWarning, match='cobair.qt.configurator'):
        module = importlib.import_module('cobair.configurator')
    assert module.Configurator is Configurator
