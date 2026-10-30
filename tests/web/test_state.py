"""Unit tests for the state of the web GUI, the event handlers are called directly."""

# System imports
import asyncio
from concurrent.futures import ThreadPoolExecutor

# 3rd party imports
import pytest

pytest.importorskip('reflex')

# local imports
from cobair.model import Config  # noqa: E402
from cobair.web.state import EditorState, read_example  # noqa: E402

# end file header
__author__ = 'Adrian Lubitz'


def run(generator):
    """Run an async generator to the end in its own thread.

    Sync Playwright may own the event loop of this thread.

    Args:
        generator: The async generator of an event handler.

    Returns:
        list: The yielded events.
    """
    async def collect():
        return [event async for event in generator]
    with ThreadPoolExecutor(1) as executor:
        return executor.submit(asyncio.run, collect()).result()


class FakeUpload:
    """Stands in for `rx.UploadFile`."""

    def __init__(self, data: bytes, filename: str) -> None:
        """Keep the content.

        Args:
            data: The file content.
            filename: The file name.
        """
        self.data = data
        self.filename = filename

    async def read(self) -> bytes:
        """Return the content.

        Returns:
            bytes: The content.
        """
        return self.data


@pytest.fixture
def state():
    """A fresh editor state.

    Returns:
        EditorState: The state.
    """
    return EditorState(_reflex_internal_init=True)


def test_initial_state(state):
    """The editor starts empty."""
    assert state.contexts == []
    assert state.intentions == []
    assert state.file_name == ''


def test_load_example(state):
    """The example fills contexts, intentions and has no problems."""
    call(EditorState.load_example, state)
    assert [context.name for context in state.contexts] == [
        'human activity', 'human holding object', 'speech commands']
    holding = state.contexts[1]
    assert [(i.name, i.apriori) for i in holding.instantiations] == [('False', '0.6'),
                                                                     ('True', '0.4')]
    assert state.intentions == ['hand over tool', 'pick up tool']
    assert state.problems == []
    assert state.file_name == 'small_example.yml'
    assert state._model() == Config.loads(read_example())  # pylint: disable=protected-access


def test_upload(state):
    """An uploaded YAML file is loaded."""
    text = 'contexts:\n  a:\n    x: 0.5\n    y: 0.5\nintentions:\n  i: {}\n'
    run(EditorState.upload_config.fn(state, [FakeUpload(text.encode(), 'mine.yml')]))
    assert state.file_name == 'mine.yml'
    assert [context.name for context in state.contexts] == ['a']
    assert state.intentions == ['i']
    assert state.error == ''


@pytest.mark.parametrize('data, message', [
    (b'\xff\xfe\x00', 'not a text file'),
    (b'- just\n- a list\n', 'mapping'),
    (b'contexts: [unclosed', 'Could not load'),
])
def test_upload_invalid_keeps_config(state, data, message):
    """A broken file shows an error and keeps the current config."""
    call(EditorState.load_example, state)
    run(EditorState.upload_config.fn(state, [FakeUpload(data, 'broken.yml')]))
    assert message in state.error
    assert state.file_name == 'small_example.yml'
    assert len(state.contexts) == 3


def test_upload_nothing(state):
    """An empty upload does nothing."""
    run(EditorState.upload_config.fn(state, []))
    assert state.error == ''


def test_new_config(state):
    """New starts with an empty, invalid config."""
    call(EditorState.load_example, state)
    call(EditorState.new_config, state)
    assert state.contexts == []
    assert state.file_name == ''
    assert 'No contexts defined' in state.problems


def call(handler, state, *args):
    """Call an event handler directly and run it to the end.

    Args:
        handler: The event handler of `EditorState`.
        state: The state.
        *args: Arguments of the handler.

    Returns:
        The events returned or yielded by the handler.
    """
    result = handler.fn(state, *args)
    if hasattr(result, '__next__'):
        return list(result)
    return result


@pytest.fixture
def example(state):
    """The state with the example loaded.

    Returns:
        EditorState: The state.
    """
    call(EditorState.load_example, state)
    return state


def model(state) -> Config:
    """Return the config of the state.

    Args:
        state: The state.

    Returns:
        Config: The config.
    """
    return state._model()  # pylint: disable=protected-access


def test_set_apriori_and_undo_redo(example):
    """Apriori values change the config, undo/redo restore it."""
    call(EditorState.set_apriori, example, 2, 0, '0,3')  # speech commands.handover
    assert model(example).contexts['speech commands']['handover'] == 0.3
    assert example.can_undo and not example.can_redo
    assert any('speech commands' in problem for problem in example.problems)
    call(EditorState.undo, example)
    assert model(example) == Config.loads(read_example())
    assert not example.can_undo and example.can_redo
    call(EditorState.redo, example)
    assert model(example).contexts['speech commands']['handover'] == 0.3


def test_set_apriori_invalid(example):
    """Text that is no number shows an error and changes nothing."""
    events = call(EditorState.set_apriori, example, 0, 0, 'abc')
    assert 'is not a number' in example.error
    assert model(example) == Config.loads(read_example())
    assert len(events) == 1  # the input shows the old value again
    assert not example.can_undo


def test_unchanged_value_adds_no_undo_step(example):
    """Leaving an input without change doesn't create an undo step."""
    call(EditorState.set_apriori, example, 0, 0, '0.2')
    call(EditorState.set_threshold, example, '0.8')
    assert not example.can_undo


def test_threshold(example):
    """The decision threshold can be changed and is validated."""
    call(EditorState.set_threshold, example, '0.5')
    assert model(example).decision_threshold == 0.5
    call(EditorState.set_threshold, example, '1.5')
    assert 'Decision threshold must be a number between 0 and 1' in example.problems


def test_influence_table(example):
    """The influence table shows the selected context and changes values."""
    assert [row.name for row in example.influence_rows] == ['idle', 'working']
    assert example.influence_rows[0].influences == ['4', '2']
    call(EditorState.select_influence_context, example, '1')
    assert [row.name for row in example.influence_rows] == ['False', 'True']
    call(EditorState.set_influence, example, 1, 1, '5')  # True on pick up tool
    assert model(example).intentions['pick up tool']['human holding object'][True] == 5
    assert example.influence_rows[1].influences == ['1', '5']


def test_new_context_dialog(example):
    """A context is added from the dialog."""
    call(EditorState.open_new_context, example)
    assert example.context_dialog_open
    call(EditorState.set_context_dialog_name, example, 'weather')
    call(EditorState.set_context_row_name, example, 0, 'sunny')
    call(EditorState.set_context_row_name, example, 1, 'rainy')
    call(EditorState.add_context_row, example)
    call(EditorState.set_context_row_name, example, 2, 'snowy')
    call(EditorState.set_context_row_apriori, example, 0, '0.4')
    call(EditorState.set_context_row_apriori, example, 2, '0.1')
    call(EditorState.save_context_dialog, example)
    assert not example.context_dialog_open
    assert model(example).contexts['weather'] == {'sunny': 0.4, 'rainy': 0.5, 'snowy': 0.1}
    assert model(example).intentions['pick up tool']['weather'] == {
        'sunny': 0, 'rainy': 0, 'snowy': 0}


@pytest.mark.parametrize('name, rows, message', [
    ('', [('a', '1')], 'needs a name'),
    ('weather', [('', '1')], 'need a name'),
    ('weather', [('a', '0.5'), ('a', '0.5')], 'used twice'),
    ('weather', [('a', 'x')], 'not a number'),
    ('weather', [], 'At least one'),
    ('speech commands', [('a', '1')], 'existing context'),
])
def test_new_context_dialog_errors(example, name, rows, message):
    """Invalid input keeps the dialog open with an error."""
    call(EditorState.open_new_context, example)
    call(EditorState.set_context_dialog_name, example, name)
    for _ in range(2):
        call(EditorState.remove_context_row, example, 0)
    for index, (row_name, apriori) in enumerate(rows):
        call(EditorState.add_context_row, example)
        call(EditorState.set_context_row_name, example, index, row_name)
        call(EditorState.set_context_row_apriori, example, index, apriori)
    call(EditorState.save_context_dialog, example)
    assert example.context_dialog_open
    assert message in example.context_dialog_error
    assert model(example) == Config.loads(read_example())


def test_edit_context_keeps_bool_instantiations(example):
    """Unchanged labels keep their original keys, e.g. the bools True / False."""
    call(EditorState.open_edit_context, example, 1)
    assert example.context_dialog_name == 'human holding object'
    call(EditorState.set_context_dialog_name, example, 'holding')
    call(EditorState.set_context_row_apriori, example, 0, '0.5')
    call(EditorState.set_context_row_apriori, example, 1, '0.5')
    call(EditorState.save_context_dialog, example)
    config = model(example)
    assert config.contexts['holding'] == {False: 0.5, True: 0.5}
    assert config.intentions['hand over tool']['holding'] == {False: 4, True: 1}


def test_delete_context(example):
    """A context and its combined influences are deleted."""
    call(EditorState.delete_context, example, 0)  # human activity
    assert [context.name for context in example.contexts] == ['human holding object',
                                                              'speech commands']
    assert example.combined == []


def test_intention_dialog(example):
    """Intentions are added, renamed and deleted."""
    call(EditorState.open_new_intention, example)
    call(EditorState.set_intention_dialog_name, example, 'fetch tool')
    call(EditorState.save_intention_dialog, example)
    assert example.intentions == ['hand over tool', 'pick up tool', 'fetch tool']
    call(EditorState.open_rename_intention, example, 2)
    call(EditorState.set_intention_dialog_name, example, 'pick up tool')
    call(EditorState.save_intention_dialog, example)
    assert example.intention_dialog_open
    assert 'exists' in example.intention_dialog_error
    call(EditorState.set_intention_dialog_name, example, 'bring tool')
    call(EditorState.save_intention_dialog, example)
    assert example.intentions == ['hand over tool', 'pick up tool', 'bring tool']
    call(EditorState.delete_intention, example, 0)
    assert example.intentions == ['pick up tool', 'bring tool']


def test_combined_dialog(example):
    """A combined influence is added from the dialog and removed again."""
    call(EditorState.open_combined_dialog, example)
    assert [(part.context, part.instantiation) for part in example.combined_parts] == [
        ('0', '0'), ('1', '0')]
    call(EditorState.set_combined_intention, example, '0')
    call(EditorState.set_combined_part_instantiation, example, 1, '1')  # holding = True
    call(EditorState.add_combined_part, example)
    call(EditorState.set_combined_part_instantiation, example, 2, '1')  # speech = other
    call(EditorState.set_combined_value, example, '2')
    call(EditorState.save_combined_dialog, example)
    assert not example.combined_dialog_open
    combined = model(example).combined_influences('hand over tool')
    assert combined == {('human activity', 'human holding object', 'speech commands'): {
        ('idle', True, 'other'): 2}}
    assert [view.combination for view in example.combined] == [
        'human activity = idle, human holding object = True, speech commands = other',
        'speech commands = pickup, human activity = working']
    call(EditorState.remove_combined, example, 0)
    assert len(example.combined) == 1


def test_combined_dialog_errors(example):
    """A context can only be used once and two contexts are needed."""
    call(EditorState.open_combined_dialog, example)
    call(EditorState.set_combined_part_context, example, 1, '0')
    call(EditorState.save_combined_dialog, example)
    assert 'only be used once' in example.combined_error
    call(EditorState.remove_combined_part, example, 1)
    call(EditorState.save_combined_dialog, example)
    assert 'at least two' in example.combined_error
    call(EditorState.set_combined_dialog_open, example, False)
    call(EditorState.new_config, example)
    call(EditorState.open_combined_dialog, example)
    assert not example.combined_dialog_open
    assert 'at least two contexts' in example.error


def test_no_unsaved_changes_without_file(example):
    """Without a file nothing is saved to disk, so there are no unsaved changes to warn about."""
    call(EditorState.set_threshold, example, '0.5')
    assert not example.dirty
    assert call(EditorState.download_config, example)


def test_draft_is_autosaved_and_restored(state):
    """Every change updates the draft, a new session restores it."""
    call(EditorState.load_example, state)
    call(EditorState.set_threshold, state, '0.6')
    assert Config.loads(state.draft).decision_threshold == 0.6
    restored = EditorState(_reflex_internal_init=True)
    restored.draft = state.draft
    call(EditorState.on_load, restored)
    assert model(restored).decision_threshold == 0.6
    assert 'draft was restored' in restored.info
    call(EditorState.on_load, restored)  # only once per session
    assert restored.info


def test_local_file(state, tmp_path, monkeypatch):
    """With a file, cobair-web opens it and saves to it."""
    path = tmp_path / 'mine.yml'
    path.write_text(read_example(), encoding='utf-8')
    monkeypatch.setenv('COBAIR_WEB_FILE', str(path))
    call(EditorState.on_load, state)
    assert state.local_file == str(path)
    assert state.file_name == 'mine.yml'
    assert not state.dirty
    call(EditorState.set_threshold, state, '0.3')
    assert state.dirty
    call(EditorState.download_config, state)
    assert state.dirty  # the file is not changed by a download
    call(EditorState.save_config, state)
    assert not state.dirty
    assert Config.load(path).decision_threshold == 0.3


def test_local_file_missing(state, tmp_path, monkeypatch):
    """A file that doesn't exist yet is created on save."""
    path = tmp_path / 'new.yml'
    monkeypatch.setenv('COBAIR_WEB_FILE', str(path))
    call(EditorState.on_load, state)
    assert 'created on save' in state.info
    call(EditorState.save_config, state)
    assert Config.load(path) == Config()


def test_save_without_file(example):
    """Without a file only download is possible."""
    call(EditorState.save_config, example)
    assert 'only possible' in example.error
