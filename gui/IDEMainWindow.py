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
from data.PyWrightGame import PyWrightGameInfo


class IDEMainWindow(QMainWindow):
    """Main Window of the PyWright IDE"""

    def __init__(self, selected_game_path: str = ""):
        super().__init__()

        # Instance-wide variables
        self.selected_pywright_installation = ""  # Will be filled with game path
        self.selected_game_info: PyWrightGameInfo | None = None
        self.pywright_executable_name = ""

        if len(IDESettings.all_keys()) == 0:
            IDESettings.reset_settings()

        self.recent_folders = IDESettings.get_recent_games()

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

        # Try to load the last open game here, if the option is enabled, and the game folder still exists.
        if selected_game_path != "":
            self.pick_game_folder_and_open_game_properties_tab(Path(selected_game_path))
        elif IDESettings.get_autoload_last_game_check():
            autoload_path: str = IDESettings.get_autoload_last_game_path()
            if autoload_path != "" and PyWrightGameInfo.is_valid_game_folder(Path(autoload_path)):
                self.pick_game_folder(Path(autoload_path))

                # Also restore previously open tabs
                open_tabs = IDESettings.get_last_open_tabs()
                if len(open_tabs) > 0:
                    last_tab_index = IDESettings.get_last_open_tab_index()
                    self.restore_last_open_tabs(open_tabs)
                    self.central_widget.set_current_tab_index(last_tab_index)

        # Try loading the window state (docks positions, visibility, etc.)
        if IDESettings.window_state_data_exists():
            self.restoreState(IDESettings.get_window_state())

        # Apply the color theme
        self._apply_new_color_theme()

    def pick_game_folder(self, game_folder_path: Path):
        if self.central_widget.attempt_closing_unsaved_tabs():
            self.selected_game_info = PyWrightGameInfo.load_from_folder(game_folder_path)
            self.selected_pywright_installation = str(self.selected_game_info.pywright_folder_path)

            self.game_properties_widget = GamePropertiesWidget(self.selected_game_info)

            self.directory_view.clear_directory_view()
            if self.central_widget.tabs_count() > 0:
                self.central_widget.clear_tabs()

            self.installation_path_label.setText(self.selected_pywright_installation)

            self.pywright_executable_name = PyWrightFolder.pick_pywright_executable(self.selected_pywright_installation)
            self.central_widget.set_selected_game(self.selected_game_info)
            self._add_folder_to_recent(str(game_folder_path))
            self._top_toolbar.update_run_pywright_status_tip(self.pywright_executable_name)
            self._top_toolbar.update_toolbar_buttons(self.selected_pywright_installation != "",
                                                     self.selected_game_info.get_game_name() != "")
            self.asset_manager_widget.update_assets(self.selected_game_info)

            self.game_properties_widget.load_game(self.selected_game_info)

            self.directory_view.update_directory_view(self.selected_game_info)

            self.asset_manager_widget.update_assets(self.selected_game_info)

            self.setWindowTitle("PyWright IDE - {}".format(self.selected_game_info.game_title))

    def pick_game_folder_and_open_game_properties_tab(self, game_path: Path):
        self.pick_game_folder(game_path)
        self.central_widget.open_game_properties_tab(self.game_properties_widget)

    def _handle_new_game(self):
        new_game_dialog = NewGameDialog(self.selected_pywright_installation, self)

        if new_game_dialog.exec():
            self.pick_game_folder(new_game_dialog.get_new_game().game_path)

    def _handle_open_game(self):
        picker = QFileDialog.getExistingDirectory()

        if picker != "":
            # See if the user pointed to a game folder.
            # If that's the case, try to load it.
            if PyWrightGameInfo.is_valid_game_folder(Path(picker)):
                if self.attempt_closing_unsaved_tabs():
                    self.pick_game_folder_and_open_game_properties_tab(Path(picker))
                    self._top_toolbar.update_recent_folders_list()
            # See if the user pointed to a PyWright folder instead of a game folder.
            # Open the Open Game Dialog if that's the case.
            elif PyWrightFolder.is_valid_pywright_folder(picker) \
                    or PyWrightFolder.is_valid_pywright_folder(str(Path(picker).parent)):
                open_game_dialog = OpenGameDialog(picker, self)

                if open_game_dialog.exec():
                    if self.attempt_closing_unsaved_tabs():
                        game_path = Path(picker) / "games" / open_game_dialog.selected_game
                        self.pick_game_folder_and_open_game_properties_tab(game_path)
                        self._top_toolbar.update_recent_folders_list()
            else:
                QMessageBox.critical(self, "Error", "Invalid folder selected!")

    def _add_folder_to_recent(self, folder_path: str):
        for recent_folder_path in self.recent_folders:
            if folder_path == recent_folder_path:
                return
        self.recent_folders.append(folder_path)

    def _handle_open_file(self):
        open_dialog = QFileDialog.getOpenFileName(self, "Open File", str(self.selected_game_info.game_path),
                                                  "Text Files (*.txt)")

        if open_dialog[0] != "":
            self.central_widget.open_new_editing_tab(open_dialog[0])

    def _handle_find_replace(self):
        self.find_replace_dialog = FindReplaceDialog(self)
        self.find_replace_dialog.find_requested.connect(self.central_widget.handle_find_signals)
        self.find_replace_dialog.replace_requested.connect(self.central_widget.handle_replace_signals)
        self.find_replace_dialog.show()

    def _handle_game_icon_change_request(self, icon_path: str):
        # Don't do anything if there is no game selected
        if self.selected_game_info is None:
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

        self.recent_folders = IDESettings.get_recent_games()
        self._top_toolbar.update_recent_folders_list()

    def _apply_new_color_theme(self):
        self.setStyleSheet(ColorThemes.load_current_color_theme())

    def attempt_closing_unsaved_tabs(self) -> bool:
        return self.central_widget.attempt_closing_unsaved_tabs()

    def update_toolbar_buttons(self, has_pywright: bool, has_pywright_game: bool):
        self._top_toolbar.update_toolbar_buttons(has_pywright, has_pywright_game)

    def update_toolbar_toggle_buttons(self):
        self._top_toolbar.update_toolbar_toggle_buttons()

    def restore_last_open_tabs(self, open_tabs: list[str]):
        for tab_path in open_tabs:
            if tab_path == "Game Properties":
                self.central_widget.open_game_properties_tab(self.game_properties_widget)
            else:
                self.central_widget.open_new_editing_tab(tab_path)

    def closeEvent(self, event: QCloseEvent):
        if not self.central_widget.attempt_closing_unsaved_tabs():
            event.ignore()
            return

        # Always save the last open project's path and the selected game
        IDESettings.set_autoload_last_game_path(str(self.selected_game_info.game_path))
        IDESettings.set_recent_open_tabs(self.central_widget.get_open_tabs_paths())
        IDESettings.set_last_open_tab_index(self.central_widget.get_current_tab_index())

        IDESettings.set_recent_games(self.recent_folders)

        IDESettings.set_window_geometry(self.saveGeometry())
        IDESettings.set_window_state(self.saveState())

        self.asset_manager_widget.deinit()
        event.accept()
