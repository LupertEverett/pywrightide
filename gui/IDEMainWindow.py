# IDE Main Window

from pathlib import Path

from PyQt6.QtWidgets import (QMainWindow, QStatusBar, QFileDialog, QLabel, QMessageBox)
from PyQt6.QtGui import QIcon, QCloseEvent
from PyQt6.QtCore import Qt

from .MainWindowTopToolbar import MainWindowTopToolbar
from .MainWindowCentralWidget import MainWindowCentralWidget
from .WelcomeWidget import WelcomeWidget
from .MainWindowStatusBar import MainWindowStatusBar
from .NewGameDialog import NewGameDialog
from .OpenGameDialog import OpenGameDialog
from .DirectoryViewWidget import DirectoryViewWidget
from .PyWrightLoggerWidget import PyWrightLoggerWidget
from .CharacterViewerDialog import CharacterViewerDialog
from .SettingsDialog import SettingsDialog
from .FindReplaceDialog import FindReplaceDialog
from .AssetBrowserRootWidget import AssetBrowserRootWidget
from .FileEditWidget import FileEditWidget
from .MissingFilesDialog import MissingFilesDialog
from .AboutDialog import about_pywright_ide

from data import IDESettings, ColorThemes, PyWrightFolder
from data.PyWrightGame import PyWrightGameInfo, CurrentPyWrightGame


current_pywright_game = CurrentPyWrightGame()


class IDEMainWindow(QMainWindow):
    """Main Window of the PyWright IDE"""

    def __init__(self, selected_game_path: str = ""):
        super().__init__()

        if len(IDESettings.all_keys()) == 0:
            IDESettings.reset_settings()

        self.recent_folders = IDESettings.get_recent_games()

        self.setWindowTitle("PyWright IDE")
        self.setWindowIcon(QIcon("res/icons/ideicon.png"))
        self.setMinimumSize(720, 540)
        if IDESettings.window_geometry_data_exists() and IDESettings.get_settings_version() is not None:
            self.restoreGeometry(IDESettings.get_window_geometry())

        self.directory_view = DirectoryViewWidget(self)
        self.asset_manager_widget = AssetBrowserRootWidget(self)
        self.logger_view = PyWrightLoggerWidget()
        self.logger_view.hide()

        self.welcome_widget = WelcomeWidget(self)
        self.welcome_widget.game_path_selected.connect(self.pick_game_folder_and_open_game_properties_tab)
        self.welcome_widget.settings_selected.connect(self._handle_settings)
        self.welcome_widget.about_selected.connect(lambda: about_pywright_ide(self))

        self.central_widget = MainWindowCentralWidget(self)

        self.asset_manager_widget.texture_browser\
            .command_insert_at_cursor_requested.connect(self._handle_insert_into_cursor)
        self.asset_manager_widget.texture_browser\
            .game_icon_change_requested.connect(self.central_widget.handle_game_icon_change_request)
        self.asset_manager_widget.music_browser\
            .command_insert_at_cursor_requested.connect(self._handle_insert_into_cursor)
        self.asset_manager_widget.sfx_browser \
            .command_insert_at_cursor_requested.connect(self._handle_insert_into_cursor)

        self._top_toolbar = MainWindowTopToolbar(self)
        self._top_toolbar.new_pywright_game_action.triggered.connect(self._handle_new_game)
        self._top_toolbar.open_pywright_game_action.triggered.connect(self._handle_open_game)
        self._top_toolbar.new_file_action.triggered.connect(lambda: self.central_widget.open_new_editing_tab(""))
        self._top_toolbar.open_file_action.triggered.connect(self._handle_open_file)
        self._top_toolbar.save_file_action.triggered.connect(self.central_widget.handle_save_tab)
        self._top_toolbar.character_viewer_action.triggered.connect(self._handle_character_viewer)
        self._top_toolbar.find_replace_dialog_action.triggered.connect(self._handle_find_replace)
        self._top_toolbar.settings_action.triggered.connect(self._handle_settings)

        # Status bar
        self.status_bar = MainWindowStatusBar(self)
        self.setStatusBar(self.status_bar)

        self.central_widget.update_save_button_requested.connect(self._top_toolbar.update_save_button)
        self.central_widget.current_tab_cursor_position_changed.connect(self.status_bar.set_cursor_position_info)
        self.central_widget.selection_length_changed.connect(self.status_bar.set_selection_length_info)

        self.directory_view.open_new_tab.connect(self.central_widget.open_new_editing_tab)
        self.directory_view.open_game_properties_tab.connect(
            lambda: self.central_widget.open_game_properties_tab()
        )

        # Toolbar and the central widget
        self.addToolBar(self._top_toolbar)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.directory_view)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.asset_manager_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.logger_view)

        # Try loading the window state (docks positions, visibility, etc.)
        if IDESettings.window_state_data_exists() and IDESettings.get_settings_version() is not None:
            self.restoreState(IDESettings.get_window_state())

        self._is_directory_view_hidden = not IDESettings.get_show_directory_view()
        self._is_asset_browser_hidden = not IDESettings.get_show_asset_browser()
        self._is_logger_view_hidden = not IDESettings.get_show_logger_view()

        game_open_condition = selected_game_path != "" and Path(selected_game_path).exists() and Path(selected_game_path).is_dir()

        # Try to load the last open game here, if the option is enabled, and the game folder still exists.
        if game_open_condition:
            self.pick_game_folder(Path(selected_game_path))

            # Also restore previously open tabs
            open_tabs = IDESettings.get_last_open_tabs()
            if len(open_tabs) > 0:
                last_tab_index = IDESettings.get_last_open_tab_index()
                missing_files = self.central_widget.restore_last_open_tabs(open_tabs, last_tab_index)

                if len(missing_files) > 0:
                    missing_files_dialog = MissingFilesDialog(self, missing_files)
                    missing_files_dialog.exec()
            else:
                self.central_widget.open_game_properties_tab()
        else:
            self.setCentralWidget(self.welcome_widget)
            self.central_widget.hide()
            self._top_toolbar.hide()
            self.status_bar.hide()
            self.directory_view.hide()
            self.logger_view.hide()
            self.asset_manager_widget.hide()

        # Apply the color theme
        self._apply_new_color_theme()

    def switch_to_editor_mode(self):
        self.welcome_widget.hide()
        self.central_widget.show()
        self.setCentralWidget(self.central_widget)
        self._top_toolbar.show()
        self.status_bar.show()
        self.directory_view.setVisible(not self._is_directory_view_hidden)
        self.asset_manager_widget.setVisible(not self._is_asset_browser_hidden)
        self.logger_view.setVisible(not self._is_logger_view_hidden)

        self.directory_view.visibilityChanged.connect(self._handle_directory_view_visibility_change)
        self.asset_manager_widget.visibilityChanged.connect(self._handle_asset_browser_visibility_change)
        self.logger_view.visibilityChanged.connect(self._handle_logger_view_visibility_change)

    def _handle_directory_view_visibility_change(self):
        self._is_directory_view_hidden = self.directory_view.isHidden()

    def _handle_asset_browser_visibility_change(self):
        self._is_asset_browser_hidden = self.asset_manager_widget.isHidden()

    def _handle_logger_view_visibility_change(self):
        self._is_logger_view_hidden = self.logger_view.isHidden()

    def pick_game_folder(self, game_folder_path: Path):
        if self.central_widget.attempt_closing_unsaved_tabs():
            current_pywright_game.set_current_game(PyWrightGameInfo.load_from_folder(game_folder_path))

            self.directory_view.clear_directory_view()
            if self.central_widget.tabs_count() > 0:
                self.central_widget.clear_tabs()

            self.switch_to_editor_mode()
            self.status_bar.set_installation_path_info(str(current_pywright_game.current_pywright_folder_path))

            self.central_widget.set_selected_game(current_pywright_game.current_game)
            self._add_folder_to_recent(str(game_folder_path))
            self._top_toolbar.update_run_pywright_status_tip(current_pywright_game.current_pywright_executable_name)
            self._top_toolbar.update_toolbar_buttons(current_pywright_game.current_pywright_folder_path != "",
                                                     current_pywright_game.current_game.get_game_name() != "")
            self.asset_manager_widget.update_assets(current_pywright_game.current_game)

            self.directory_view.update_directory_view(current_pywright_game.current_game)

            self.asset_manager_widget.update_assets(current_pywright_game.current_game)

            self.setWindowTitle("PyWright IDE - {}".format(current_pywright_game.current_game.game_title))

    def pick_game_folder_and_open_game_properties_tab(self, game_path: Path):
        self.pick_game_folder(game_path)
        self.central_widget.open_game_properties_tab()

    def _handle_new_game(self):
        new_game_dialog = NewGameDialog(str(current_pywright_game.current_pywright_folder_path), self)

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
        self.recent_folders.insert(0, folder_path)

    def _handle_open_file(self):
        open_dialog = QFileDialog.getOpenFileName(self, "Open File", str(current_pywright_game.current_game.game_path),
                                                  "Text Files (*.txt)")

        if open_dialog[0] != "":
            self.central_widget.open_new_editing_tab(open_dialog[0])

    def _handle_find_replace(self):
        string_to_find = ""
        if self.central_widget.tab_widget.count() > 0 and not self.central_widget.is_game_properties_tab(self.central_widget.tab_widget.currentIndex()):
            file_edit_widget: FileEditWidget = self.central_widget.tab_widget.currentWidget()
            string_to_find = file_edit_widget.sci.selectedText()
        self.find_replace_dialog = FindReplaceDialog(string_to_find, self)
        self.find_replace_dialog.find_requested.connect(self.central_widget.handle_find_signals)
        self.find_replace_dialog.replace_requested.connect(self.central_widget.handle_replace_signals)
        self.find_replace_dialog.show()

    def _handle_insert_into_cursor(self, command: str):
        self.central_widget.handle_insert_into_cursor(command)

    def _handle_character_viewer(self):
        char_viewer = CharacterViewerDialog(self)
        char_viewer.command_insert_at_cursor_requested.connect(self._handle_insert_into_cursor)

        char_viewer.show()

    def _handle_settings(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.settings_changed.connect(self._apply_settings)
        settings_dialog.exec()

    def _apply_settings(self):
        self.central_widget.apply_settings()
        self.welcome_widget.set_autoload_checkbox_ticked(IDESettings.get_autoload_last_game_check())
        self._apply_new_color_theme()
        self._top_toolbar.update_toolbar_icons()

        self.recent_folders = IDESettings.get_recent_games()
        self._top_toolbar.update_recent_folders_list()

    def _apply_new_color_theme(self):
        try:
            stylesheet = ColorThemes.load_current_color_theme()
        except FileNotFoundError:
            theme_name = IDESettings.get_color_theme()
            QMessageBox.information(self, "Color Theme Not Found",
                                    "PyWright IDE couldn't find the color theme <b>{}</b>!<br>Resetting back to system theme.".format(
                                        theme_name),
                                    QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
            IDESettings.set_color_theme("System Theme")
            stylesheet = ""

        self.setStyleSheet(stylesheet)

    def attempt_closing_unsaved_tabs(self) -> bool:
        return self.central_widget.attempt_closing_unsaved_tabs()

    def update_toolbar_buttons(self, has_pywright: bool, has_pywright_game: bool):
        self._top_toolbar.update_toolbar_buttons(has_pywright, has_pywright_game)

    def update_toolbar_toggle_buttons(self):
        self._top_toolbar.update_toolbar_toggle_buttons()

    def handle_open_image_viewer_request(self, image_path: str):
        self.central_widget.open_image_viewer_tab(Path(image_path))

    def closeEvent(self, event: QCloseEvent):
        if not self.central_widget.attempt_closing_unsaved_tabs():
            event.ignore()
            return

        # Always save the last open project's path and the selected game
        if current_pywright_game.current_game is not None:
            IDESettings.set_autoload_last_game_path(str(current_pywright_game.current_game.game_path))
            IDESettings.set_recent_open_tabs(self.central_widget.get_open_tabs_paths())
            IDESettings.set_last_open_tab_index(self.central_widget.get_current_tab_index())

        IDESettings.set_recent_games(self.recent_folders)

        IDESettings.set_window_geometry(self.saveGeometry())
        IDESettings.set_window_state(self.saveState())

        IDESettings.set_show_directory_view(not self._is_directory_view_hidden)
        IDESettings.set_show_asset_browser(not self._is_asset_browser_hidden)
        IDESettings.set_show_logger_view(not self._is_logger_view_hidden)

        self.asset_manager_widget.deinit()
        IDESettings.save_settings()
        event.accept()
