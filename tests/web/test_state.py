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


def run(coroutine):
    """Run a coroutine in its own thread (sync Playwright may own this thread's event loop).

    Args:
        coroutine: The coroutine.

    Returns:
        The result of the coroutine.
    """
    with ThreadPoolExecutor(1) as executor:
        return executor.submit(asyncio.run, coroutine).result()


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
    EditorState.load_example.fn(state)
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
    EditorState.load_example.fn(state)
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
    EditorState.load_example.fn(state)
    EditorState.new_config.fn(state)
    assert state.contexts == []
    assert state.file_name == ''
    assert 'No contexts defined' in state.problems
