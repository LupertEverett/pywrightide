from PyQt5.QtWidgets import (QDialog, QFontDialog, QGroupBox, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QSpinBox, QDialogButtonBox, QLabel, QPushButton, QCheckBox)
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

        font_name_line_layout = QHBoxLayout()
        self.font_name_line_edit = QLineEdit(self.settings.value(IDESettings.FONT_NAME_KEY))
        self.font_change_button = QPushButton("Change...")
        self.font_change_button.clicked.connect(self._handle_font_dialog)

        font_name_line_layout.addWidget(QLabel("Font Name:"))
        font_name_line_layout.addStretch()
        font_name_line_layout.addWidget(self.font_name_line_edit)
        font_name_line_layout.addWidget(self.font_change_button)

        font_size_spinbox_layout = QHBoxLayout()
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setValue(int(self.settings.value(IDESettings.FONT_SIZE_KEY)))
        self.font_size_spinbox.setMinimum(8)
        self.font_size_spinbox.setMaximum(72)
        font_size_spinbox_layout.addWidget(QLabel("Font Size:"))
        font_size_spinbox_layout.addStretch()
        font_size_spinbox_layout.addWidget(self.font_size_spinbox)

        font_group_layout.addLayout(font_name_line_layout)
        font_group_layout.addLayout(font_size_spinbox_layout)

        font_group_box.setLayout(font_group_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        # Obtain the Apply button
        apply_button = self.button_box.button(QDialogButtonBox.Apply)
        apply_button.clicked.connect(self._handle_apply)
        self.button_box.rejected.connect(self.reject)
        self.button_box.accepted.connect(self._handle_accept)

        main_layout.addWidget(general_group_box)
        main_layout.addWidget(font_group_box)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

    def _handle_font_dialog(self):
        font_name = self.settings.value(IDESettings.FONT_NAME_KEY)
        font_size = int(self.settings.value(IDESettings.FONT_SIZE_KEY))
        font_tuple = QFontDialog.getFont(QFont(font_name, font_size, QFont.Bold), self, "Pick a font")

        if font_tuple[1]:
            self.font_name_line_edit.setText(font_tuple[0].family())
            self.font_size_spinbox.setValue(font_tuple[0].pointSize())

    def _handle_apply(self):
        self.settings.setValue(IDESettings.FONT_NAME_KEY, self.font_name_line_edit.text())
        self.settings.setValue(IDESettings.FONT_SIZE_KEY, self.font_size_spinbox.value())
        self.settings.setValue(IDESettings.AUTOLOAD_LAST_PROJECT_KEY, self.autoreload_last_checkbox.isChecked())
        self.settings_changed.emit()

    def _handle_accept(self):
        self._handle_apply()
        self.accept()
