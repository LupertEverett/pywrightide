# IDE Main Window

from pathlib import Path

from PyQt5.QtWidgets import (QMainWindow, QWidget, QToolBar, QStatusBar, QAction,
                             QFileDialog, QLabel, QTabWidget, QMessageBox)
from PyQt5.QtGui import QIcon, QKeySequence, QCloseEvent
from PyQt5.QtCore import Qt, QSettings

from .NewGameDialog import NewGameDialog
from .OpenGameDialog import OpenGameDialog
from .FileEditWidget import FileEditWidget
from .GamePropertiesWidget import GamePropertiesWidget
from .DirectoryViewWidget import DirectoryViewWidget
from .PyWrightLoggerWidget import PyWrightLoggerWidget
from .SettingsDialog import SettingsDialog
from .FindReplaceDialog import FindReplaceDialog, SearchScope, FindType, ReplaceType
from .AssetBrowserRootWidget import AssetBrowserRootWidget

from data import IDESettings
from data.PyWrightGame import PyWrightGame


class IDEMainWindow(QMainWindow):
    """Main Window of the PyWright IDE"""

    def __init__(self):
        super().__init__()

        # Instance-wide variables
        self.selected_pywright_installation = ""
        self.selected_game = PyWrightGame()
        self.pywright_executable_name = ""

        self.program_settings = QSettings("PyWrightIDE", "PyWrightIDE")
        if len(self.program_settings.allKeys()) == 0:
            self._default_settings()

        self.setWindowTitle("PyWright IDE")
        self.setWindowIcon(QIcon("res/icons/ideicon.png"))
        self.setMinimumSize(1024, 768)
        if self.program_settings.value(IDESettings.WINDOW_GEOMETRY_KEY) is not None:
            self.restoreGeometry(bytes(self.program_settings.value(IDESettings.WINDOW_GEOMETRY_KEY)))

        self.game_properties_widget = None  # Will be created later, when a PyWright root folder is selected

        self.directory_view = DirectoryViewWidget(self)
        self.asset_manager_widget = AssetBrowserRootWidget(self)
        self.logger_view = PyWrightLoggerWidget()
        self.logger_view.hide()

        self.directory_view.open_new_tab.connect(self.open_new_editing_tab)
        self.directory_view.open_game_properties_tab.connect(self.open_game_properties_tab)

        self.asset_manager_widget.texture_browser\
            .command_insert_at_cursor_requested.connect(self._handle_insert_into_cursor)
        self.asset_manager_widget.texture_browser\
            .game_icon_change_requested.connect(self._handle_game_icon_change_request)
        self.asset_manager_widget.music_browser\
            .command_insert_at_cursor_requested.connect(self._handle_insert_into_cursor)
        self.asset_manager_widget.sfx_browser \
            .command_insert_at_cursor_requested.connect(self._handle_insert_into_cursor)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self._handle_remove_tab)
        self.tab_widget.currentChanged.connect(self._handle_tab_change)

        # Actions
        self.new_pywright_game_action = QAction(QIcon("res/icons/newgame.png"), "New PyWright Game")
        self.new_pywright_game_action.setEnabled(False)
        self.new_pywright_game_action.triggered.connect(self._handle_new_game)
        self.new_pywright_game_action.setShortcut(QKeySequence("Ctrl+n"))
        self.new_pywright_game_action.setStatusTip("Create a new PyWright Game [{}]".format(
            self.new_pywright_game_action.shortcut().toString()
        ))

        self.open_pywright_game_action = QAction(QIcon("res/icons/opengame.png"), "Open PyWright Game")
        self.open_pywright_game_action.setEnabled(False)
        self.open_pywright_game_action.triggered.connect(self._handle_open_game)
        self.open_pywright_game_action.setShortcut(QKeySequence("Ctrl+Shift+o"))
        self.open_pywright_game_action.setStatusTip("Open an existing PyWright Game [{}]".format(
            self.open_pywright_game_action.shortcut().toString()
        ))

        self.new_file_action = QAction(QIcon("res/icons/newfile.png"), "New File")
        self.new_file_action.setEnabled(False)
        self.new_file_action.triggered.connect(lambda: self.open_new_editing_tab(""))
        self.new_file_action.setShortcut(QKeySequence("Ctrl+t"))
        self.new_file_action.setStatusTip("Create a new File [{}]".format(
            self.new_file_action.shortcut().toString()
        ))

        self.open_file_action = QAction(QIcon("res/icons/openfile.png"), "Open File")
        self.open_file_action.triggered.connect(self._handle_open_file)
        self.open_file_action.setEnabled(False)
        self.open_file_action.setShortcut(QKeySequence("Ctrl+o"))
        self.open_file_action.setStatusTip("Open an existing File [{}]".format(
            self.open_file_action.shortcut().toString()
        ))

        self.save_file_action = QAction(QIcon("res/icons/save.png"), "Save File")
        self.save_file_action.setEnabled(False)
        self.save_file_action.triggered.connect(self._handle_save_tab)
        self.save_file_action.setShortcut(QKeySequence("Ctrl+s"))
        self.save_file_action.setStatusTip("Save the currently open File [{}]".format(
            self.save_file_action.shortcut().toString()
        ))

        self.find_replace_dialog_action = QAction(QIcon("res/icons/Binoculars.png"), "Find/Replace")
        self.find_replace_dialog_action.triggered.connect(self._handle_find_replace)
        self.find_replace_dialog_action.setShortcut(QKeySequence("Ctrl+f"))
        self.find_replace_dialog_action.setStatusTip("Find/Replace words [{}]".format(
            self.find_replace_dialog_action.shortcut().toString()
        ))

        self.run_pywright_action = QAction(QIcon("res/icons/runpywright.png"), "Run PyWright")
        self.run_pywright_action.setEnabled(False)
        self.run_pywright_action.triggered.connect(self._handle_run_pywright)
        self.run_pywright_action.setShortcut(QKeySequence("Ctrl+r"))
        self.run_pywright_action.setStatusTip("Run PyWright executable (none found) [{}]".format(
            self.run_pywright_action.shortcut().toString()
        ))

        self.settings_action = QAction(QIcon("res/icons/cog.png"), "Settings")
        self.settings_action.setStatusTip("Open Settings")
        self.settings_action.triggered.connect(self._handle_settings)

        self.about_action = QAction(QIcon("res/icons/gameproperties.png"), "About")
        self.about_action.setStatusTip("About PyWright IDE")
        self.about_action.triggered.connect(self._handle_about)

        # Toolbar and the central widget
        self.addToolBar(self._create_top_toolbar())
        self.setCentralWidget(self.tab_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.directory_view)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.asset_manager_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.logger_view)

        # Status bar
        self.status_bar = QStatusBar()
        self.installation_path_label = QLabel("No PyWright folder selected")
        self.status_bar.addPermanentWidget(self.installation_path_label)

        self.setStatusBar(self.status_bar)

        # Macros tracking
        self._pywright_builtin_macros: list[str] = []
        self._game_macros: list[str] = []

        # Try to load the last open project here, if the option is enabled, and the project folder still exists.
        if self.program_settings.value(IDESettings.AUTOLOAD_LAST_PROJECT_KEY, False, bool):
            autoload_path: str = self.program_settings.value(IDESettings.AUTOLOAD_LAST_PROJECT_PATH_KEY, "")
            if autoload_path != "" and Path(autoload_path).exists() and Path(autoload_path).is_dir():
                self._pick_pywright_installation_folder(autoload_path)
                autoload_game_name: str = self.program_settings.value(IDESettings.AUTOLOAD_LAST_GAME_NAME_KEY, "")
                if autoload_game_name != "":
                    self._switch_to_selected_game(autoload_game_name)

    def _create_top_toolbar(self) -> QToolBar:
        result = QToolBar(self)
        result.setWindowTitle("Main Toolbar")

        find_pywright_installation_action = QAction(QIcon("res/icons/pwicon.png"),
                                                    "Locate PyWright Installation",
                                                    result)
        find_pywright_installation_action.triggered.connect(self.handle_find_pywright_installation)
        find_pywright_installation_action.setShortcut(QKeySequence("Ctrl+l"))
        find_pywright_installation_action.setStatusTip("Locate PyWright Installation Folder [{}]".format(
            find_pywright_installation_action.shortcut().toString()
        ))
        result.addAction(find_pywright_installation_action)

        result.addSeparator()

        self.new_pywright_game_action.setParent(result)
        result.addAction(self.new_pywright_game_action)

        self.open_pywright_game_action.setParent(result)
        result.addAction(self.open_pywright_game_action)

        # TODO: Perhaps a "Command dictionary" button, that is for checking thru all the available commands for scripts.

        result.addSeparator()

        self.new_file_action.setParent(result)
        result.addAction(self.new_file_action)

        self.open_file_action.setParent(result)
        result.addAction(self.open_file_action)

        self.save_file_action.setParent(result)
        result.addAction(self.save_file_action)

        result.addSeparator()

        self.find_replace_dialog_action.setParent(result)
        result.addAction(self.find_replace_dialog_action)

        result.addSeparator()

        self.run_pywright_action.setParent(result)
        result.addAction(self.run_pywright_action)

        result.addSeparator()

        self.settings_action.setParent(result)
        result.addAction(self.settings_action)

        self.about_action.setParent(result)
        result.addAction(self.about_action)

        result.setMovable(False)
        return result

    def handle_find_pywright_installation(self):
        """Prompts the user for a folder and determines if the selected folder is a valid PyWright folder"""
        picker = QFileDialog.getExistingDirectory()

        if picker != "":
            if not self.check_legit_pywright(picker):
                QMessageBox.critical(self, "Error", "Could not find a PyWright installation")
                return

            if self._attempt_closing_unsaved_tabs():
                self._pick_pywright_installation_folder(picker)

    def _pick_pywright_installation_folder(self, folder_path: str):
        self.selected_pywright_installation = folder_path
        self.game_properties_widget = GamePropertiesWidget(self.selected_pywright_installation)
        self.directory_view.clear_directory_view()
        if self.tab_widget.count() > 0:
            self.tab_widget.clear()
        self.installation_path_label.setText(folder_path)
        self._pick_pywright_executable(folder_path)
        self._parse_builtin_macros(folder_path)
        self.run_pywright_action.setStatusTip(
            "Run PyWright executable ({}) [{}]".format(
                self.pywright_executable_name,
                self.run_pywright_action.shortcut().toString()
            )
        )
        self._update_toolbar_buttons()

    def check_legit_pywright(self, selected_directory) -> bool:
        """Returns true if the selected folder is a valid PyWright directory."""

        return Path("{}/games".format(selected_directory)).exists() \
               and Path("{}/art".format(selected_directory)).exists() \
               and Path("{}/core".format(selected_directory)).exists() \
               and self._check_legit_pywright_executables(selected_directory)

    def _check_legit_pywright_executables(self, selected_directory) -> bool:
        # Let's not handle macOS PyWright yet...
        return Path("{}/PyWright.exe".format(selected_directory)).exists() \
               or Path("{}/PyWright.py".format(selected_directory)).exists()

    def _pick_pywright_executable(self, selected_directory):
        """Picks a PyWright executable from the selected_directory.

        :param selected_directory: Selected Directory, must be the root folder of the PyWright installation."""
        # Default to Windows, fallback to the generic py version.
        win_pywright = Path("{}/PyWright.exe".format(selected_directory))
        py_pywright = Path("{}/PyWright.py".format(selected_directory))

        if win_pywright.exists():
            self.pywright_executable_name = win_pywright.name
        elif py_pywright.exists():
            self.pywright_executable_name = py_pywright.name

    def _handle_new_game(self):
        new_game_dialog = NewGameDialog(self.selected_pywright_installation, self)

        if new_game_dialog.exec():
            self._switch_to_selected_game(new_game_dialog.get_new_game_name())

    def _handle_open_game(self):
        if self.selected_pywright_installation == "":
            QMessageBox.critical(self, "Error", "PyWright root folder is not valid!")
            return

        open_game_dialog = OpenGameDialog(self.selected_pywright_installation, self)
        if open_game_dialog.exec():
            self._switch_to_selected_game(open_game_dialog.selected_game)

    def _switch_to_selected_game(self, selected_game: str):
        """Switches the IDE to the selected PyWright game, closing all open tabs in the process

        :param selected_game: Name of the selected PyWright game."""

        if self._attempt_closing_unsaved_tabs():
            self.selected_game.set_game_path("{}/games/{}".format(self.selected_pywright_installation, selected_game))
            # TODO: Gradually switch from strings to PyWrightGame instances
            # game_path = str(Path("{}/games/{}".format(self.selected_pywright_installation, self.selected_game)))
            self.game_properties_widget.load_game(self.selected_game.game_path)
            self.tab_widget.clear()
            self.directory_view.update_directory_view(self.selected_game.game_path)
            self._parse_game_macros()
            self.open_game_properties_tab()
            self._update_toolbar_buttons()
            self.asset_manager_widget.update_assets(self.selected_pywright_installation, self.selected_game)

    def _handle_open_file(self):
        open_dialog = QFileDialog.getOpenFileName(self, "Open File",
                                                  str(Path("{}/games/{}".format(self.selected_pywright_installation,
                                                                                self.selected_game))),
                                                  "Text Files (*.txt)"
                                                  )

        if open_dialog[0] != "":
            self.open_new_editing_tab(open_dialog[0])

    def open_new_editing_tab(self, file_path: str):
        # Create a new FileEditWidget, and add it to the tab widget
        file_edit_widget = FileEditWidget(self.selected_pywright_installation, file_path)
        file_edit_widget.file_name_changed.connect(self._handle_rename_tab)
        file_edit_widget.file_modified.connect(self._update_save_button)
        file_edit_widget.supply_builtin_macros_to_lexer(self._pywright_builtin_macros)
        file_edit_widget.supply_game_macros_to_lexer(self._game_macros)
        file_edit_widget.move_to_tab_requested.connect(self._handle_move_to_tab)
        file_edit_widget.replace_next_in_next_tabs_requested.connect(self.replace_next_in_next_tabs)
        file_name = Path(file_path).name
        self._open_new_tab(file_edit_widget, file_name if file_name != "" else "New File")

    def open_game_properties_tab(self):
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == "Game Properties":
                # We already have a Game Properties tab open, so switch to that instead.
                self.tab_widget.setCurrentIndex(i)
                return

        self._open_new_tab(self.game_properties_widget, "Game Properties")

    def _open_new_tab(self, tab_widget: QWidget, tab_title: str):
        self.tab_widget.addTab(tab_widget, tab_title)
        self.tab_widget.setMovable(self.tab_widget.count() > 1)
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)

    def _handle_rename_tab(self, new_name: str):
        self.tab_widget.setTabText(self.tab_widget.currentIndex(), new_name)

    def _handle_remove_tab(self, index):
        if self.tab_widget.tabText(index) != "Game Properties":
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

    def _handle_save_tab(self):
        if self.tab_widget.tabText(self.tab_widget.currentIndex()) != "Game Properties":
            self.tab_widget.currentWidget().save_to_file()
            self._update_save_button()

    def _handle_tab_change(self, index: int):
        condition = self.tab_widget.count() > 0 and \
                    self.tab_widget.tabText(index) != "Game Properties" and \
                    self.tab_widget.currentWidget().is_file_modified()

        self.save_file_action.setEnabled(condition)

    def _update_save_button(self):
        condition = self.tab_widget.currentWidget().is_file_modified()

        self.save_file_action.setEnabled(condition)
        tab_text = self.tab_widget.currentWidget().file_name
        # Prepend a * to the tab name if the file is modified
        self.tab_widget.setTabText(self.tab_widget.currentIndex(), "*" + tab_text if condition else tab_text)

    def _update_tab_modified_infos(self):
        # Like _update_save_button() but for all tabs
        for idx in range(self.tab_widget.count()):
            if self.tab_widget.tabText(idx) == "Game Properties":
                continue

            condition = self.tab_widget.currentWidget().is_file_modified()
            tab_text = self.tab_widget.currentWidget().file_name
            # Prepend a * to the tab name if the file is modified
            self.tab_widget.setTabText(idx, "*" + tab_text if condition else tab_text)

    def _update_toolbar_buttons(self):
        has_pywright = self.selected_pywright_installation != ""
        has_pywright_game = self.selected_game != ""

        self.new_pywright_game_action.setEnabled(has_pywright)
        self.open_pywright_game_action.setEnabled(has_pywright)
        self.new_file_action.setEnabled(has_pywright_game)
        self.open_file_action.setEnabled(has_pywright_game)
        # Let's not enable the save button yet.
        self.run_pywright_action.setEnabled(has_pywright)

    def _handle_find_replace(self):
        self.find_replace_dialog = FindReplaceDialog(self)
        self.find_replace_dialog.find_requested.connect(self._handle_find_signals)
        self.find_replace_dialog.replace_requested.connect(self._handle_replace_signals)
        self.find_replace_dialog.show()

    def _handle_find_signals(self, text: str, find_type: FindType, search_scope: SearchScope):
        if self.tab_widget.count() == 0:
            # If nothing is open, inform the user and do nothing.
            QMessageBox.information(self, "Find/Replace", "There are no tabs open.")
            return
        if self.tab_widget.tabText(self.tab_widget.currentIndex()) != "Game Properties":
            file_widget: FileEditWidget = self.tab_widget.currentWidget()
            file_widget.search_in_file(text, find_type, search_scope)

    def _handle_replace_signals(self, text_to_find: str, text_to_replace: str, replace_type: ReplaceType, search_scope: SearchScope):
        if self.tab_widget.count() == 0:
            # If nothing is open, inform the user and do nothing.
            QMessageBox.information(self, "Find/Replace", "There are no tabs open.")
            return
        if replace_type == ReplaceType.REPLACE_ALL and search_scope == SearchScope.OPEN_TABS:
            self.replace_all_in_all_open_tabs(text_to_find, text_to_replace)
            return
        if self.tab_widget.tabText(self.tab_widget.currentIndex()) != "Game Properties":
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
            if self.tab_widget.tabText(idx) == "Game Properties":
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
            if self.tab_widget.tabText(idx) == "Game Properties":
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
            QMessageBox.information(self, "Find/Replace", "Last tab has been reached. Text to replace couldn't be found.")
            return

        for idx in range(current_position + 1, tabs_count):
            if self.tab_widget.tabText(idx) == "Game Properties":
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
            if self.tab_widget.tabText(idx) == "Game Properties":
                continue

            curr_tab: FileEditWidget = self.tab_widget.widget(idx)
            curr_tab.replace_all_in_file(text_to_find, text_to_replace)
        self._update_tab_modified_infos()

    def _handle_run_pywright(self):
        self.logger_view.show()
        self.logger_view.run_and_log(self.selected_pywright_installation, self.pywright_executable_name)

    def _handle_game_icon_change_request(self, icon_path: str):
        # Don't do anything if there is no game selected
        if not self.selected_game.is_a_game_selected():
            QMessageBox.critical(self, "Error", "No game is selected!")
            return

        self.game_properties_widget.set_game_icon_path(icon_path)

    def _handle_insert_into_cursor(self, command: str):
        # Don't do anything if there are no tabs open
        if self.tab_widget.count() == 0:
            QMessageBox.critical(self, "Error", "There are no tabs open!")
            return

        tab_index = self.tab_widget.currentIndex()

        # Don't do anything if Game Properties is open
        if self.tab_widget.tabText(tab_index) == "Game Properties":
            QMessageBox.critical(self, "Error", "Current tab is not a script editing tab!")
            return

        file_edit_widget: FileEditWidget = self.tab_widget.currentWidget()

        file_edit_widget.insert_at_cursor_position(command)

    def _handle_settings(self):
        settings_dialog = SettingsDialog(self.program_settings, self)
        settings_dialog.settings_changed.connect(self._apply_settings)
        settings_dialog.exec()

    def _apply_settings(self):
        for idx in range(self.tab_widget.count()):
            if self.tab_widget.tabText(idx) != "Game Properties":
                tab: FileEditWidget = self.tab_widget.widget(idx)
                tab.supply_font_properties_to_lexer(self.program_settings.value(IDESettings.FONT_NAME_KEY),
                                                    int(self.program_settings.value(IDESettings.FONT_SIZE_KEY)),
                                                    self.program_settings.value(IDESettings.FONT_BOLD_KEY, True, bool))

    def _handle_about(self):
        QMessageBox.about(self, "About PyWright IDE", "PyWright IDE by LupertEverett\n"
                                                      "This program aims to make developing PyWright games easier\n"
                                                      "Made with PyQt5 and QScintilla")

    def _parse_builtin_macros(self, pywright_install_dir: str):
        core_macros_dir = Path("{}/core/macros".format(pywright_install_dir))
        if not (core_macros_dir.exists() and core_macros_dir.is_dir()):
            raise FileNotFoundError("core/macros dir does not exist!")

        # Get a list of the .mcro files
        macro_files_list = list(core_macros_dir.glob("*.mcro"))

        self._pywright_builtin_macros.clear()

        for macro_file_name in macro_files_list:
            with open(macro_file_name, "r", encoding="UTF-8") as f:
                lines = f.readlines()

                for line in lines:
                    if line.startswith("macro "):
                        splitted_lines = line.split(maxsplit=1)
                        self._pywright_builtin_macros.append(splitted_lines[1])

    def _parse_game_macros(self):
        # game_path = Path("{}/games/{}".format(self.selected_pywright_installation, self.selected_game))
        game_path = Path("{}".format(self.selected_game.game_path))

        if not (game_path.exists() and game_path.is_dir()):
            raise FileNotFoundError("Selected game doesn't exist!")

        macro_files_list = game_path.glob("*.mcro")

        self._game_macros.clear()

        for macro_file_name in macro_files_list:
            with open(macro_file_name, "r", encoding="UTF-8") as f:
                lines = f.readlines()

                for line in lines:
                    if line.startswith("macro "):
                        splitted_lines = line.split(maxsplit=1)
                        self._game_macros.append(splitted_lines[1])

    def _save_all_modified_files(self, unsaved_tabs_indexes: list[int]):
        for idx in unsaved_tabs_indexes:
            tab: FileEditWidget = self.tab_widget.widget(idx)

            tab.save_to_file()

        self._update_save_button()

    def _get_modified_files_tab_indexes(self) -> list[int]:
        result = []

        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == "Game Properties":
                continue

            tab: FileEditWidget = self.tab_widget.widget(i)

            if tab.is_file_modified():
                result.append(i)

        return result

    def _attempt_closing_unsaved_tabs(self) -> bool:
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

    def _default_settings(self):
        self.program_settings.setValue(IDESettings.FONT_NAME_KEY, "Consolas")
        self.program_settings.setValue(IDESettings.FONT_SIZE_KEY, 10)
        self.program_settings.setValue(IDESettings.FONT_BOLD_KEY, True)
        self.program_settings.setValue(IDESettings.AUTOLOAD_LAST_PROJECT_KEY, False)
        self.program_settings.setValue(IDESettings.AUTOLOAD_LAST_PROJECT_PATH_KEY, "")
        self.program_settings.setValue(IDESettings.AUTOLOAD_LAST_GAME_NAME_KEY, "")
        self.program_settings.setValue(IDESettings.WINDOW_GEOMETRY_KEY, None)

    def _save_settings(self):
        self.program_settings.sync()

    def closeEvent(self, event: QCloseEvent):
        if not self._attempt_closing_unsaved_tabs():
            event.ignore()
            return

        # Save the last open project's path in here, if the autoload last project option is enabled
        if self.program_settings.value(IDESettings.AUTOLOAD_LAST_PROJECT_KEY, False):
            self.program_settings.setValue(IDESettings.AUTOLOAD_LAST_PROJECT_PATH_KEY,
                                           self.selected_pywright_installation)
            self.program_settings.setValue(IDESettings.AUTOLOAD_LAST_GAME_NAME_KEY, self.selected_game.get_game_name())
        else:
            # Otherwise clear the paths, just in case
            self.program_settings.setValue(IDESettings.AUTOLOAD_LAST_PROJECT_PATH_KEY, "")
            self.program_settings.setValue(IDESettings.AUTOLOAD_LAST_GAME_NAME_KEY, "")

        self.program_settings.setValue(IDESettings.WINDOW_GEOMETRY_KEY, self.saveGeometry())

        self.asset_manager_widget.deinit()
        event.accept()
