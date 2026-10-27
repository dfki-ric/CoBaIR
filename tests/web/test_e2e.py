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


def load_example(page):
    """Load the example and wait for it.

    Args:
        page: The page.
    """
    page.click('#load-example')
    page.wait_for_selector('#valid')


def field(page, selector: str):
    """Return the input element of a text field, whether the selector hits the input or its root.

    Args:
        page: The page.
        selector: CSS selector of the field.

    Returns:
        The locator of the input elements.
    """
    return page.locator(f'input{selector}, {selector} input')


def choose(page, trigger, option: str):
    """Choose an option of a select.

    Args:
        page: The page.
        trigger: Locator of the select trigger.
        option: Text of the option.
    """
    trigger.click()
    page.get_by_role('option', name=option).click()


def test_context_dialog(page):
    """A context is added, renamed and deleted (manual protocol: New/Edit/Delete Context)."""
    load_example(page)
    page.click('#add-context')
    page.fill('#context-name', 'weather')
    names = field(page, '.instantiation-name')
    names.nth(0).fill('sunny')
    names.nth(1).fill('rainy')
    page.click('#save-context')
    page.wait_for_selector('.context-name:text-is("weather")')
    assert page.locator('.context-card').count() == 4

    page.locator('.edit-context').nth(3).click()
    page.fill('#context-name', 'speech commands')
    page.click('#save-context')
    assert 'exists already' in page.text_content('#context-dialog-error')
    page.fill('#context-name', 'sky')
    page.click('#save-context')
    page.wait_for_selector('.context-name:text-is("sky")')

    page.locator('.delete-context').nth(3).click()
    page.wait_for_function("document.querySelectorAll('.context-card').length === 3")


def test_empty_context_name(page):
    """An empty context name shows an error (manual protocol)."""
    page.click('#add-context')
    page.click('#save-context')
    assert 'needs a name' in page.text_content('#context-dialog-error')


def test_intention_dialog(page):
    """An intention is added, renamed and deleted (manual protocol)."""
    load_example(page)
    page.click('#add-intention')
    page.fill('#intention-name', 'fetch tool')
    page.click('#save-intention')
    page.wait_for_selector('.intention-name:text-is("fetch tool")')
    page.locator('.rename-intention').nth(2).click()
    page.fill('#intention-name', 'bring tool')
    page.click('#save-intention')
    page.wait_for_selector('.intention-name:text-is("bring tool")')
    page.locator('.delete-intention').nth(2).click()
    page.wait_for_function("document.querySelectorAll('.intention-card').length === 2")


def test_apriori_undo_redo(page):
    """Editing an apriori value shows the problem, undo and redo work."""
    load_example(page)
    apriori = field(page, '.apriori-input').first
    apriori.fill('0.5')
    apriori.blur()
    page.wait_for_selector('#problems')
    assert 'human activity' in page.text_content('#problems')
    assert page.evaluate('window.cobairDirty') is True
    page.click('#undo')
    page.wait_for_selector('#valid')
    assert field(page, '.apriori-input').first.input_value() == '0.2'
    page.click('#redo')
    page.wait_for_selector('#problems')
    assert field(page, '.apriori-input').first.input_value() == '0.5'


def test_influence_select(page):
    """Influences are chosen on the human readable scale."""
    load_example(page)
    choose(page, page.locator('#influence-context'), 'speech commands')
    page.wait_for_selector('#influence-table >> text=pickup')
    select = page.locator('.influence-select').nth(5)  # pickup on pick up tool
    assert '4 - very probable (75%)' in select.text_content()
    choose(page, select, '1 - not very probable (5%)')
    page.wait_for_function(
        "document.querySelectorAll('.influence-select')[5].textContent.includes('not very')")
    assert page.is_enabled('#undo')


def test_combined_influence(page):
    """A combined influence is added and removed (manual protocol: advanced table)."""
    load_example(page)
    page.click('#add-combined')
    choose(page, page.locator('.combined-part-select').nth(1), 'working')
    page.click('#save-combined')
    page.wait_for_function("document.querySelectorAll('.combined-row').length === 2")
    rows = page.locator('.combined-row')
    assert 'human activity = working, human holding object = False' in rows.nth(0).text_content()
    page.locator('.remove-combined').nth(0).click()
    page.wait_for_function("document.querySelectorAll('.combined-row').length === 1")


def test_threshold(page):
    """An invalid decision threshold is reported."""
    load_example(page)
    page.fill('#threshold', '1.2')
    page.locator('#threshold').blur()
    page.wait_for_selector('#problems')
    assert 'Decision threshold' in page.text_content('#problems')


def test_download(page):
    """Download saves the config as YAML with header (manual protocol: Save)."""
    load_example(page)
    page.fill('#threshold', '0.7')
    page.locator('#threshold').blur()
    page.wait_for_selector('#dirty')
    with page.expect_download() as download_info:
        page.click('#download')
    download = download_info.value
    assert download.suggested_filename == 'small_example.yml'
    text = open(download.path(), encoding='utf-8').read()
    assert 'format_version: 1' in text and 'decision_threshold: 0.7' in text
    page.wait_for_selector('#dirty', state='detached')
    assert page.evaluate('window.cobairDirty') is False


def test_draft_restored(page):
    """A new tab restores the unsaved draft from the browser storage."""
    load_example(page)
    page.fill('#threshold', '0.65')
    page.locator('#threshold').blur()
    page.wait_for_selector('#dirty')
    second = page.context.new_page()
    second.goto(page.url)
    second.wait_for_selector('#info')
    assert 'draft was restored' in second.text_content('#info')
    assert second.input_value('#threshold') == '0.65'


def test_help_links(page):
    """The info icons link to the Tutorial sections (#178 - #181)."""
    for topic, anchor in [('apriori', 'apriori-probabilities'), ('influence', 'influence-values'),
                          ('combined', 'combined-context-influence'),
                          ('threshold', 'decision-threshold')]:
        href = page.get_attribute(f'#help-{topic}', 'href')
        assert href == f'https://dfki-ric.github.io/CoBaIR/Tutorial/#{anchor}'


def test_graph(page):
    """The graph shows the config; clicking a context unfolds and selects it (#182)."""
    load_example(page)
    page.wait_for_selector('#graph .react-flow__node')
    assert page.locator('#graph .react-flow__node').count() == 6
    assert page.locator('#graph .react-flow__edge').count() == 9
    page.locator('#graph .react-flow__node', has_text='speech commands').click()
    page.wait_for_function("document.querySelectorAll('#graph .react-flow__node').length === 9")
    assert page.text_content('#influence-context') == 'speech commands'
    page.locator('#graph .react-flow__node', has_text='pick up tool').click()
    page.wait_for_function(
        "getComputedStyle(document.querySelectorAll('.intention-column')[1]).color "
        "!== getComputedStyle(document.querySelectorAll('.intention-column')[0]).color")


def test_live_inference(page):
    """Evidence selects change the chart and the recognized intention (#207)."""
    load_example(page)
    page.click('#tab-inference')
    page.wait_for_selector('#recognized')
    assert page.text_content('#recognized') == \
        'No intention above the decision threshold (80%)'
    selects = page.locator('.evidence-select')
    choose(page, selects.nth(2), 'pickup')
    choose(page, selects.nth(0), 'working')
    choose(page, selects.nth(1), 'True')
    page.wait_for_function(
        "document.querySelector('#recognized').textContent === 'Recognized: pick up tool (95%)'")
    assert page.locator('#inference-chart .recharts-bar-rectangle').count() == 2
    page.wait_for_selector('#graph .react-flow__node:has-text("pick up tool 95%")')
    page.click('#reset-evidence')
    page.wait_for_function(
        "document.querySelector('#recognized').textContent.startsWith('No intention')")


def test_inference_needs_valid_config(page):
    """An invalid config shows a hint instead of the inference."""
    page.click('#tab-inference')
    page.wait_for_selector('#inference-error')
    assert 'Fix the problems' in page.text_content('#inference-error')
