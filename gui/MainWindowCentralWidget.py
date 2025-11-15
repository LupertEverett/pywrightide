from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QMessageBox

from data import IDESettings, EditorThemes
from data.PyWrightGame import PyWrightGameInfo
from .FileEditWidget import FileEditWidget
from .FindReplaceDialog import SearchScope, FindType, ReplaceType
from .GamePropertiesWidget import GamePropertiesWidget


class MainWindowCentralWidget(QWidget):
    update_save_button_requested = pyqtSignal(bool)
    current_tab_cursor_position_changed = pyqtSignal(int, int)
    selection_length_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        """Central widget for the main window. Handles the open tabs.
            :param parent: The parent widget (actually an IDEMainWindow) to attach this widget to.
        """
        super().__init__(parent)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self._handle_remove_tab)
        self.tab_widget.currentChanged.connect(self._handle_tab_change)

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)

        layout.addWidget(self.tab_widget)

        self.setLayout(layout)

        self._try_loading_editor_theme(IDESettings.get_editor_color_theme())

        self.pywright_installation_path: str = ""
        self.selected_game_info: PyWrightGameInfo | None = None
        self._game_properties_widget: GamePropertiesWidget | None = None

    def set_selected_game(self, selected_game_info: PyWrightGameInfo):
        self.selected_game_info = selected_game_info
        self.pywright_installation_path = str(self.selected_game_info.pywright_folder_path)
        self._game_properties_widget = GamePropertiesWidget(self.selected_game_info)
        self._game_properties_widget.load_game(self.selected_game_info)

    # ====== Tab Handling ======
    # ==== Opening new tab ====
    def open_new_tab(self, tab_widget: QWidget, tab_title: str):
        self.tab_widget.addTab(tab_widget, tab_title)
        self.tab_widget.setMovable(self.tab_widget.count() > 1)
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)

    def open_game_properties_tab(self):
        for i in range(self.tab_widget.count()):
            if self.is_game_properties_tab(i):
                # We already have a Game Properties tab open, so switch to that instead.
                self.tab_widget.setCurrentIndex(i)
                return

        self.open_new_tab(self._game_properties_widget, "Game Properties")

    def open_new_editing_tab(self, file_path: str):
        # Don't open a file editing tab if there is already one open for a given file
        for i in range(self.tab_widget.count()):
            # Skip Game Properties tab
            if self.is_game_properties_tab(i):
                continue

            opened_tab: FileEditWidget = self.tab_widget.widget(i)

            if opened_tab.file_path == file_path:
                self.tab_widget.setCurrentIndex(i)
                return
        # Create a new FileEditWidget, and add it to the tab widget
        try:
            file_edit_widget = FileEditWidget(self.pywright_installation_path, file_path)
        except FileNotFoundError:
            return
        file_edit_widget.file_name_changed.connect(self.handle_rename_tab)
        EditorThemes.current_editor_theme.load_theme(IDESettings.get_editor_color_theme())
        file_edit_widget.file_modified.connect(self._update_save_button_and_current_tab)
        if self.selected_game_info is not None:
            file_edit_widget.supply_builtin_macros_to_lexer(self.selected_game_info.builtin_macros)
            file_edit_widget.supply_game_macros_to_lexer(self.selected_game_info.game_macros)
        file_edit_widget.supply_editor_color_theme_to_lexer()
        file_edit_widget.move_to_tab_requested.connect(self._handle_move_to_tab)
        file_edit_widget.replace_next_in_next_tabs_requested.connect(self.replace_next_in_next_tabs)
        file_edit_widget.cursor_position_changed.connect(self._update_line_and_col)
        file_edit_widget.selected_text_changed.connect(self._handle_text_selection_changed)
        file_name = Path(file_path).name
        self.open_new_tab(file_edit_widget, file_name if file_name != "" else "New File")

    def _try_loading_editor_theme(self, theme_name: str):
        """Try loading the editor theme named {theme_name}, on the case of theme missing, load the default editor theme instead.
            :param theme_name: Name of the editor theme.
        """
        try:
            EditorThemes.current_editor_theme.load_theme(IDESettings.get_editor_color_theme())
        except EditorThemes.ThemeNotFoundException:
            theme_name = IDESettings.get_editor_color_theme()
            QMessageBox.information(self, "Editor Theme Not Found",
                                    "PyWright IDE couldn't find the editor theme <b>{}</b>!<br>Resetting back to default editor theme.".format(theme_name),
                                    QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
            EditorThemes.current_editor_theme.reset_colors_to_defaults()
            IDESettings.set_editor_color_theme("default")

    # ==== Changing to a new tab ====
    def _handle_tab_change(self, index: int):
        condition = self.tab_widget.count() > 0 and \
                    not self.is_game_properties_tab(index) and \
                    self.tab_widget.currentWidget().is_file_modified()

        self.update_save_button_requested.emit(condition)
        self._update_line_and_col()
        self._handle_text_selection_changed()

    def _update_line_and_col(self):
        if self.tabs_count() == 0:
            self.current_tab_cursor_position_changed.emit(-1, -1)
        elif not self.is_game_properties_tab(self.tab_widget.currentIndex()):
            (line, col) = self.tab_widget.widget(self.tab_widget.currentIndex()).get_current_cursor_position()
            self.current_tab_cursor_position_changed.emit(line + 1, col + 1)
        else:
            self.current_tab_cursor_position_changed.emit(-1, -1)

    def _handle_text_selection_changed(self):
        if self.tabs_count() == 0 or self.is_game_properties_tab(self.tab_widget.currentIndex()):
            self.selection_length_changed.emit(-1)
        else:
            selection_length = self.tab_widget.widget(self.tab_widget.currentIndex()).get_selection_length()
            self.selection_length_changed.emit(selection_length)

    def is_game_properties_tab(self, index: int):
        return isinstance(self.tab_widget.widget(index), GamePropertiesWidget)

    # ==== Renaming a tab ====
    def handle_rename_tab(self, new_name: str):
        self.tab_widget.setTabText(self.tab_widget.currentIndex(), new_name)

    # ==== Saving a tab ====
    def handle_save_tab(self):
        if not self.is_game_properties_tab(self.tab_widget.currentIndex()):
            self.tab_widget.currentWidget().save_to_file()
            self._update_save_button_and_current_tab()

    def _update_save_button_and_current_tab(self):
        self._update_file_editing_tab_info(self.tab_widget.currentIndex())

    def _update_tab_modified_infos(self):
        # Like _update_save_button() but for all tabs
        for idx in range(self.tab_widget.count()):
            if self.is_game_properties_tab(idx):
                continue

            self._update_file_editing_tab_info(idx)

    def _update_file_editing_tab_info(self, tab_index: int):
        file_edit_widget: FileEditWidget = self.tab_widget.widget(tab_index)
        condition = file_edit_widget.is_file_modified()
        if tab_index == self.tab_widget.currentIndex():
            self.update_save_button_requested.emit(condition)
        tab_text = file_edit_widget.file_name
        # Prepend a * to the tab name if the file is modified
        self.tab_widget.setTabText(tab_index, "*" + tab_text if condition else tab_text)

    # ==== Removing a tab ====
    def _handle_remove_tab(self, index):
        if not self.is_game_properties_tab(index):
            tab: FileEditWidget = self.tab_widget.widget(index)

            if tab.is_file_modified():
                result = self._ask_for_closing_tab(index, False)

                if result == QMessageBox.StandardButton.Cancel:
                    return
                # QMessageBox.No will just ignore the current file, so no special handling for it.
                if result == QMessageBox.StandardButton.Yes:
                    tab.save_to_file()

        self.tab_widget.removeTab(index)
        self.tab_widget.setMovable(self.tab_widget.count() > 1)

    def get_open_tabs_paths(self) -> list[str]:
        """Returns a list of the paths of the open tabs."""
        result = []

        for tab_idx in range(self.tabs_count()):
            if self.is_game_properties_tab(tab_idx):
                result.append("Game Properties")
            else:
                file_widget: FileEditWidget = self.tab_widget.widget(tab_idx)
                result.append(file_widget.file_path)

        return result

    def get_current_tab_index(self):
        return self.tab_widget.currentIndex()

    def set_current_tab_index(self, tab_idx: int):
        if tab_idx < 0:
            raise ValueError("Cannot switch to a negative tab index!")
        self.tab_widget.setCurrentIndex(tab_idx)

    def _ask_for_closing_tab(self, index: int, multiple_tabs: bool):
        """Asks the user if they want to save the contents of the [index]th tab before closing it.

        :param index: Index of the tab about to be closed

        :param multiple_tabs: If set to True, 'Yes To All' and 'No To All' will be added to the possible answers"""

        answers = (QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.YesToAll |
                   QMessageBox.StandardButton.No | QMessageBox.StandardButton.NoToAll |
                   QMessageBox.StandardButton.Cancel) if multiple_tabs \
            else (QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)

        tab: FileEditWidget = self.tab_widget.widget(index)
        tab_text = tab.file_name

        return QMessageBox.question(self, "Confirm Save", "Would you like to save {}?".format(tab_text),
                                    answers, QMessageBox.StandardButton.Cancel)

    def handle_find_signals(self, text: str, find_type: FindType, search_scope: SearchScope):
        if self.tab_widget.count() == 0:
            # If nothing is open, inform the user and do nothing.
            QMessageBox.information(self, "Find/Replace", "There are no tabs open.")
            return
        if not self.is_game_properties_tab(self.tab_widget.currentIndex()):
            file_widget: FileEditWidget = self.tab_widget.currentWidget()
            file_widget.search_in_file(text, find_type, search_scope)

    def handle_replace_signals(self, text_to_find: str, text_to_replace: str, replace_type: ReplaceType,
                               search_scope: SearchScope):
        if self.tab_widget.count() == 0:
            # If nothing is open, inform the user and do nothing.
            QMessageBox.information(self, "Find/Replace", "There are no tabs open.")
            return
        if replace_type == ReplaceType.REPLACE_ALL and search_scope == SearchScope.OPEN_TABS:
            self.replace_all_in_all_open_tabs(text_to_find, text_to_replace)
            return
        if not self.is_game_properties_tab(self.tab_widget.currentIndex()):
            file_widget: FileEditWidget = self.tab_widget.currentWidget()
            file_widget.replace_in_file(text_to_find, text_to_replace, replace_type, search_scope)

    def _handle_move_to_tab(self, text_to_find: str, find_type: FindType):
        if find_type == FindType.FIND_NEXT:
            self._try_to_move_forwards_in_tabs(text_to_find)
        elif find_type == FindType.FIND_PREVIOUS:
            self._try_to_move_backwards_in_tabs(text_to_find)

    def _try_to_move_forwards_in_tabs(self, text_to_find: str):
        tabs_count = self.tab_widget.count()
        current_position = self.tab_widget.currentIndex()
        # If we're already at the last tab, inform the user and do nothing.
        if current_position == tabs_count - 1:
            QMessageBox.information(self, "Find/Replace", "Last tab has been reached. The text couldn't be found.")
            return

        for idx in range(current_position + 1, tabs_count):
            if self.is_game_properties_tab(idx):
                continue

            curr_widget: FileEditWidget = self.tab_widget.widget(idx)
            # Do a search in the selected tab.
            curr_text = curr_widget.sci.text()
            pos = curr_text.find(text_to_find)

            # If we don't have a match, then continue
            if pos == -1:
                continue

            # If we're here, then we have a match.
            self.tab_widget.setCurrentIndex(idx)
            curr_widget.find_next_in_file(text_to_find, SearchScope.SINGLE_FILE, from_top=True)
            return

        # If we cannot find anything, inform the user and stop.
        QMessageBox.information(self, "Find/Replace", "Last tab has been reached. The text couldn't be found.")

    def _try_to_move_backwards_in_tabs(self, text_to_find: str):
        current_position = self.tab_widget.currentIndex()
        # If we're already at the first tab, inform the user and do nothing.
        if current_position == 0:
            QMessageBox.information(self, "Find/Replace", "First tab has been reached. The text couldn't be found.")
            return

        for idx in range(current_position).__reversed__():
            if self.is_game_properties_tab(idx):
                continue

            curr_widget: FileEditWidget = self.tab_widget.widget(idx)
            # Do a search in the selected tab.
            curr_text = curr_widget.sci.text()
            pos = curr_text.rfind(text_to_find)

            # If we don't have a match, then continue
            if pos == -1:
                continue

            # If we're here, then we have a match.
            self.tab_widget.setCurrentIndex(idx)
            curr_widget.find_previous_in_file(text_to_find, SearchScope.SINGLE_FILE, from_bottom=True)
            return

        # If we cannot find anything, inform the user and stop.
        QMessageBox.information(self, "Find/Replace", "First tab has been reached. The text couldn't be found.")

    def replace_next_in_next_tabs(self, text_to_find: str, text_to_replace: str):
        tabs_count = self.tab_widget.count()
        current_position = self.tab_widget.currentIndex()

        if current_position == tabs_count - 1:
            QMessageBox.information(self, "Find/Replace",
                                    "Last tab has been reached. Text to replace couldn't be found.")
            return

        for idx in range(current_position + 1, tabs_count):
            if self.is_game_properties_tab(idx):
                continue

            curr_widget: FileEditWidget = self.tab_widget.widget(idx)
            pos = curr_widget.find_next_in_file(text_to_find, SearchScope.SINGLE_FILE, from_top=True)

            if pos == -1:
                continue

            self.tab_widget.setCurrentIndex(idx)
            curr_widget.replace_next_in_file(text_to_find, text_to_replace, SearchScope.SINGLE_FILE)
            return

        QMessageBox.information(self, "Find/Replace", "Last tab has been reached. Text to replace couldn't be found.")

    def replace_all_in_all_open_tabs(self, text_to_find: str, text_to_replace: str):
        tab_count = self.tab_widget.count()

        for idx in range(tab_count):
            if self.is_game_properties_tab(idx):
                continue

            curr_tab: FileEditWidget = self.tab_widget.widget(idx)
            curr_tab.replace_all_in_file(text_to_find, text_to_replace)
        self._update_tab_modified_infos()

    def tabs_count(self) -> int:
        return self.tab_widget.count()

    def clear_tabs(self):
        self.tab_widget.clear()

    def restore_last_open_tabs(self, open_tabs: list[str], last_tab_index: int) -> list[str]:
        """Tries to restore last open tabs if there are any, and returns a list of missing files.
            :param open_tabs: List of previously opened tabs acquired from IDE settings
            :param last_tab_index: Last open tab's index acquired from IDE settings
            :return: A list of missing files (or an empty list if there are none)"""
        missing_tabs = []

        for tab_path in open_tabs:
            if tab_path == "Game Properties":
                self.open_game_properties_tab()
            elif Path(tab_path).exists() and Path(tab_path).is_file():
                self.open_new_editing_tab(tab_path)
            else:
                # File on tab_path is missing.
                missing_tabs.append(tab_path)
                last_tab_index -= 1

        if last_tab_index < 0:
            last_tab_index = 0

        self.tab_widget.setCurrentIndex(last_tab_index)

        # Emit files missing signal if there are any files missing
        return missing_tabs

    def apply_settings(self):
        self._try_loading_editor_theme(IDESettings.get_editor_color_theme())

        for idx in range(self.tabs_count()):
            if not self.is_game_properties_tab(idx):
                tab: FileEditWidget = self.tab_widget.widget(idx)
                tab.supply_font_properties_to_lexer(IDESettings.get_font_name(),
                                                    IDESettings.get_font_size(),
                                                    IDESettings.get_font_boldness())
                tab.supply_editor_color_theme_to_lexer()
                tab.setup_autocompletion()
                tab.set_highlight_style(IDESettings.get_highlight_fill_rect())

    def handle_insert_into_cursor(self, command: str):
        # Don't do anything if there are no tabs open
        if self.tab_widget.count() == 0:
            QMessageBox.critical(self, "Error", "There are no tabs open!")
            return

        # Don't do anything if Game Properties is open
        if self.is_game_properties_tab(self.tab_widget.currentIndex()):
            QMessageBox.critical(self, "Error", "Current tab is not a script editing tab!")
            return

        file_edit_widget: FileEditWidget = self.tab_widget.currentWidget()

        file_edit_widget.insert_at_cursor_position(command)

    def handle_game_icon_change_request(self, icon_path: str):
        # Don't do anything if there is no game selected
        if self.selected_game_info is None:
            QMessageBox.critical(self, "Error", "No game is selected!")
            return

        if self._game_properties_widget is not None:
            self._game_properties_widget.set_game_icon_path(icon_path)

    def _get_modified_files_tab_indexes(self) -> list[int]:
        result = []

        for i in range(self.tabs_count()):
            if self.is_game_properties_tab(i):
                continue

            tab: FileEditWidget = self.tab_widget.widget(i)

            if tab.is_file_modified():
                result.append(i)

        return result

    def attempt_closing_unsaved_tabs(self) -> bool:
        unsaved_tab_indexes = self._get_modified_files_tab_indexes()

        for idx in unsaved_tab_indexes:
            tab: FileEditWidget = self.tab_widget.widget(idx)

            result = self._ask_for_closing_tab(idx, len(unsaved_tab_indexes) > 1)

            if result == QMessageBox.StandardButton.Yes:
                tab.save_to_file()
            elif result == QMessageBox.StandardButton.YesToAll:
                self._save_all_modified_files(unsaved_tab_indexes)
                return True
            # QMessageBox.No will just ignore the current file, so no special handling for it.
            elif result == QMessageBox.StandardButton.NoToAll:
                return True
            elif result == QMessageBox.StandardButton.Cancel:
                return False

        return True

    def _save_all_modified_files(self, unsaved_tabs_indexes: list[int]):
        for idx in unsaved_tabs_indexes:
            tab: FileEditWidget = self.tab_widget.widget(idx)

            tab.save_to_file()

        self.update_save_button_requested.emit(False)
        self._update_tab_modified_infos()
