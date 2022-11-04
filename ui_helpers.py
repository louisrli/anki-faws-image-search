from aqt.qt import *


class OverwriteValues:
    """
    Possible values for the overwrite config.
    """
    OVERWRITE = "Overwrite"
    SKIP = "Skip"
    APPEND = "Append"


class ConfigKeys:
    """
    See config.json
    """
    SOURCE_FIELD = "sourceField"
    DELIMITER = "delimiter"
    LABEL = "label"
    QUERY_CONFIGS = "queryConfigs"
    SEARCH_TERM = "searchTerm"
    TARGET_FIELD = "targetField"
    RESULT_COUNT = "resultCount"
    WIDTH = "width"
    HEIGHT = "height"
    OVERWRITE = "overwrite"


# The order in which the keys appear as columns in the query config form.
#
# This is an extremely unideal way to do this (hacky) but basing on the legacy
# code: to extract the values from the form later, we need to know what order
# the columns appear.
# TODO: Add some assertions to check this.
QUERY_CONFIG_KEY_ORDER = (
    ConfigKeys.LABEL,
    ConfigKeys.SEARCH_TERM,
    ConfigKeys.TARGET_FIELD,
    ConfigKeys.RESULT_COUNT,
    ConfigKeys.OVERWRITE,
    ConfigKeys.WIDTH,
    ConfigKeys.HEIGHT)


class ConfigDefaults:
    RESULT_COUNT = 1
    WIDTH = -1
    HEIGHT = -1
    OVERWRITE = "Skip"
    IGNORED = "<ignored>"
    # The placeholder value in the search term the user provides.
    WORD_PLACEHOLDER = "{}"


COLUMN_LABELS = [
    "Label",
    "Search Query",
    "Target Field",
    "Result Count",
    "If not empty?",
    "",
    ""]


def make_target_field_select(options, config_value) -> QComboBox:
    """
    Makes a select (combo box) that defaults to selecting the provided value
    """
    comboBox = QComboBox()
    comboBox.setObjectName(ConfigKeys.TARGET_FIELD)
    comboBox.addItem(ConfigDefaults.IGNORED)
    comboBox.addItems(options)

    if config_value in options:
        # + 1 because of the "<ignore>" option that we added earlier
        comboBox.setCurrentIndex(options.index(config_value) + 1)
    return comboBox


def make_result_count_box(config_value) -> QSpinBox:
    spinBox = QSpinBox()
    spinBox.setMinimum(1)
    spinBox.setValue(config_value)
    spinBox.setStyleSheet("""
           QSpinBox {
            width: 24;
        }""")
    return spinBox


def make_overwrite_select(config_value) -> QComboBox:
    select = QComboBox()
    select.setObjectName(ConfigKeys.OVERWRITE)
    select.addItem(OverwriteValues.SKIP)
    select.addItem(OverwriteValues.OVERWRITE)
    select.addItem(OverwriteValues.APPEND)
    # TODO: Need to match the values correctly here.
    select.setCurrentIndex(select.findText(config_value))
    return select


def make_dimension_spin_box(config_value, label) -> QHBoxLayout:
    """
    Used to make either a width/height spin box with the given label, populated
    with the provided value.
    """
    hbox = QHBoxLayout()
    hbox.addWidget(QLabel("%s:" % label))
    spinBox = QSpinBox()
    spinBox.setMinimum(-1)
    spinBox.setMaximum(9999)
    spinBox.setValue(config_value)
    spinBox.setAlignment(Qt.AlignmentFlag.AlignRight |
                         Qt.AlignmentFlag.AlignVCenter)
    hbox.addWidget(spinBox)
    return hbox


def serialize_config_from_ui(form):
    """
    Reads/scrapes the form to get the values of the form as a config so that it
    can be saved to disk and persist across uses.

    See config.json for the default config.
    """
    config = {}
    source_field = form.sourceField.currentText()
    config[ConfigKeys.SOURCE_FIELD] = source_field

    query_configs = []
    num_ui_columns = form.gridLayout.columnCount()
    assert (num_ui_columns == len(QUERY_CONFIG_KEY_ORDER))
    for i in range(1, form.gridLayout.rowCount()):
        q = {}
        # Well, in general this approach is highly coupled with the UI, but I'm
        # too lazy to change it for now, so I'm copying this guy's code.
        for j in range(form.gridLayout.columnCount()):
            key = QUERY_CONFIG_KEY_ORDER[j]
            item = form.gridLayout.itemAtPosition(i, j)

            if isinstance(item, QWidgetItem):
                item = item.widget()
            elif isinstance(item, QLayoutItem):
                item = item.itemAt(1).widget()
            if isinstance(item, QComboBox):
                # Overwrite and target field boxes
                q[key] = item.currentText()
            elif isinstance(item, QSpinBox):
                q[key] = item.value()
            else:
                q[key] = item.text()
        query_configs.append(q)
    config[ConfigKeys.QUERY_CONFIGS] = query_configs
    return config
