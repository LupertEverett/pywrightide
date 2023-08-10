# Main Window Toolbar
# Contains stuff like "New File", "Load File", etc.

from PyQt5.QtWidgets import QToolBar, QAction, QWidget, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon, QKeySequence

import gui.IDEMainWindow
import data.IconThemes as IconThemes


class MainWindowTopToolbar(QToolBar):

    # Cannot use MainWindow as parent's type as it causes a circular import error
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setWindowTitle("Main Toolbar")
        self.setObjectName("MainToolbar")
        self.setMovable(False)
        # We must not be able to disable the toolbar
        self.toggleViewAction().setEnabled(False)
        self.toggleViewAction().setVisible(False)

        # For easier access to the Main Window we're attached to
        self.ide_main_window: gui.IDEMainWindow.IDEMainWindow = parent

        find_pywright_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_FIND_PYWRIGHT)
        self.find_pywright_installation_action = QAction(QIcon(find_pywright_icon_path),
                                                         "Locate PyWright Installation",
                                                         self)
        self.find_pywright_installation_action.triggered.connect(self.handle_find_pywright_installation)
        self.find_pywright_installation_action.setShortcut(QKeySequence("Ctrl+l"))
        self.find_pywright_installation_action.setStatusTip("Locate PyWright Installation Folder [{}]".format(
            self.find_pywright_installation_action.shortcut().toString()
        ))

        # Actions
        new_game_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_NEW_GAME)
        self.new_pywright_game_action = QAction(QIcon(new_game_icon_path), "New PyWright Game")
        self.new_pywright_game_action.setEnabled(False)
        # self.new_pywright_game_action.triggered.connect(self._handle_new_game)
        self.new_pywright_game_action.setShortcut(QKeySequence("Ctrl+n"))
        self.new_pywright_game_action.setStatusTip("Create a new PyWright Game [{}]".format(
            self.new_pywright_game_action.shortcut().toString()
        ))

        open_game_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_OPEN_GAME)
        self.open_pywright_game_action = QAction(QIcon(open_game_icon_path), "Open PyWright Game")
        self.open_pywright_game_action.setEnabled(False)
        # self.open_pywright_game_action.triggered.connect(self._handle_open_game)
        self.open_pywright_game_action.setShortcut(QKeySequence("Ctrl+Shift+o"))
        self.open_pywright_game_action.setStatusTip("Open an existing PyWright Game [{}]".format(
            self.open_pywright_game_action.shortcut().toString()
        ))

        new_file_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_NEW_FILE)
        self.new_file_action = QAction(QIcon(new_file_icon_path), "New File")
        self.new_file_action.setEnabled(False)
        # self.new_file_action.triggered.connect(lambda: self.open_new_editing_tab(""))
        self.new_file_action.setShortcut(QKeySequence("Ctrl+t"))
        self.new_file_action.setStatusTip("Create a new File [{}]".format(
            self.new_file_action.shortcut().toString()
        ))

        open_file_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_OPEN_FILE)
        self.open_file_action = QAction(QIcon(open_file_icon_path), "Open File")
        # self.open_file_action.triggered.connect(self._handle_open_file)
        self.open_file_action.setEnabled(False)
        self.open_file_action.setShortcut(QKeySequence("Ctrl+o"))
        self.open_file_action.setStatusTip("Open an existing File [{}]".format(
            self.open_file_action.shortcut().toString()
        ))

        save_file_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_SAVE_FILE)
        self.save_file_action = QAction(QIcon(save_file_icon_path), "Save File")
        self.save_file_action.setEnabled(False)
        # self.save_file_action.triggered.connect(self._handle_save_tab)
        self.save_file_action.setShortcut(QKeySequence("Ctrl+s"))
        self.save_file_action.setStatusTip("Save the currently open File [{}]".format(
            self.save_file_action.shortcut().toString()
        ))

        find_replace_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_FIND_REPLACE)
        self.find_replace_dialog_action = QAction(QIcon(find_replace_icon_path), "Find/Replace")
        # self.find_replace_dialog_action.triggered.connect(self._handle_find_replace)
        self.find_replace_dialog_action.setShortcut(QKeySequence("Ctrl+f"))
        self.find_replace_dialog_action.setStatusTip("Find/Replace words [{}]".format(
            self.find_replace_dialog_action.shortcut().toString()
        ))

        directory_view_toggle_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_DIRECTORY_VIEW_TOGGLE)
        self.directory_view_toggle_action = QAction(QIcon(directory_view_toggle_icon_path), "Toggle Directory View")
        self.directory_view_toggle_action.setCheckable(True)
        self.directory_view_toggle_action.setChecked(not self.ide_main_window.directory_view.isHidden())
        self.directory_view_toggle_action.triggered.connect(lambda: self.ide_main_window.directory_view.setVisible(
            self.directory_view_toggle_action.isChecked()
        ))
        self.directory_view_toggle_action.setStatusTip("Toggle Directory View ON or OFF")

        asset_browser_toggle_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_ASSET_BROWSER_TOGGLE)
        self.asset_browser_toggle_action = QAction(QIcon(asset_browser_toggle_icon_path), "Toggle Asset Browser")
        self.asset_browser_toggle_action.setCheckable(True)
        self.asset_browser_toggle_action.setChecked(not self.ide_main_window.asset_manager_widget.isHidden())
        self.asset_browser_toggle_action.triggered.connect(lambda: self.ide_main_window.asset_manager_widget.setVisible(
            self.asset_browser_toggle_action.isChecked()
        ))
        self.asset_browser_toggle_action.setStatusTip("Toggle Asset Browser ON or OFF")

        logger_toggle_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_LOGGER_TOGGLE)
        self.logger_toggle_action = QAction(QIcon(logger_toggle_icon_path), "Toggle Logger View")
        self.logger_toggle_action.setCheckable(True)
        self.logger_toggle_action.setChecked(not self.ide_main_window.logger_view.isHidden())
        self.logger_toggle_action.triggered.connect(lambda: self.ide_main_window.logger_view.setVisible(
            self.logger_toggle_action.isChecked()
        ))
        self.logger_toggle_action.setStatusTip("Toggle Logger View ON or OFF")

        run_pywright_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_RUN_PYWRIGHT)
        self.run_pywright_action = QAction(QIcon(run_pywright_icon_path), "Run PyWright")
        self.run_pywright_action.setEnabled(False)
        self.run_pywright_action.triggered.connect(self._handle_run_pywright)
        self.run_pywright_action.setShortcut(QKeySequence("Ctrl+r"))
        self.run_pywright_action.setStatusTip("Run PyWright executable (none found) [{}]".format(
            self.run_pywright_action.shortcut().toString()
        ))

        settings_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_SETTINGS)
        self.settings_action = QAction(QIcon(settings_icon_path), "Settings")
        self.settings_action.setStatusTip("Open Settings")
        # self.settings_action.triggered.connect(self._handle_settings)

        about_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_ABOUT)
        self.about_action = QAction(QIcon(about_icon_path), "About")
        self.about_action.setStatusTip("About PyWright IDE")
        self.about_action.triggered.connect(self._handle_about)

        # TODO: Perhaps a "Command dictionary" button, that is for checking thru all the available commands for scripts.

        self.addAction(self.find_pywright_installation_action)
        self.addSeparator()
        self.addAction(self.new_pywright_game_action)
        self.addAction(self.open_pywright_game_action)
        self.addSeparator()
        self.addAction(self.new_file_action)
        self.addAction(self.open_file_action)
        self.addAction(self.save_file_action)
        self.addSeparator()
        self.addAction(self.find_replace_dialog_action)
        self.addSeparator()
        self.addAction(self.directory_view_toggle_action)
        self.addAction(self.asset_browser_toggle_action)
        self.addAction(self.logger_toggle_action)
        self.addSeparator()
        self.addAction(self.run_pywright_action)
        self.addSeparator()
        self.addAction(self.settings_action)
        self.addAction(self.about_action)

    def handle_find_pywright_installation(self):
        """Prompts the user for a folder and determines if the selected folder is a valid PyWright folder"""
        picker = QFileDialog.getExistingDirectory()

        if picker != "":
            if not self.ide_main_window.check_legit_pywright(picker):
                QMessageBox.critical(self, "Error", "Could not find a PyWright installation")
                return

            if self.ide_main_window.attempt_closing_unsaved_tabs():
                self.ide_main_window.pick_pywright_installation_folder(picker)

    def _handle_run_pywright(self):
        self.ide_main_window.logger_view.show()
        self.logger_toggle_action.setChecked(True)  # Since we open the logger, makes sense to set this checked also
        self.ide_main_window.logger_view.run_and_log(self.ide_main_window.selected_pywright_installation,
                                                     self.ide_main_window.pywright_executable_name)

    def update_run_pywright_status_tip(self, executable_name: str):
        self.run_pywright_action.setStatusTip(
            "Run PyWright executable ({}) [{}]".format(
                executable_name,
                self.run_pywright_action.shortcut().toString()
            )
        )

    def update_toolbar_buttons(self, has_pywright: bool, has_pywright_game: bool):
        self.new_pywright_game_action.setEnabled(has_pywright)
        self.open_pywright_game_action.setEnabled(has_pywright)
        self.new_file_action.setEnabled(has_pywright_game)
        self.open_file_action.setEnabled(has_pywright_game)
        # Let's not enable the save button yet, and handle it in update_save_button() instead.
        self.run_pywright_action.setEnabled(has_pywright)
        self.update_toolbar_toggle_buttons()

    def update_toolbar_toggle_buttons(self):
        self.directory_view_toggle_action.setChecked(self.ide_main_window.directory_view.isVisible())
        self.asset_browser_toggle_action.setChecked(self.ide_main_window.asset_manager_widget.isVisible())
        self.logger_toggle_action.setChecked(self.ide_main_window.logger_view.isVisible())

    def update_toolbar_icons(self):
        find_pywright_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_FIND_PYWRIGHT)
        self.find_pywright_installation_action.setIcon(QIcon(find_pywright_icon_path))

        new_game_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_NEW_GAME)
        self.new_pywright_game_action.setIcon(QIcon(new_game_icon_path))

        open_game_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_OPEN_GAME)
        self.open_pywright_game_action.setIcon(QIcon(open_game_icon_path))

        new_file_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_NEW_FILE)
        self.new_file_action.setIcon(QIcon(new_file_icon_path))

        open_file_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_OPEN_FILE)
        self.open_file_action.setIcon(QIcon(open_file_icon_path))

        save_file_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_SAVE_FILE)
        self.save_file_action.setIcon(QIcon(save_file_icon_path))

        find_replace_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_FIND_REPLACE)
        self.find_replace_dialog_action.setIcon(QIcon(find_replace_icon_path))

        directory_view_toggle_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_DIRECTORY_VIEW_TOGGLE)
        self.directory_view_toggle_action.setIcon(QIcon(directory_view_toggle_icon_path))

        asset_browser_toggle_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_ASSET_BROWSER_TOGGLE)
        self.asset_browser_toggle_action.setIcon(QIcon(asset_browser_toggle_icon_path))

        logger_toggle_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_LOGGER_TOGGLE)
        self.logger_toggle_action.setIcon(QIcon(logger_toggle_icon_path))

        run_pywright_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_RUN_PYWRIGHT)
        self.run_pywright_action.setIcon(QIcon(run_pywright_icon_path))

        settings_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_SETTINGS)
        self.settings_action.setIcon(QIcon(settings_icon_path))

        about_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_ABOUT)
        self.about_action.setIcon(QIcon(about_icon_path))

    def update_save_button(self, is_file_modified: bool):
        """Updates the Save File button depending on whether the currently open tab has the file modified or not.
        :param is_file_modified: Represents the condition of whether the file is modified or not. Should be False if
        the current tab is NOT a file editor tab."""
        self.save_file_action.setEnabled(is_file_modified)

    def _handle_about(self):
        QMessageBox.about(self, "About PyWright IDE", "<h1>PyWright IDE</h1><h2>Prerelease version (23.08.10)</h2>\n"
                                                      "<h3>by LupertEverett</h3>\n"
                                                      "This program aims to make developing PyWright games easier\n"
                                                      "Made with PyQt5, QScintilla and pygame")
