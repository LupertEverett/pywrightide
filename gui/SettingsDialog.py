from PyQt5.QtWidgets import (QDialog, QGroupBox, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QSpinBox, QDialogButtonBox, QLabel, QPushButton, QCheckBox, QFontComboBox)
from PyQt5.QtCore import QSettings, pyqtSignal
from PyQt5.QtGui import QFont

from data import IDESettings


class SettingsDialog(QDialog):

    settings_changed = pyqtSignal()

    def __init__(self, settings_object: QSettings, parent=None):
        super().__init__(parent)

        # Prepare the main layout
        # Don't think we can put so much to here:
        # Fonts
        # Continue from the last folder
        # Maybe an autosave feature
        # Color themes (or at least a dark theme toggle)
        self.setWindowTitle("PyWright IDE Settings")

        self.settings = settings_object
        main_layout = QVBoxLayout()

        general_group_box = QGroupBox("General")
        general_group_layout = QVBoxLayout()

        self.autoreload_last_checkbox = QCheckBox("Autoreload the last open project")
        self.autoreload_last_checkbox.setChecked(self.settings.value(IDESettings.AUTOLOAD_LAST_PROJECT_KEY, False, bool))

        general_group_layout.addWidget(self.autoreload_last_checkbox)

        general_group_box.setLayout(general_group_layout)

        font_group_box = QGroupBox("Editor")
        font_group_layout = QVBoxLayout()

        font_name_layout = QHBoxLayout()
        self.font_name_line_edit = QLineEdit(self.settings.value(IDESettings.FONT_NAME_KEY))
        self.font_name_combobox = QFontComboBox()
        current_font = QFont(self.settings.value(IDESettings.FONT_NAME_KEY),
                             self.settings.value(IDESettings.FONT_SIZE_KEY))
        self.font_name_combobox.setCurrentFont(current_font)

        font_name_layout.addWidget(QLabel("Font:"))
        font_name_layout.addStretch()

        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setValue(self.settings.value(IDESettings.FONT_SIZE_KEY, 10, int))
        self.font_size_spinbox.setMinimum(8)
        self.font_size_spinbox.setMaximum(72)
        self.font_size_spinbox.setToolTip("Font Size")

        self.bold_toggle_button = QPushButton("B")
        self.bold_toggle_button.setCheckable(True)
        self.bold_toggle_button.setChecked(self.settings.value(IDESettings.FONT_BOLD_KEY, True, bool))
        self.bold_toggle_button.font().setBold(True)
        self.bold_toggle_button.setFixedWidth(30)
        self.bold_toggle_button.setToolTip("Bold")

        font_name_layout.addWidget(self.font_name_combobox)
        font_name_layout.addWidget(self.font_size_spinbox)
        font_name_layout.addWidget(self.bold_toggle_button)

        font_group_layout.addLayout(font_name_layout)
        font_group_box.setLayout(font_group_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                           QDialogButtonBox.StandardButton.Cancel |
                                           QDialogButtonBox.StandardButton.Apply)
        # Obtain the Apply button
        apply_button = self.button_box.button(QDialogButtonBox.StandardButton.Apply)
        apply_button.clicked.connect(self._handle_apply)
        self.button_box.rejected.connect(self.reject)
        self.button_box.accepted.connect(self._handle_accept)

        main_layout.addWidget(general_group_box)
        main_layout.addWidget(font_group_box)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

    def _handle_apply(self):
        current_font = self.font_name_combobox.currentFont()
        self.settings.setValue(IDESettings.FONT_NAME_KEY, current_font.family())
        self.settings.setValue(IDESettings.FONT_SIZE_KEY, current_font.pointSize())
        self.settings.setValue(IDESettings.FONT_BOLD_KEY, self.bold_toggle_button.isChecked())
        self.settings.setValue(IDESettings.AUTOLOAD_LAST_PROJECT_KEY, self.autoreload_last_checkbox.isChecked())
        self.settings_changed.emit()

    def _handle_accept(self):
        self._handle_apply()
        self.accept()
