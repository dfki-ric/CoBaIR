"""End-to-end tests: the real `cobair-web` in a headless browser."""

# System imports

# 3rd party imports

# local imports

# end file header
__author__ = 'Adrian Lubitz'


def test_load_example(page):
    """The example shows its contexts, intentions and that it is valid."""
    page.click('#load-example')
    page.wait_for_selector('#valid')
    assert page.locator('.context-card').count() == 3
    assert page.locator('.intention-card').count() == 2
    assert page.text_content('#file-name') == 'small_example.yml'


def test_upload_yaml(page, tmp_path):
    """An uploaded file is loaded, problems are shown."""
    config = tmp_path / 'upload.yml'
    config.write_text('contexts:\n  weather:\n    sunny: 0.7\n    rainy: 0.2\n'
                      'intentions:\n  take umbrella: {}\n', encoding='utf-8')
    page.set_input_files('#config_upload input[type=file]', str(config))
    page.wait_for_selector('#problems')
    assert page.text_content('#file-name') == 'upload.yml'
    assert 'For "weather" it is 0.8999999999999999' in page.text_content('#problems')
    assert page.locator('.context-card').count() == 1


def test_upload_broken_file(page, tmp_path):
    """A broken file shows an error and keeps the loaded config."""
    page.click('#load-example')
    page.wait_for_selector('#valid')
    broken = tmp_path / 'broken.yml'
    broken.write_text('- not\n- a config\n', encoding='utf-8')
    page.set_input_files('#config_upload input[type=file]', str(broken))
    page.wait_for_selector('#error')
    assert 'Could not load broken.yml' in page.text_content('#error')
    assert page.locator('.context-card').count() == 3


def test_new(page):
    """New clears the editor."""
    page.click('#load-example')
    page.wait_for_selector('.context-card')
    page.click('#new-config')
    page.wait_for_selector('#problems')
    assert page.locator('.context-card').count() == 0
    assert 'No contexts defined' in page.text_content('#problems')
