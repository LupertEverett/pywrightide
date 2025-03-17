# A dialog that allows displaying and editing of Editor Themes

from data import IDESettings, EditorThemes

from PyQt6.QtWidgets import QDialog, QPushButton, QColorDialog, QComboBox, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, \
    QGridLayout, QInputDialog, QLineEdit, QMessageBox
from PyQt6.QtGui import QColor

from data.ColorThemes import load_current_color_theme

PROTECTED_EDITOR_THEMES = ("default", "darkmode")


class ColorEditorDialog(QDialog):

    def __init__(self, selected_theme:str = "", parent=None):
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
        self.close_button = QPushButton("Close")

        self.save_button.pressed.connect(self._handle_save_pressed)
        self.save_as_button.pressed.connect(self._handle_save_as_pressed)
        self.close_button.pressed.connect(self.accept)

        # Prepare the grid area
        theme_color_group_box = QGroupBox("Theme Colors")

        theme_colors_layout = QGridLayout()

        theme_colors_layout.addWidget(QLabel("<b>Color Name</b>"), 0, 0)
        theme_colors_layout.addWidget(QLabel("<b>Text</b>"), 0, 1)
        theme_colors_layout.addWidget(QLabel("<b>Background</b>"), 0, 2)

        theme_colors_layout.addWidget(QLabel("Default:"), 1, 0)
        theme_colors_layout.addWidget(QLabel("Commands:"), 2, 0)
        theme_colors_layout.addWidget(QLabel("Special Variables:"), 3, 0)
        theme_colors_layout.addWidget(QLabel("Parameters:"), 4, 0)
        theme_colors_layout.addWidget(QLabel("Comments:"), 5, 0)
        theme_colors_layout.addWidget(QLabel("Strings:"), 6, 0)
        theme_colors_layout.addWidget(QLabel("Numbers:"), 7, 0)
        theme_colors_layout.addWidget(QLabel("Built-in Macros:"), 8, 0)
        theme_colors_layout.addWidget(QLabel("Game Macros:"), 9, 0)
        theme_colors_layout.addWidget(QLabel("String Tokens:"), 10, 0)
        theme_colors_layout.addWidget(QLabel("Line Column:"), 11, 0)
        theme_colors_layout.addWidget(QLabel("Line Column Border:"), 12, 0)
        theme_colors_layout.addWidget(QLabel("Caret:"), 13, 0)

        ## Prepare the color buttons
        self.color_buttons = []

        # Add the double-color elements
        for row in range(len(self.selected_theme_colors.colors) - 2):
            color_button_row = []

            for col in range(2):
                color_button = ColorButton()

                color_button.pressed.connect(lambda r=row, c=col: self._handle_color_button_pressed(r, c))

                color_button_row.append(color_button)

                theme_colors_layout.addWidget(color_button, row+1, col+1)

            self.color_buttons.append(color_button_row)

        # Add the single-color elements
        self.line_column_border_color_button = ColorButton()
        self.line_column_border_color_button.pressed.connect(lambda r=11, c=1: self._handle_color_button_pressed(r, c))
        theme_colors_layout.addWidget(self.line_column_border_color_button, 12, 2)

        self.caret_color_button = ColorButton()
        self.caret_color_button.pressed.connect(lambda r=12, c=1: self._handle_color_button_pressed(r, c))
        theme_colors_layout.addWidget(self.caret_color_button, 13, 2)

        self.color_buttons.append([None, self.line_column_border_color_button])
        self.color_buttons.append([None, self.caret_color_button])

        self._colorize_buttons_from_selected_theme()

        self.selected_theme_combobox.currentIndexChanged.connect(self._handle_selected_theme_combobox_current_changed)

        theme_color_group_box.setLayout(theme_colors_layout)

        bottom_button_layout = QHBoxLayout()

        bottom_button_layout.addWidget(self.save_button)
        bottom_button_layout.addWidget(self.save_as_button)
        bottom_button_layout.addWidget(self.close_button)

        main_layout = QVBoxLayout()

        main_layout.addLayout(selected_theme_combobox_layout)
        main_layout.addWidget(theme_color_group_box)
        main_layout.addLayout(bottom_button_layout)

        self._set_save_buttons_states()

        self.setLayout(main_layout)

    def _set_editor_theme_in_editor_combobox(self, selected_theme_name):
        found_idx = self.selected_theme_combobox.findText(selected_theme_name)

        if found_idx != -1:
            self.selected_theme_combobox.setCurrentIndex(found_idx)

    def _query_available_editor_themes(self):
        self.selected_theme_combobox.clear()
        self.selected_theme_combobox.addItems(EditorThemes.query_available_editor_themes())

    def _handle_color_button_pressed(self, row: int, col: int):
        current_color = self.color_buttons[row][col].button_color
        color_picker_dialog = QColorDialog(current_color, self)

        if color_picker_dialog.exec() and color_picker_dialog.currentColor() != current_color:
            self.color_buttons[row][col].set_button_color(color_picker_dialog.currentColor())
            if col == 0:
                self.selected_theme_colors.colors[row].text_color = color_picker_dialog.currentColor().name(QColor.NameFormat.HexArgb)
            else:
                self.selected_theme_colors.colors[row].paper_color = color_picker_dialog.currentColor().name(QColor.NameFormat.HexArgb)
            self._current_theme_modified = True
            self._set_save_buttons_states()

    def _handle_save_pressed(self):
        self._save_theme_to_file(self.selected_theme_combobox.currentText())

    def _handle_save_as_pressed(self):
        if self._try_to_save_as():
            self._query_available_editor_themes()
            self._switch_to_another_theme(self._previous_selected_theme)

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
            self._set_save_buttons_states()

    def _handle_selected_theme_combobox_current_changed(self):
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
        self._set_save_buttons_states()

    def _set_save_buttons_states(self):
        self.save_button.setEnabled(self._current_theme_modified
                                    and self.selected_theme_combobox.currentText() not in PROTECTED_EDITOR_THEMES)
        self.save_as_button.setEnabled(self._current_theme_modified)

    def _colorize_buttons_from_selected_theme(self):
        for row in range(len(self.selected_theme_colors.colors) - 2):
            text_color = QColor.fromString(self.selected_theme_colors.colors[row].text_color)
            paper_color = QColor.fromString(self.selected_theme_colors.colors[row].paper_color)

            self.color_buttons[row][0].set_button_color(text_color)
            self.color_buttons[row][1].set_button_color(paper_color)

        line_column_border_color = QColor.fromString(self.selected_theme_colors.editor_margin_border_color.paper_color)
        caret_color = QColor.fromString(self.selected_theme_colors.caret_color.paper_color)

        self.line_column_border_color_button.set_button_color(line_column_border_color)
        self.caret_color_button.set_button_color(caret_color)


class ColorButton(QPushButton):
    def __init__(self, parent=None, button_color = QColor()):
        super().__init__(parent)

        self.button_color = QColor()
        self.set_button_color(button_color)

    def set_button_color(self, button_color: QColor):
        self.button_color = button_color
        self.setStyleSheet("""background-color: {}; 
                           border: 1px solid gray;
                           border-radius: 4px"""
                           .format(self.button_color.name(QColor.NameFormat.HexArgb)))