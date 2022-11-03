from aqt.qt import *

COLUMN_LABELS = [
    "Label",
    "Search Query",
    "Target Field",
    "Result Count",
    "If not empty?",
    "",
    ""]

# Essentially an enum for values of overwriting.
OverwriteValues = {
    OVERWRITE: "Overwrite",
    SKIP: "Skip",
    APPEND: "Append",
}

ConfigKeys = {
    SOURCE_FIELD: "sourceField",
    DELIMITER: "delimiter",
    LABEL: "label",
    QUERY_CONFIGS: "queryConfigs",
    SEARCH_TERM: "searchTerm",
    TARGET_FIELD: "targetField",
    RESULT_COUNT: "resultCount",
    WIDTH: "width",
    HEIGHT: "height",
    OVERWRITE: "overwrite",
}

ConfigDefaults = {
    RESULT_COUNT: 1,
    WIDTH: -1,
    HEIGHT: 260,
    OVERWRITE: "Skip",
    IGNORED: "<ignored>",
    # The placeholder value in the search term the user provides.
    WORD_PLACEHOLDER: "{}",
}


def make_target_field_select(options, config_value) -> QComboBox:
    """
    Makes a select (combo box) that defaults to selecting the provided value
    """
    comboBox = QComboBox()
    comboBox.setObjectName(ConfigKeys.TARGET_FIELD)
    comboBox.addItem(ConfigDefaults.IGNORED)
    comboBox.addItems(options)

    if config_value in options:
        # + 1 because ignoring options
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
    spinBox.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    hbox.addWidget(spinBox)
    return hbox


def serialize_config_from_ui(form):
    """
    Reads/scrapes the form to get the values of the form as a config so that it
    can be saved to disk and persist across uses.

    See config.json for the default config.
    """
    pass
