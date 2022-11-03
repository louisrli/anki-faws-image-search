from aqt import mw, browser
from aqt.utils import showInfo, qconnect
# TODO(louisli): Try not to * import
from aqt.qt import *
from aqt import gui_hooks

# See main.ui
from .designer.main import Ui_Dialog
from .ui_helpers import ConfigDefaults, ConfigKeys, COLUMN_LABELS, OverwriteValues
from .ui_helpers import make_target_field_select, make_dimension_spin_box, make_overwrite_select, make_result_count_box

def open_add_images_dialog(browser: browser.Browser) -> None:
    """
    Triggered after selecting notes in the browser and clicking "add"

    Opens up the dialog to configure the image search.
    """
    mw = browser.mw

    selected_notes = browser.selectedNotes()
    if not selected_notes:
        aqt.utils.tooltip("No notes were selected.")
        return

    # Set up the dialog using Qt, importing a UI config.
    dialog = QDialog(browser)
    form = Ui_Dialog()
    form.setupUi(dialog)
    config = mw.addonManager.getConfig(__name__)

    # Using the first note in the collection, read the possible fields to
    # configure source/target fields. Set the default field from the config.
    note_fields = mw.col.getNote(selected_notes[0]).keys()
    form.sourceField.addItems(note_fields)
    config_src_field = config[ConfigKeys.SOURCE_FIELD]
    if config_src_field in note_fields:
        form.sourceField.setCurrentIndex(note_fields.index(config_src_field))

    form.gridLayout.setColumnStretch(1, 1)
    form.gridLayout.setColumnMinimumWidth(1, 120)

    for i, title in enumerate(COLUMN_LABELS):
        form.gridLayout.addWidget(QLabel(title), 0, i)

    for i, sq in enumerate(config[ConfigKeys.QUERY_CONFIGS]):
        label = sq[ConfigKeys.LABEL]
        search_term = sq[ConfigKeys.SEARCH_TERM]
        target_field = sq[ConfigKeys.TARGET_FIELD]
        result_count = sq.get(
            ConfigKeys.RESULT_COUNT,
            ConfigDefaults.RESULT_COUNT)
        width = sq.get(ConfigKeys.WIDTH, ConfigDefaults.WIDTH)
        height = sq.get(ConfigKeys.HEIGHT, ConfigDefaults.HEIGHT)
        overwrite = sq.get(ConfigKeys.OVERWRITE, ConfigDefaults.OVERWRITE)

        # Shift +1 to account for the column headers.
        row_idx = i + 1

        # Add the columns for this search query
        # NOTE: This section needs to be synchronized with serialize_config_from_ui
        # and COLUMN_LABELS
        form.gridLayout.addWidget(QLineEdit(label), row_idx, 0)
        form.gridLayout.addWidget(QLineEdit(search_term), row_idx, 1)
        form.gridLayout.addWidget(make_target_field_select(note_fields,
                                                           target_field),
                                  row_idx, 2)
        form.gridLayout.addWidget(make_result_count_box(result_count), row_idx, 3)
        form.gridLayout.addWidget(make_overwrite_select(overwrite), row_idx, 4)
        form.gridLayout.addLayout(make_dimension_spin_box(width, "Width"),
                                  row_idx, 5)
        form.gridLayout.addLayout(make_dimension_spin_box(width, "Height"),
                                  row_idx, 6)

    # TODO: document this
    if not dialog.exec_():
        return
    scrape_images_and_update(form, selected_notes)


def scrape_images_and_update(form, note_ids):
    """
    Main entry point for logic that runs after the start button is pressed.
    """
    pass
    # Save new config to disk, then use new config to scrape images.
    new_config = serialize_config_from_ui(form)
    mw.addonManager.writeConfig(__name__, new_config)

    mw.checkpoint("Add Google Images")
    mw.progress.start(immediate=True)
    browser.model.beginReset()

    # Begin a pool of executors. One job = one query.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        jobs = []
        processed_notes = set()
        for c, note_id in enumerate(note_ids, 1):
            note = mw.col.getNote(note_id)
            source_value = note[new_config[ConfigKeys.SOURCE_FIELD]]

            query_configs = new_config[ConfigKeys.QUERY_CONFIGS]

            for qc in query_configs:
                target_field = qc[ConfigKeys.TARGET_FIELD]

                if not target_field:
                    continue

                # Value already exists, skip to next one.
                if note[target_field] and qc[ConfigKeys.OVERWRITE] == OverwriteValues.SKIP:
                    continue

                final_search_query = qc[ConfigKeys.SEARCH_TERM].replace(
                    "{}",
                    strip_html_clozes(source_value)
                )

                # Here we start pushing the heavy lifting scraping jobs into the
                # queue.

            done, not_done = concurrent.futures.wait(jobs, timeout=0)
            for future in done:
                note_id, fld, images, overwrite = future.result()
                updateField(note_id, fld, images, overwrite)
                processed_notes.add(note_id)
                jobs.remove(future)
            else:
                label = "Processed %s notes..." % len(processed_notes)
                mw.progress.update(label)
                QApplication.instance().processEvents()

        for future in concurrent.futures.as_completed(jobs):
            note_id, fld, images, overwrite = future.result()
            updateField(note_id, fld, images, overwrite)
            processed_notes.add(note_id)
            label = "Processed %s notes..." % len(processed_notes)
            mw.progress.update(label)
            QApplication.instance().processEvents()

    browser.model.endReset()
    mw.requireReset()
    mw.progress.finish()
    showInfo("Number of notes processed: %d" % len(note_ids), parent=browser)

def setup_menu(browser: browser.Browser) -> None:
    """
    Adds the button to add images on init of the card browser.
    """
    menu = browser.form.menuEdit
    menu.addSeparator()
    new_action = menu.addAction('BatchImage: Add images to selected cards')
    new_action.triggered.connect(
        lambda _, b=browser: open_add_images_dialog(b))


gui_hooks.browser_menus_did_init.append(setup_menu)
