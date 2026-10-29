# A dialog that allows displaying and editing of Editor Themes
from enum import Enum

from data import EditorThemes

from PyQt6.QtWidgets import QDialog, QPushButton, QColorDialog, QComboBox, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, \
    QGridLayout, QInputDialog, QLineEdit, QMessageBox, QLayout, QSpinBox
from PyQt6.QtGui import QColor

PROTECTED_EDITOR_THEMES = ("default", "darkmode")

class ColorButton(QPushButton):
    def __init__(self, color_name: EditorThemes.ColorName, color_target: EditorThemes.ColorTarget, button_color = QColor(), parent=None):
        super().__init__(parent)

        self.button_color = QColor()
        self.color_name = color_name
        self.color_target = color_target
        self.set_button_color(button_color)

    def set_button_color(self, button_color: QColor):
        self.button_color = button_color
        self.setStyleSheet("""background-color: {}; 
                           border: 1px solid gray;
                           border-radius: 4px"""
                           .format(self.button_color.name(QColor.NameFormat.HexArgb)))


class ColorEditorDialog(QDialog):

    def __init__(self, selected_theme: str = "", parent=None):
        super().__init__(parent)

        self.setWindowTitle("Color Editor")

        self.selected_theme_combobox = QComboBox(self)

        self._current_theme_modified = False
        self._question_already_prompted = False # To prevent save question dialog from popping up twice

        self._query_available_editor_themes()

        self._previous_selected_theme = ""

        if selected_theme != "":
            self._set_editor_theme_in_editor_combobox(selected_theme)
            self.selected_theme_colors = EditorThemes.EditorColorTheme.load_from_theme_name(selected_theme)
            self._previous_selected_theme = selected_theme
        else:
            self.selected_theme_colors = EditorThemes.EditorColorTheme()

        selected_theme_combobox_layout = QHBoxLayout()
        selected_theme_combobox_layout.addWidget(QLabel("Selected Editor Theme:"))
        selected_theme_combobox_layout.addWidget(self.selected_theme_combobox)

        self.save_button = QPushButton("Save")
        self.save_as_button = QPushButton("Save As")
        self.reset_button = QPushButton("Reset")
        self.close_button = QPushButton("Close")

        self.save_button.pressed.connect(self._handle_save_pressed)
        self.save_as_button.pressed.connect(self._handle_save_as_pressed)
        self.reset_button.pressed.connect(self._handle_reset_pressed)
        self.close_button.pressed.connect(self.accept)

        # Prepare the grid area
        theme_color_group_box = QGroupBox("Text Colors")

        editor_color_group_box = QGroupBox("Editor Colors")

        theme_colors_layout = QGridLayout()
        theme_colors_layout.setColumnMinimumWidth(1, 75)
        theme_colors_layout.setColumnMinimumWidth(2, 75)

        editor_colors_layout = QGridLayout()
        editor_colors_layout.setColumnMinimumWidth(1, 75)
        editor_colors_layout.setColumnMinimumWidth(2, 75)

        ## Prepare the color buttons
        def_text_color = ColorButton(EditorThemes.ColorName.DEFAULT, EditorThemes.ColorTarget.TEXT)
        def_text_color.pressed.connect(lambda: self._handle_color_button_pressed(def_text_color))

        def_paper_color = ColorButton(EditorThemes.ColorName.DEFAULT, EditorThemes.ColorTarget.PAPER)
        def_paper_color.pressed.connect(lambda: self._handle_color_button_pressed(def_paper_color))

        cmd_text_color = ColorButton(EditorThemes.ColorName.COMMANDS, EditorThemes.ColorTarget.TEXT)
        cmd_text_color.pressed.connect(lambda: self._handle_color_button_pressed(cmd_text_color))

        cmd_paper_color = ColorButton(EditorThemes.ColorName.COMMANDS, EditorThemes.ColorTarget.PAPER)
        cmd_paper_color.pressed.connect(lambda: self._handle_color_button_pressed(cmd_paper_color))

        spc_var_text_color = ColorButton(EditorThemes.ColorName.SPECIAL_VARS, EditorThemes.ColorTarget.TEXT)
        spc_var_text_color.pressed.connect(lambda: self._handle_color_button_pressed(spc_var_text_color))

        spc_var_paper_color = ColorButton(EditorThemes.ColorName.SPECIAL_VARS, EditorThemes.ColorTarget.PAPER)
        spc_var_paper_color.pressed.connect(lambda: self._handle_color_button_pressed(spc_var_paper_color))

        param_text_color = ColorButton(EditorThemes.ColorName.PARAMETERS, EditorThemes.ColorTarget.TEXT)
        param_text_color.pressed.connect(lambda: self._handle_color_button_pressed(param_text_color))

        param_paper_color = ColorButton(EditorThemes.ColorName.PARAMETERS, EditorThemes.ColorTarget.PAPER)
        param_paper_color.pressed.connect(lambda: self._handle_color_button_pressed(param_paper_color))

        comment_text_color = ColorButton(EditorThemes.ColorName.LINE_COMMENTS, EditorThemes.ColorTarget.TEXT)
        comment_text_color.pressed.connect(lambda: self._handle_color_button_pressed(comment_text_color))

        comment_paper_color = ColorButton(EditorThemes.ColorName.LINE_COMMENTS, EditorThemes.ColorTarget.PAPER)
        comment_paper_color.pressed.connect(lambda: self._handle_color_button_pressed(comment_paper_color))

        strings_text_color = ColorButton(EditorThemes.ColorName.STRING_LITERALS, EditorThemes.ColorTarget.TEXT)
        strings_text_color.pressed.connect(lambda: self._handle_color_button_pressed(strings_text_color))

        strings_paper_color = ColorButton(EditorThemes.ColorName.STRING_LITERALS, EditorThemes.ColorTarget.PAPER)
        strings_paper_color.pressed.connect(lambda: self._handle_color_button_pressed(strings_paper_color))

        numbers_text_color = ColorButton(EditorThemes.ColorName.NUMBERS, EditorThemes.ColorTarget.TEXT)
        numbers_text_color.pressed.connect(lambda: self._handle_color_button_pressed(numbers_text_color))

        numbers_paper_color = ColorButton(EditorThemes.ColorName.NUMBERS, EditorThemes.ColorTarget.PAPER)
        numbers_paper_color.pressed.connect(lambda: self._handle_color_button_pressed(numbers_paper_color))

        builtin_macros_text_color = ColorButton(EditorThemes.ColorName.BUILTIN_MACROS, EditorThemes.ColorTarget.TEXT)
        builtin_macros_text_color.pressed.connect(lambda: self._handle_color_button_pressed(builtin_macros_text_color))

        builtin_macros_paper_color = ColorButton(EditorThemes.ColorName.BUILTIN_MACROS, EditorThemes.ColorTarget.PAPER)
        builtin_macros_paper_color.pressed.connect(lambda: self._handle_color_button_pressed(builtin_macros_paper_color))

        game_macros_text_color = ColorButton(EditorThemes.ColorName.GAME_MACROS, EditorThemes.ColorTarget.TEXT)
        game_macros_text_color.pressed.connect(lambda: self._handle_color_button_pressed(game_macros_text_color))

        game_macros_paper_color = ColorButton(EditorThemes.ColorName.GAME_MACROS, EditorThemes.ColorTarget.PAPER)
        game_macros_paper_color.pressed.connect(
            lambda: self._handle_color_button_pressed(game_macros_paper_color)
        )

        str_tokens_text_color = ColorButton(EditorThemes.ColorName.STRING_TOKENS, EditorThemes.ColorTarget.TEXT)
        str_tokens_text_color.pressed.connect(lambda: self._handle_color_button_pressed(str_tokens_text_color))

        str_tokens_paper_color = ColorButton(EditorThemes.ColorName.STRING_TOKENS, EditorThemes.ColorTarget.PAPER)
        str_tokens_paper_color.pressed.connect(
            lambda: self._handle_color_button_pressed(str_tokens_paper_color)
        )

        margin_color = ColorButton(EditorThemes.ColorName.EDITOR_MARGIN, EditorThemes.ColorTarget.PAPER)
        margin_color.pressed.connect(
            lambda: self._handle_color_button_pressed(margin_color)
        )

        border_margin_color = ColorButton(EditorThemes.ColorName.EDITOR_MARGIN_BORDER, EditorThemes.ColorTarget.PAPER)
        border_margin_color.pressed.connect(
            lambda: self._handle_color_button_pressed(border_margin_color)
        )

        caret_color = ColorButton(EditorThemes.ColorName.CARET, EditorThemes.ColorTarget.PAPER)
        caret_color.pressed.connect(
            lambda: self._handle_color_button_pressed(caret_color)
        )

        matching_text_highlight_color = ColorButton(EditorThemes.ColorName.MATCH_HIGHLIGHT, EditorThemes.ColorTarget.PAPER)
        matching_text_highlight_color.pressed.connect(
            lambda: self._handle_color_button_pressed(matching_text_highlight_color)
        )

        param_box_color = ColorButton(EditorThemes.ColorName.PARAMETER_BOXES, EditorThemes.ColorTarget.PAPER)
        param_box_color.pressed.connect(
            lambda: self._handle_color_button_pressed(param_box_color)
        )

        fold_margin_1_color = ColorButton(EditorThemes.ColorName.FOLD_MARGIN_1, EditorThemes.ColorTarget.PAPER)
        fold_margin_1_color.pressed.connect(
            lambda: self._handle_color_button_pressed(fold_margin_1_color)
        )

        fold_margin_2_color = ColorButton(EditorThemes.ColorName.FOLD_MARGIN_2, EditorThemes.ColorTarget.PAPER)
        fold_margin_2_color.pressed.connect(
            lambda: self._handle_color_button_pressed(fold_margin_2_color)
        )

        self.color_buttons = [
            def_text_color, def_paper_color, cmd_text_color, cmd_paper_color,
            spc_var_text_color, spc_var_paper_color, param_text_color, param_paper_color,
            comment_text_color, comment_paper_color, strings_text_color, strings_paper_color,
            numbers_text_color, numbers_paper_color, builtin_macros_text_color, builtin_macros_paper_color,
            game_macros_text_color, game_macros_paper_color, str_tokens_text_color, str_tokens_paper_color,
            margin_color, border_margin_color, caret_color, matching_text_highlight_color,
            param_box_color, fold_margin_1_color, fold_margin_2_color
        ]

        theme_colors_layout.addWidget(QLabel("<b>Color Name</b>"), 0, 0)
        theme_colors_layout.addWidget(QLabel("<b>Text</b>"), 0, 1)
        theme_colors_layout.addWidget(QLabel("<b>Background</b>"), 0, 2)

        theme_colors_layout.addWidget(QLabel("Default:"), 1, 0)
        theme_colors_layout.addWidget(def_text_color, 1, 1)
        theme_colors_layout.addWidget(def_paper_color, 1, 2)

        theme_colors_layout.addWidget(QLabel("Commands:"), 2, 0)
        theme_colors_layout.addWidget(cmd_text_color, 2, 1)
        theme_colors_layout.addWidget(cmd_paper_color, 2, 2)

        theme_colors_layout.addWidget(QLabel("Special Variables:"), 3, 0)
        theme_colors_layout.addWidget(spc_var_text_color, 3, 1)
        theme_colors_layout.addWidget(spc_var_paper_color, 3, 2)

        theme_colors_layout.addWidget(QLabel("Parameters:"), 4, 0)
        theme_colors_layout.addWidget(param_text_color, 4, 1)
        theme_colors_layout.addWidget(param_paper_color, 4, 2)

        theme_colors_layout.addWidget(QLabel("Comments:"), 5, 0)
        theme_colors_layout.addWidget(comment_text_color, 5, 1)
        theme_colors_layout.addWidget(comment_paper_color, 5, 2)

        theme_colors_layout.addWidget(QLabel("Strings:"), 6, 0)
        theme_colors_layout.addWidget(strings_text_color, 6, 1)
        theme_colors_layout.addWidget(strings_paper_color, 6, 2)

        theme_colors_layout.addWidget(QLabel("Numbers:"), 7, 0)
        theme_colors_layout.addWidget(numbers_text_color, 7, 1)
        theme_colors_layout.addWidget(numbers_paper_color, 7 ,2)

        theme_colors_layout.addWidget(QLabel("Built-in Macros:"), 8, 0)
        theme_colors_layout.addWidget(builtin_macros_text_color, 8, 1)
        theme_colors_layout.addWidget(builtin_macros_paper_color, 8, 2)

        theme_colors_layout.addWidget(QLabel("Game Macros:"), 9, 0)
        theme_colors_layout.addWidget(game_macros_text_color, 9, 1)
        theme_colors_layout.addWidget(game_macros_paper_color, 9, 2)

        theme_colors_layout.addWidget(QLabel("String Tokens:"), 10, 0)
        theme_colors_layout.addWidget(str_tokens_text_color, 10, 1)
        theme_colors_layout.addWidget(str_tokens_paper_color, 10, 2)

        editor_colors_layout.addWidget(QLabel("<b>Color Name</b>"), 0, 0)
        editor_colors_layout.addWidget(QLabel("<b>Color 1</b>"), 0, 1)
        editor_colors_layout.addWidget(QLabel("<b>Color 2</b>"), 0, 2)

        editor_colors_layout.addWidget(QLabel("Margin:"), 1, 0)
        editor_colors_layout.addWidget(margin_color, 1, 1)

        editor_colors_layout.addWidget(QLabel("Margin Border:"), 2, 0)
        editor_colors_layout.addWidget(border_margin_color, 2, 1)

        editor_colors_layout.addWidget(QLabel("Caret:"), 3, 0)
        editor_colors_layout.addWidget(caret_color, 3, 1)

        editor_colors_layout.addWidget(QLabel("Matching Text Highlight:"), 4, 0)
        editor_colors_layout.addWidget(matching_text_highlight_color, 4, 1)

        editor_colors_layout.addWidget(QLabel("Fold Margin:"), 5, 0)
        editor_colors_layout.addWidget(fold_margin_1_color, 5, 1)
        editor_colors_layout.addWidget(fold_margin_2_color, 5, 2)

        editor_colors_layout.addWidget(QLabel("Parameter boxes:"), 6, 0)
        editor_colors_layout.addWidget(param_box_color, 6, 1)

        editor_colors_layout.addWidget(QLabel("Parameter boxes alpha:"), 7, 0)

        self.parameter_boxes_spinbox = QSpinBox()
        self.parameter_boxes_spinbox.setRange(0, 255)
        self.parameter_boxes_spinbox.valueChanged.connect(lambda value: self._handle_alpha_spinbox_changed(param_box_color, value=value))
        editor_colors_layout.addWidget(self.parameter_boxes_spinbox, 7, 2)

        self._colorize_buttons_from_selected_theme()

        self.selected_theme_combobox.currentIndexChanged.connect(self._handle_selected_theme_combobox_current_changed)

        theme_color_group_box.setLayout(theme_colors_layout)

        editor_color_group_box_layout = QVBoxLayout()
        editor_color_group_box_layout.addLayout(editor_colors_layout)
        editor_color_group_box_layout.addStretch()

        editor_color_group_box.setLayout(editor_color_group_box_layout)

        bottom_button_layout = QHBoxLayout()

        bottom_button_layout.addWidget(self.save_button)
        bottom_button_layout.addWidget(self.save_as_button)
        bottom_button_layout.addWidget(self.reset_button)
        bottom_button_layout.addWidget(self.close_button)

        colors_layout = QHBoxLayout()

        colors_layout.addWidget(theme_color_group_box)
        colors_layout.addWidget(editor_color_group_box)

        main_layout = QVBoxLayout()

        main_layout.addLayout(selected_theme_combobox_layout)
        main_layout.addLayout(colors_layout)
        main_layout.addLayout(bottom_button_layout)

        main_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self._set_bottom_buttons_states()

        self.setLayout(main_layout)

    def _set_editor_theme_in_editor_combobox(self, selected_theme_name):
        found_idx = self.selected_theme_combobox.findText(selected_theme_name)

        if found_idx != -1:
            self.selected_theme_combobox.setCurrentIndex(found_idx)

    def _query_available_editor_themes(self):
        self.selected_theme_combobox.clear()
        self.selected_theme_combobox.addItems(EditorThemes.query_available_editor_themes())

    def _handle_color_button_pressed(self, button: ColorButton) -> bool:
        current_color = button.button_color
        color_picker_dialog = QColorDialog(current_color, self)

        if color_picker_dialog.exec() and color_picker_dialog.currentColor() != current_color:
            selected_color_str = color_picker_dialog.currentColor().name(QColor.NameFormat.HexArgb)
            button.set_button_color(color_picker_dialog.currentColor())

            match button.color_target:
                case EditorThemes.ColorTarget.TEXT:
                    self.selected_theme_colors.colors_dict[button.color_name].text_color = selected_color_str
                case EditorThemes.ColorTarget.PAPER:
                    self.selected_theme_colors.colors_dict[button.color_name].paper_color = selected_color_str

            self._current_theme_modified = True
            self._set_bottom_buttons_states()
            return True
        return False

    def _handle_parameter_boxes_button_pressed(self, param_button: ColorButton):
        # This variation ensures that alpha is preserved
        if self._handle_color_button_pressed(param_button):
            self._handle_alpha_spinbox_changed(param_button, self.parameter_boxes_spinbox.value())

    def _handle_alpha_spinbox_changed(self, button: ColorButton, value: int):
        color_str = self.selected_theme_colors.get_color_string(button.color_name, button.color_target)
        if int(color_str[1:3], base=16) != value:
            self._current_theme_modified = True
            self._set_bottom_buttons_states()
        self.selected_theme_colors.set_color_string(button.color_name, button.color_target,
                                                    ("#%02x" % value) + color_str[-6:])

    def _handle_save_pressed(self):
        self._save_theme_to_file(self.selected_theme_combobox.currentText())

    def _handle_save_as_pressed(self):
        if self._try_to_save_as():
            self._query_available_editor_themes()
            self._set_editor_theme_in_editor_combobox(self._previous_selected_theme)
            self._switch_to_another_theme(self._previous_selected_theme)

    def _handle_reset_pressed(self):
        choice = QMessageBox.question(self,
                                      "Question",
                                      "Are you sure you want to discard your changes?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if choice == QMessageBox.StandardButton.Yes:
            self._switch_to_another_theme(self.selected_theme_combobox.currentText())

    def _try_to_save_as(self) -> bool:
        available_themes = EditorThemes.query_available_editor_themes()

        new_name, ok = QInputDialog.getText(self,
                                            "Enter Theme Name",
                                            "Enter New Theme Name:",
                                            QLineEdit.EchoMode.Normal,
                                            self._previous_selected_theme)

        if not ok:
            return False

        if new_name == "":
            QMessageBox.critical(self, "Error", "Name cannot be empty!", QMessageBox.StandardButton.Ok)
            return False

        if new_name == self._previous_selected_theme:
            QMessageBox.critical(self, "Error", "New name cannot be the same as old name!",
                                 QMessageBox.StandardButton.Ok)
            return False

        if new_name in PROTECTED_EDITOR_THEMES:
            QMessageBox.critical(self, "Error", "Cannot override a default theme!", QMessageBox.StandardButton.Ok)
            return False

        if new_name in available_themes:
            choice = QMessageBox.question(self,
                                          "Question",
                                          "Theme {} already exists! Do you want to override it?",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if choice == QMessageBox.StandardButton.No:
                return False
            # Pressing Yes should proceed with the saving as usual, so no special handling needed

        self._save_theme_to_file(new_name)
        self._previous_selected_theme = new_name
        return True

    def _save_theme_to_file(self, theme_name: str):
        if theme_name not in PROTECTED_EDITOR_THEMES:
            self.selected_theme_colors.save_to_file(theme_name)
            self._current_theme_modified = False
            self._set_bottom_buttons_states()

    def _handle_selected_theme_combobox_current_changed(self):
        # Do not attempt anything if the combobox is empty
        # This can happen if this function is called during a clear() operation
        if self.selected_theme_combobox.count() == 0:
            return

        # Ask if the user would like to save their changes first
        if not self._current_theme_modified:
            self._switch_to_another_theme(self.selected_theme_combobox.currentText())
            return
        elif self._current_theme_modified and not self._question_already_prompted:
            choice = QMessageBox.question(self,
                                          "Question",
                                          "Would you like to save the changes you made in the current theme first?",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                                          | QMessageBox.StandardButton.Cancel)

            if choice == QMessageBox.StandardButton.Cancel or choice == QMessageBox.StandardButton.Escape:
                # Roll everything back
                self._question_already_prompted = True
                # This line down below will cause this function to run again
                self._set_editor_theme_in_editor_combobox(self._previous_selected_theme)
                self._question_already_prompted = False
                return
            elif choice == QMessageBox.StandardButton.Yes:
                if self._previous_selected_theme in PROTECTED_EDITOR_THEMES:
                    if not self._try_to_save_as():
                        self._question_already_prompted = True
                        # This line down below will cause this function to run again
                        self._set_editor_theme_in_editor_combobox(self._previous_selected_theme)
                        self._question_already_prompted = False
                        return
                else:
                    self._save_theme_to_file(self._previous_selected_theme)

            # Pressing 'No' will also bring us here, no special handling needed
            self._switch_to_another_theme(self.selected_theme_combobox.currentText())

    def _switch_to_another_theme(self, theme_name):
        self.selected_theme_colors = EditorThemes.EditorColorTheme.load_from_theme_name(theme_name)

        self._current_theme_modified = False # Switching themes resets this
        self._colorize_buttons_from_selected_theme()
        self._set_bottom_buttons_states()

    def _set_bottom_buttons_states(self):
        self.save_button.setEnabled(self._current_theme_modified
                                    and self.selected_theme_combobox.currentText() not in PROTECTED_EDITOR_THEMES)
        self.save_as_button.setEnabled(self._current_theme_modified)
        self.reset_button.setEnabled(self._current_theme_modified)

    def _colorize_buttons_from_selected_theme(self):
        for color in self.color_buttons:
            color.set_button_color(QColor.fromString(self.selected_theme_colors.get_color_string(color.color_name, color.color_target)))

        # Handle Parameter Boxes Alpha spinbox
        color_str = self.selected_theme_colors.get_color_string(EditorThemes.ColorName.PARAMETER_BOXES, EditorThemes.ColorTarget.PAPER)
        self.parameter_boxes_spinbox.setValue(int(color_str[1:3], base=16))