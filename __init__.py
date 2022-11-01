from aqt import mw, browser
from aqt.utils import showInfo, qconnect
# TODO(louisli): Try not to * import
from aqt.qt import *
from aqt import gui_hooks

# See main.ui
from .designer.main import Ui_Dialog
from .ui_helpers import ConfigDefaults, ConfigKeys, COLUMN_LABELS
from .ui_helpers import make_target_field_select, make_dimension_spin_box, make_overwrite_select, make_result_count_box

from PIL import Image, ImageSequence, UnidentifiedImageError

SPOOFED_HEADER = {
  "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36"
}

def sleep(seconds):
  """
  Sleep for a certain amount of time.
  """
  start = time.time()
  while time.time() - start < seconds:
      time.sleep(0.01)
      QApplication.instance().processEvents()

def update_notes(browser, notes):
  pass

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
  possible_fields = mw.col.getNote(selected_notes[0]).keys()
  form.srcField.addItems(possible_fields)
  config_src_field = config[ConfigKeys.SOURCE_FIELD]
  if config_src_field in fields:
    form.srcField.setCurrentIndex(fields.index(config_src_field))

  form.gridLayout.setColumnStretch(1, 1)
  form.gridLayout.setColumnMinimumWidth(1, 120)

  for i, title in enumerate(COLUMN_LABELS):
    form.gridLayout.addWidget(QLabel(title), 0, i)

  for i, sq in enumerate(config["Search Queries"], 1):
    label = sq[ConfigKeys.LABEL]
    search_term = sq[ConfigKeys.SEARCH_TERM]
    target_field = sq[ConfigKeys.TARGET_FIELD]
    result_count = sq.get(ConfigKeys.RESULT_COUNT, ConfigDefaults.RESULT_COUNT)
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
    form.gridLayout.addWidget(make_target_field_select(possible_fields,
                                                       target_field), 2)
    form.gridLayout.addWidget(make_result_count_box(result_count), 3)
    form.gridLayout.addWidget(make_overwrite_select(overwrite), 4)
    form.gridLayout.addWidget(make_dimension_spin_box(width, "Width"), 5)
    form.gridLayout.addWidget(make_dimension_spin_box(width, "Height"), 6)

  # TODO: document this
  if not d.exec_():
    return

  # Save new config to disk.
  new_config = serialize_config_from_ui(form)
  mw.addonManager.writeConfig(__name__, new_config)

  # mpv_executable, env = find_executable("mpv"), os.environ
  # if mpv_executable is None:
  #     mpv_path, env = _packagedCmd(["mpv"])
  #     mpv_executable = mpv_path[0]
  #     try:
  #         with noBundledLibs():
  #             p = subprocess.Popen([mpv_executable, "--version"], startupinfo=si)
  #     except OSError:
  #         mpv_executable = None


def setup_menu(browser: browser.Browser) -> None:
  """
  Adds the button to add images on init of the card browser.
  """
  menu = browser.form.menuEdit
  menu.addSeparator()
  new_action = menu.addAction('BatchImage: Add images to selected cards')
  new_action.triggered.connect(lambda _, b=browser: open_add_images_dialog(b))


gui_hooks.browser_menus_did_init.append(setup_menu)

