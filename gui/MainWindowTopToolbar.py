# Main Window Toolbar
# Contains stuff like "New File", "Load File", etc.

from PyQt5.QtWidgets import QToolBar, QAction, QWidget, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon, QKeySequence

import gui.IDEMainWindow


class MainWindowTopToolbar(QToolBar):

    # Cannot use MainWindow as parent's type as it causes a circular import error
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setWindowTitle("Main Toolbar")
        self.setMovable(False)

        # For easier access to the Main Window we're attached to
        self.ide_main_window: gui.IDEMainWindow.IDEMainWindow = parent

        self.find_pywright_installation_action = QAction(QIcon("res/icons/pwicon.png"),
                                                         "Locate PyWright Installation",
                                                         self)
        self.find_pywright_installation_action.triggered.connect(self.handle_find_pywright_installation)
        self.find_pywright_installation_action.setShortcut(QKeySequence("Ctrl+l"))
        self.find_pywright_installation_action.setStatusTip("Locate PyWright Installation Folder [{}]".format(
            self.find_pywright_installation_action.shortcut().toString()
        ))

        # Actions
        self.new_pywright_game_action = QAction(QIcon("res/icons/newgame.png"), "New PyWright Game")
        self.new_pywright_game_action.setEnabled(False)
        # self.new_pywright_game_action.triggered.connect(self._handle_new_game)
        self.new_pywright_game_action.setShortcut(QKeySequence("Ctrl+n"))
        self.new_pywright_game_action.setStatusTip("Create a new PyWright Game [{}]".format(
            self.new_pywright_game_action.shortcut().toString()
        ))

        self.open_pywright_game_action = QAction(QIcon("res/icons/opengame.png"), "Open PyWright Game")
        self.open_pywright_game_action.setEnabled(False)
        # self.open_pywright_game_action.triggered.connect(self._handle_open_game)
        self.open_pywright_game_action.setShortcut(QKeySequence("Ctrl+Shift+o"))
        self.open_pywright_game_action.setStatusTip("Open an existing PyWright Game [{}]".format(
            self.open_pywright_game_action.shortcut().toString()
        ))

        self.new_file_action = QAction(QIcon("res/icons/newfile.png"), "New File")
        self.new_file_action.setEnabled(False)
        # self.new_file_action.triggered.connect(lambda: self.open_new_editing_tab(""))
        self.new_file_action.setShortcut(QKeySequence("Ctrl+t"))
        self.new_file_action.setStatusTip("Create a new File [{}]".format(
            self.new_file_action.shortcut().toString()
        ))

        self.open_file_action = QAction(QIcon("res/icons/openfile.png"), "Open File")
        # self.open_file_action.triggered.connect(self._handle_open_file)
        self.open_file_action.setEnabled(False)
        self.open_file_action.setShortcut(QKeySequence("Ctrl+o"))
        self.open_file_action.setStatusTip("Open an existing File [{}]".format(
            self.open_file_action.shortcut().toString()
        ))

        self.save_file_action = QAction(QIcon("res/icons/save.png"), "Save File")
        self.save_file_action.setEnabled(False)
        # self.save_file_action.triggered.connect(self._handle_save_tab)
        self.save_file_action.setShortcut(QKeySequence("Ctrl+s"))
        self.save_file_action.setStatusTip("Save the currently open File [{}]".format(
            self.save_file_action.shortcut().toString()
        ))

        self.find_replace_dialog_action = QAction(QIcon("res/icons/Binoculars.png"), "Find/Replace")
        # self.find_replace_dialog_action.triggered.connect(self._handle_find_replace)
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
        # self.settings_action.triggered.connect(self._handle_settings)

        self.about_action = QAction(QIcon("res/icons/gameproperties.png"), "About")
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

    def update_save_button(self, is_file_modified: bool):
        """Updates the Save File button depending on whether the currently open tab has the file modified or not.
        :param is_file_modified: Represents the condition of whether the file is modified or not. Should be False if
        the current tab is NOT a file editor tab."""
        self.save_file_action.setEnabled(is_file_modified)

    def _handle_about(self):
        QMessageBox.about(self, "About PyWright IDE", "<h1>PyWright IDE</h1><h2>Prerelease version</h2>\n"
                                                      "<h3>by LupertEverett</h3>\n"
                                                      "This program aims to make developing PyWright games easier\n"
                                                      "Made with PyQt5 and QScintilla")
