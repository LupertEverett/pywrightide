from PyQt6.QtWidgets import (QDialog, QGroupBox, QVBoxLayout, QHBoxLayout,
                             QSpinBox, QDialogButtonBox, QLabel, QPushButton, QCheckBox, QFontComboBox, QComboBox,
                             QLayout)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from data import IDESettings, ColorThemes, EditorThemes
from data import IconThemes


class SettingsDialog(QDialog):

    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Prepare the main layout
        # Don't think we can put so much to here:
        # Fonts
        # Continue from the last folder
        # Maybe an autosave feature
        # Color themes (or at least a dark theme toggle)
        self.setWindowTitle("PyWright IDE Settings")

        main_layout = QVBoxLayout()

        general_group_box = QGroupBox("General")
        general_group_layout = QVBoxLayout()

        self.autoreload_last_checkbox = QCheckBox("Restore the last open game and tabs on startup")
        self.autoreload_last_checkbox.setChecked(IDESettings.get_autoload_last_game_check())

        icon_theme_section_layout = QHBoxLayout()
        self.icon_theme_combobox = QComboBox()
        self.icon_theme_combobox.addItems(IconThemes.query_icon_themes())
        self.icon_theme_combobox.setCurrentText(IDESettings.get_icon_theme())
        icon_theme_section_layout.addWidget(QLabel("Icon Theme:"))
        icon_theme_section_layout.addWidget(self.icon_theme_combobox)

        color_theme_selection_layout = QHBoxLayout()
        self.color_theme_combobox = QComboBox()
        self.color_theme_combobox.addItem("System Theme")
        self.color_theme_combobox.addItems(ColorThemes.query_color_themes())
        self._set_current_color_theme_in_color_combobox()
        color_theme_selection_layout.addWidget(QLabel("Color Theme:"))
        color_theme_selection_layout.addWidget(self.color_theme_combobox)

        editor_theme_selection_layout = QHBoxLayout()
        self.editor_theme_combobox = QComboBox()
        self.editor_theme_combobox.addItems(EditorThemes.query_available_editor_themes())
        self._set_editor_theme_in_editor_combobox()
        editor_theme_selection_layout.addWidget(QLabel("Editor Color Theme:"))
        editor_theme_selection_layout.addWidget(self.editor_theme_combobox)

        general_group_layout.addWidget(self.autoreload_last_checkbox)
        general_group_layout.addLayout(icon_theme_section_layout)
        general_group_layout.addLayout(color_theme_selection_layout)

        general_group_box.setLayout(general_group_layout)

        editor_group_box = QGroupBox("Editor")
        editor_group_layout = QVBoxLayout()

        font_name_layout = QHBoxLayout()
        self.font_name_combobox = QFontComboBox()
        current_font = QFont(IDESettings.get_font_name(),
                             IDESettings.get_font_size())
        self.font_name_combobox.setCurrentFont(current_font)

        font_name_layout.addWidget(QLabel("Font:"))
        font_name_layout.addStretch()

        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setValue(IDESettings.get_font_size())
        self.font_size_spinbox.setMinimum(8)
        self.font_size_spinbox.setMaximum(72)
        self.font_size_spinbox.setToolTip("Font Size")

        self.bold_toggle_button = QPushButton("B")
        self.bold_toggle_button.setCheckable(True)
        self.bold_toggle_button.setChecked(IDESettings.get_font_boldness())
        self.bold_toggle_button.font().setBold(True)
        self.bold_toggle_button.setFixedWidth(30)
        self.bold_toggle_button.setToolTip("Bold")

        font_name_layout.addWidget(self.font_name_combobox)
        font_name_layout.addWidget(self.font_size_spinbox)
        font_name_layout.addWidget(self.bold_toggle_button)

        editor_group_layout.addLayout(font_name_layout)
        editor_group_layout.addLayout(editor_theme_selection_layout)
        editor_group_box.setLayout(editor_group_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                           QDialogButtonBox.StandardButton.Cancel |
                                           QDialogButtonBox.StandardButton.Apply)
        # Obtain the Apply button
        apply_button = self.button_box.button(QDialogButtonBox.StandardButton.Apply)
        apply_button.clicked.connect(self._handle_apply)
        self.button_box.rejected.connect(self.reject)
        self.button_box.accepted.connect(self._handle_accept)

        main_layout.addWidget(general_group_box)
        main_layout.addWidget(editor_group_box)
        main_layout.addWidget(self.button_box)

        main_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(main_layout)

    def _set_current_color_theme_in_color_combobox(self):
        theme_name = IDESettings.get_color_theme()
        found_idx = self.color_theme_combobox.findText(theme_name)

        if found_idx != -1:
            self.color_theme_combobox.setCurrentIndex(found_idx)

    def _set_editor_theme_in_editor_combobox(self):
        theme_name = IDESettings.get_editor_color_theme()
        found_idx = self.editor_theme_combobox.findText(theme_name)

        if found_idx != -1:
            self.editor_theme_combobox.setCurrentIndex(found_idx)

    def _handle_apply(self):
        current_font = self.font_name_combobox.currentFont()
        IDESettings.set_font_name(current_font.family())
        IDESettings.set_font_size(self.font_size_spinbox.value())
        IDESettings.set_font_boldness(self.bold_toggle_button.isChecked())
        IDESettings.set_autoload_last_game_check(self.autoreload_last_checkbox.isChecked())
        IDESettings.set_icon_theme(self.icon_theme_combobox.currentText())
        IDESettings.set_color_theme(self.color_theme_combobox.currentText())
        IDESettings.set_editor_color_theme(self.editor_theme_combobox.currentText())
        self.settings_changed.emit()

    def _handle_accept(self):
        self._handle_apply()
        self.accept()
