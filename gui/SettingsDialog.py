from PyQt6.QtWidgets import (QDialog, QGroupBox, QVBoxLayout, QHBoxLayout,
                             QSpinBox, QDialogButtonBox, QLabel, QPushButton, QCheckBox, QFontComboBox, QComboBox,
                             QLayout, QMessageBox)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from .ColorEditorDialog import ColorEditorDialog

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
        self._query_available_editor_themes()
        self.color_editor_dialog_button = QPushButton("Color Editor...")
        self.color_editor_dialog_button.clicked.connect(self._handle_color_editor_clicked)
        editor_theme_selection_layout.addWidget(QLabel("Editor Color Theme:"))
        editor_theme_selection_layout.addStretch()
        editor_theme_selection_layout.addWidget(self.editor_theme_combobox)
        editor_theme_selection_layout.addWidget(self.color_editor_dialog_button)

        self.highlight_matching_text_checkbox = QCheckBox("Highlight other occurrences of the selected text")
        self.highlight_matching_text_checkbox.setChecked(IDESettings.get_highlight_matching_text())

        self.highlight_style_combobox = QComboBox()
        self.highlight_style_combobox.addItems(["Hollow", "Filled"])
        self.highlight_style_combobox.setCurrentIndex(IDESettings.get_highlight_fill_rect())

        general_group_layout.addWidget(self.autoreload_last_checkbox)
        general_group_layout.addLayout(icon_theme_section_layout)
        general_group_layout.addLayout(color_theme_selection_layout)

        general_group_box.setLayout(general_group_layout)

        editor_group_box = QGroupBox("Editor")
        editor_group_layout = QVBoxLayout()

        self.enable_autocompletion_checkbox = QCheckBox("Enable autocompletion suggestions")
        self.enable_autocompletion_checkbox.setChecked(IDESettings.get_enable_autocompletion_check())

        autocompletion_threshold_layout = QHBoxLayout()
        self.autocompletion_threshold_spinbox = QSpinBox(self)
        self.autocompletion_threshold_spinbox.setMinimum(1)
        self.autocompletion_threshold_spinbox.setMaximum(10)
        self.autocompletion_threshold_spinbox.setValue(IDESettings.get_autocompletion_trigger_threshold())
        self.autocompletion_threshold_spinbox.setEnabled(self.enable_autocompletion_checkbox.isChecked())

        self.enable_autocompletion_checkbox.checkStateChanged.connect(self._handle_autosuggestions_checkbox_state_changed)

        autocompletion_threshold_layout.addWidget(QLabel("Suggestions dialog trigger threshold:"))
        autocompletion_threshold_layout.addStretch()
        autocompletion_threshold_layout.addWidget(self.autocompletion_threshold_spinbox)
        autocompletion_threshold_layout.addWidget(QLabel("character(s)"))

        self.font_name_combobox = QFontComboBox()
        current_font = QFont(IDESettings.get_font_name(),
                             IDESettings.get_font_size())
        self.font_name_combobox.setCurrentFont(current_font)

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

        font_name_layout = QHBoxLayout()
        font_name_layout.addWidget(QLabel("Font:"))
        font_name_layout.addStretch()
        font_name_layout.addWidget(self.font_name_combobox)
        font_name_layout.addWidget(self.font_size_spinbox)
        font_name_layout.addWidget(self.bold_toggle_button)

        highlight_style_layout = QHBoxLayout()
        highlight_style_layout.addWidget(QLabel("Matching text highlight style:"))
        highlight_style_layout.addStretch()
        highlight_style_layout.addWidget(self.highlight_style_combobox)

        editor_group_layout.addWidget(self.enable_autocompletion_checkbox)
        editor_group_layout.addLayout(autocompletion_threshold_layout)
        editor_group_layout.addLayout(font_name_layout)
        editor_group_layout.addLayout(editor_theme_selection_layout)
        editor_group_layout.addWidget(self.highlight_matching_text_checkbox)
        editor_group_layout.addLayout(highlight_style_layout)
        editor_group_box.setLayout(editor_group_layout)

        advanced_group_box = QGroupBox("Advanced")
        advanced_group_layout = QHBoxLayout()

        self._reset_settings_button = QPushButton("Reset All Settings")
        self._reset_settings_button.clicked.connect(self._handle_reset_settings_clicked)

        advanced_group_layout.addWidget(self._reset_settings_button)
        advanced_group_layout.addStretch()

        advanced_group_box.setLayout(advanced_group_layout)

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
        main_layout.addWidget(advanced_group_box)
        main_layout.addWidget(self.button_box)

        main_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(main_layout)

    def _handle_autosuggestions_checkbox_state_changed(self, newState):
        self.autocompletion_threshold_spinbox.setEnabled(self.enable_autocompletion_checkbox.isChecked())

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

    def _query_available_editor_themes(self):
        self.editor_theme_combobox.clear()
        self.editor_theme_combobox.addItems(EditorThemes.query_available_editor_themes())
        self._set_editor_theme_in_editor_combobox()

    def _handle_color_editor_clicked(self):
        color_editor = ColorEditorDialog(self.editor_theme_combobox.currentText(), self)
        color_editor.exec()
        self._query_available_editor_themes()

    def _handle_reset_settings_clicked(self):
        confirm_prompt = QMessageBox.question(self, "Confirm Reset",
                                              "Are you sure you want to reset ALL settings?<br>" +
                                              "<b>Note: This will also clear the recently opened folders list!</b>",
                                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                              QMessageBox.StandardButton.No)

        if confirm_prompt == QMessageBox.StandardButton.Yes:
            IDESettings.reset_settings()
            self._get_settings()

    def _get_settings(self):
        self.autoreload_last_checkbox.setChecked(IDESettings.get_autoload_last_game_check())
        current_font = QFont(IDESettings.get_font_name(),
                             IDESettings.get_font_size())
        self.font_name_combobox.setCurrentFont(current_font)
        self.icon_theme_combobox.setCurrentText(IDESettings.get_icon_theme())
        self.font_size_spinbox.setValue(IDESettings.get_font_size())
        self.bold_toggle_button.setChecked(IDESettings.get_font_boldness())
        self.enable_autocompletion_checkbox.setChecked(IDESettings.get_enable_autocompletion_check())
        self.autocompletion_threshold_spinbox.setValue(IDESettings.get_autocompletion_trigger_threshold())
        self.highlight_matching_text_checkbox.setChecked(IDESettings.get_highlight_matching_text())
        self.highlight_style_combobox.setCurrentIndex(IDESettings.get_highlight_fill_rect())


    def _handle_apply(self):
        current_font = self.font_name_combobox.currentFont()
        IDESettings.set_font_name(current_font.family())
        IDESettings.set_font_size(self.font_size_spinbox.value())
        IDESettings.set_font_boldness(self.bold_toggle_button.isChecked())
        IDESettings.set_autoload_last_game_check(self.autoreload_last_checkbox.isChecked())
        IDESettings.set_icon_theme(self.icon_theme_combobox.currentText())
        IDESettings.set_color_theme(self.color_theme_combobox.currentText())
        IDESettings.set_editor_color_theme(self.editor_theme_combobox.currentText())
        IDESettings.set_enable_autocompletion_check(self.enable_autocompletion_checkbox.isChecked())
        IDESettings.set_autocompletion_trigger_threshold(self.autocompletion_threshold_spinbox.value())
        IDESettings.set_hightlight_matching_text(self.highlight_matching_text_checkbox.isChecked())
        IDESettings.set_highlight_fill_rect(self.highlight_style_combobox.currentIndex())
        self.settings_changed.emit()

    def _handle_accept(self):
        self._handle_apply()
        self.accept()
