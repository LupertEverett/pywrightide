# IDE Main Window

from pathlib import Path

from PyQt6.QtWidgets import (QMainWindow, QStatusBar, QFileDialog, QLabel, QMessageBox)
from PyQt6.QtGui import QIcon, QCloseEvent
from PyQt6.QtCore import Qt

from .MainWindowTopToolbar import MainWindowTopToolbar
from .MainWindowCentralWidget import MainWindowCentralWidget
from .NewGameDialog import NewGameDialog
from .OpenGameDialog import OpenGameDialog
from .GamePropertiesWidget import GamePropertiesWidget
from .DirectoryViewWidget import DirectoryViewWidget
from .PyWrightLoggerWidget import PyWrightLoggerWidget
from .SettingsDialog import SettingsDialog
from .FindReplaceDialog import FindReplaceDialog
from .AssetBrowserRootWidget import AssetBrowserRootWidget

from data import IDESettings, ColorThemes, PyWrightFolder
from data.PyWrightGame import PyWrightGame


class IDEMainWindow(QMainWindow):
    """Main Window of the PyWright IDE"""

    def __init__(self, selected_pywright_path: str = ""):
        super().__init__()

        # Instance-wide variables
        self.selected_pywright_installation = selected_pywright_path
        self.selected_game = PyWrightGame()
        self.pywright_executable_name = ""

        if len(IDESettings.all_keys()) == 0:
            IDESettings.reset_settings()

        self.recent_folders = IDESettings.get_recent_docs()

        self.setWindowTitle("PyWright IDE")
        self.setWindowIcon(QIcon("res/icons/ideicon.png"))
        self.setMinimumSize(720, 540)
        if IDESettings.window_geometry_data_exists():
            self.restoreGeometry(IDESettings.get_window_geometry())

        self.game_properties_widget = None  # Will be created later, when a PyWright root folder is selected

        self.directory_view = DirectoryViewWidget(self)
        self.asset_manager_widget = AssetBrowserRootWidget(self)
        self.logger_view = PyWrightLoggerWidget()
        self.logger_view.hide()

        self.asset_manager_widget.texture_browser\
            .command_insert_at_cursor_requested.connect(self._handle_insert_into_cursor)
        self.asset_manager_widget.texture_browser\
            .game_icon_change_requested.connect(self._handle_game_icon_change_request)
        self.asset_manager_widget.music_browser\
            .command_insert_at_cursor_requested.connect(self._handle_insert_into_cursor)
        self.asset_manager_widget.sfx_browser \
            .command_insert_at_cursor_requested.connect(self._handle_insert_into_cursor)

        self.central_widget = MainWindowCentralWidget(self)

        self._top_toolbar = MainWindowTopToolbar(self)
        self._top_toolbar.new_pywright_game_action.triggered.connect(self._handle_new_game)
        self._top_toolbar.open_pywright_game_action.triggered.connect(self._handle_open_game)
        self._top_toolbar.new_file_action.triggered.connect(lambda: self.central_widget.open_new_editing_tab(""))
        self._top_toolbar.open_file_action.triggered.connect(self._handle_open_file)
        self._top_toolbar.save_file_action.triggered.connect(self.central_widget.handle_save_tab)
        self._top_toolbar.find_replace_dialog_action.triggered.connect(self._handle_find_replace)
        self._top_toolbar.settings_action.triggered.connect(self._handle_settings)

        self.central_widget.update_save_button_requested.connect(self._top_toolbar.update_save_button)

        self.directory_view.open_new_tab.connect(self.central_widget.open_new_editing_tab)
        self.directory_view.open_game_properties_tab.connect(
            lambda: self.central_widget.open_game_properties_tab(self.game_properties_widget)
        )

        # Toolbar and the central widget
        self.addToolBar(self._top_toolbar)
        self.setCentralWidget(self.central_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.directory_view)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.asset_manager_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.logger_view)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        self.installation_path_label = QLabel("No PyWright folder selected")
        self.installation_path_label.setContentsMargins(0, 4, 12, 4)
        self.status_bar.addPermanentWidget(self.installation_path_label)

        self.setStatusBar(self.status_bar)

        # Macros tracking
        self._pywright_builtin_macros: list[str] = []

        # Try to load the last open project here, if the option is enabled, and the project folder still exists.
        if IDESettings.get_autoload_last_project_check():
            autoload_path: str = IDESettings.get_autoload_last_project_path()
            if autoload_path != "" and Path(autoload_path).exists() and Path(autoload_path).is_dir():
                self.pick_pywright_installation_folder(autoload_path)
                autoload_game_name: str = IDESettings.get_autoload_last_game_name()
                if autoload_game_name != "":
                    # Check if it is an actual game folder within the selected PyWright installation
                    game_path = Path("{}/games/{}".format(autoload_path, autoload_game_name))
                    if game_path.exists() and game_path.is_dir():
                        self._switch_to_selected_game(autoload_game_name)
                    else:
                        IDESettings.set_autoload_last_game_name("")
        elif self.selected_pywright_installation != "":
            self.pick_pywright_installation_folder(self.selected_pywright_installation)

        # Try loading the window state (docks positions, visibility, etc.)
        if IDESettings.window_state_data_exists():
            self.restoreState(IDESettings.get_window_state())

        # Apply the color theme
        self._apply_new_color_theme()

    def pick_pywright_installation_folder(self, folder_path: str):
        self.selected_pywright_installation = folder_path
        self.game_properties_widget = GamePropertiesWidget(self.selected_pywright_installation)
        self.directory_view.clear_directory_view()
        if self.central_widget.tabs_count() > 0:
            self.central_widget.clear_tabs()
        self.installation_path_label.setText(folder_path)
        self.pywright_executable_name = PyWrightFolder.pick_pywright_executable(folder_path)
        self._parse_builtin_macros(folder_path)
        self.central_widget.set_pywright_installation_path(self.selected_pywright_installation)
        self.central_widget.load_builtin_macros(self._pywright_builtin_macros)
        self._add_pywright_folder_to_recent(folder_path)
        self._top_toolbar.update_run_pywright_status_tip(self.pywright_executable_name)
        self._top_toolbar.update_toolbar_buttons(self.selected_pywright_installation != "",
                                                 self.selected_game.get_game_name() != "")
        self.asset_manager_widget.clear_everything()

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

    def _add_pywright_folder_to_recent(self, folder_path: str):
        for recent_folder_path in self.recent_folders:
            if folder_path == recent_folder_path:
                return
        self.recent_folders.append(folder_path)

    def _switch_to_selected_game(self, selected_game: str):
        """Switches the IDE to the selected PyWright game, closing all open tabs in the process

        :param selected_game: Name of the selected PyWright game."""

        if self.central_widget.attempt_closing_unsaved_tabs():
            self.selected_game.load_game(Path("{}/games/{}".format(self.selected_pywright_installation, selected_game)))
            self.game_properties_widget.load_game(self.selected_game)
            self.central_widget.clear_tabs()
            self.central_widget.set_selected_game(self.selected_game)
            self.directory_view.update_directory_view(self.selected_game)
            self.central_widget.open_game_properties_tab(self.game_properties_widget)
            self._top_toolbar.update_toolbar_buttons(self.selected_pywright_installation != "",
                                                     self.selected_game.get_game_name() != "")
            self.asset_manager_widget.update_assets(self.selected_pywright_installation, self.selected_game)

    def _handle_open_file(self):
        open_dialog = QFileDialog.getOpenFileName(self, "Open File",
                                                  str(Path("{}/games/{}".format(self.selected_pywright_installation,
                                                                                self.selected_game.get_game_name()))),
                                                  "Text Files (*.txt)"
                                                  )

        if open_dialog[0] != "":
            self.central_widget.open_new_editing_tab(open_dialog[0])

    def _handle_find_replace(self):
        self.find_replace_dialog = FindReplaceDialog(self)
        self.find_replace_dialog.find_requested.connect(self.central_widget.handle_find_signals)
        self.find_replace_dialog.replace_requested.connect(self.central_widget.handle_replace_signals)
        self.find_replace_dialog.show()

    def _handle_game_icon_change_request(self, icon_path: str):
        # Don't do anything if there is no game selected
        if not self.selected_game.is_a_game_selected():
            QMessageBox.critical(self, "Error", "No game is selected!")
            return

        self.game_properties_widget.set_game_icon_path(icon_path)

    def _handle_insert_into_cursor(self, command: str):
        self.central_widget.handle_insert_into_cursor(command)

    def _handle_settings(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.settings_changed.connect(self._apply_settings)
        settings_dialog.exec()

    def _apply_settings(self):
        self.central_widget.apply_settings()
        self._apply_new_color_theme()
        self._top_toolbar.update_toolbar_icons()

    def _apply_new_color_theme(self):
        self.setStyleSheet(ColorThemes.load_current_color_theme())

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

    def attempt_closing_unsaved_tabs(self) -> bool:
        return self.central_widget.attempt_closing_unsaved_tabs()

    def update_toolbar_buttons(self, has_pywright: bool, has_pywright_game: bool):
        self._top_toolbar.update_toolbar_buttons(has_pywright, has_pywright_game)

    def update_toolbar_toggle_buttons(self):
        self._top_toolbar.update_toolbar_toggle_buttons()

    def closeEvent(self, event: QCloseEvent):
        if not self.central_widget.attempt_closing_unsaved_tabs():
            event.ignore()
            return

        # Always save the last open project's path and the selected game
        IDESettings.set_autoload_last_project_path(self.selected_pywright_installation)
        IDESettings.set_autoload_last_game_name(self.selected_game.get_game_name())

        IDESettings.set_recent_docs(self.recent_folders)

        IDESettings.set_window_geometry(self.saveGeometry())
        IDESettings.set_window_state(self.saveState())

        self.asset_manager_widget.deinit()
        event.accept()
