# IDE Main Window

from pathlib import Path

from PyQt5.QtWidgets import (QMainWindow, QWidget, QToolBar, QStatusBar,
                             QAction, QFileDialog, QLabel, QTabWidget, QMessageBox)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import Qt

from .NewGameDialog import NewGameDialog
from .OpenGameDialog import OpenGameDialog
from .FileEditWidget import FileEditWidget
from .GamePropertiesWidget import GamePropertiesWidget
from .DirectoryViewWidget import DirectoryViewWidget
from .PyWrightLoggerWidget import PyWrightLoggerWidget


class IDEMainWindow(QMainWindow):
    """Main Window of the PyWright IDE"""

    def __init__(self):
        super().__init__()

        # Instance-wide variables
        self.selected_pywright_installation = ""
        self.selected_game = ""
        self.pywright_executable_name = ""

        self.setWindowTitle("PyWright IDE")
        self.setWindowIcon(QIcon("res/icons/ideicon.png"))
        self.setMinimumSize(1024, 768)

        self.game_properties_widget = None  # Will be created later, when a PyWright root folder is selected

        self.directory_view = DirectoryViewWidget()
        self.logger_view = PyWrightLoggerWidget()
        self.logger_view.hide()

        self.directory_view.open_new_tab.connect(self.open_new_editing_tab)
        self.directory_view.open_game_properties_tab.connect(self.open_game_properties_tab)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self._handle_remove_tab)
        self.tab_widget.currentChanged.connect(self._handle_tab_change)

        # Actions
        self.new_pywright_game_action = QAction(QIcon("res/icons/newgame.png"), "New PyWright Game")
        self.new_pywright_game_action.setEnabled(False)
        self.new_pywright_game_action.setStatusTip("Create a new PyWright Game")
        self.new_pywright_game_action.triggered.connect(self._handle_new_game)
        self.new_pywright_game_action.setShortcut(QKeySequence("ctrl+n"))

        self.open_pywright_game_action = QAction(QIcon("res/icons/opengame.png"), "Open PyWright Game")
        self.open_pywright_game_action.setEnabled(False)
        self.open_pywright_game_action.setStatusTip("Open an existing PyWright Game")
        self.open_pywright_game_action.triggered.connect(self._handle_open_game)

        self.new_file_action = QAction(QIcon("res/icons/newfile.png"), "New file")
        self.new_file_action.setEnabled(False)
        self.new_file_action.setStatusTip("Create a new File")
        self.new_file_action.triggered.connect(lambda: self.open_new_editing_tab(""))
        self.new_file_action.setShortcut(QKeySequence("Ctrl+t"))

        self.open_file_action = QAction(QIcon("res/icons/openfile.png"), "Open File")
        self.open_file_action.triggered.connect(self._handle_open_file)
        self.open_file_action.setStatusTip("Open an existing file")
        self.open_file_action.setEnabled(False)
        self.open_file_action.setShortcut(QKeySequence("Ctrl+o"))

        self.save_file_action = QAction(QIcon("res/icons/save.png"), "Save File")
        self.save_file_action.setEnabled(False)
        self.save_file_action.setStatusTip("Save the file currently open")
        self.save_file_action.triggered.connect(self._handle_save_tab)
        self.save_file_action.setShortcut(QKeySequence("Ctrl+s"))

        self.run_pywright_action = QAction(QIcon("res/icons/runpywright.png"), "Run PyWright")
        self.run_pywright_action.setEnabled(False)
        self.run_pywright_action.setStatusTip("Run PyWright executable (none found)")
        self.run_pywright_action.triggered.connect(self._handle_run_pywright)

        self.about_action = QAction(QIcon("res/icons/gameproperties.png"), "About")
        self.about_action.setStatusTip("About PyWright")
        self.about_action.triggered.connect(self._handle_about)

        # Toolbar and the central widget
        self.addToolBar(self._create_top_toolbar())
        self.setCentralWidget(self.tab_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.directory_view)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.logger_view)

        # Status bar
        self.status_bar = QStatusBar()
        self.installation_path_label = QLabel("No PyWright folder selected")
        self.status_bar.addPermanentWidget(self.installation_path_label)

        self.setStatusBar(self.status_bar)

    def _create_top_toolbar(self) -> QToolBar:
        result = QToolBar(self)

        find_pywright_installation_action = QAction(QIcon("res/icons/pwicon.png"),
                                                    "Locate PyWright Installation",
                                                    result)
        find_pywright_installation_action.triggered.connect(self.handle_find_pywright_installation)
        find_pywright_installation_action.setStatusTip("Locate PyWright Installation Folder")
        find_pywright_installation_action.setShortcut(QKeySequence("Ctrl+l"))
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

        self.run_pywright_action.setParent(result)
        result.addAction(self.run_pywright_action)

        result.addSeparator()

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

            self.selected_pywright_installation = picker
            self.game_properties_widget = GamePropertiesWidget(self.selected_pywright_installation)
            self.directory_view.clear_directory_view()
            if self.tab_widget.count() > 0:
                self.tab_widget.clear()
            self.installation_path_label.setText(picker)
            self._pick_pywright_executable(picker)
            self.run_pywright_action.setStatusTip("Run PyWright executable ({})".format(self.pywright_executable_name))
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
        # Default to Windows, fallback to the generic py version.
        win_pywright = Path("{}/PyWright.exe".format(selected_directory))
        py_pywright = Path("{}/PyWright.py".format(selected_directory))

        if win_pywright.exists():
            self.pywright_executable_name = win_pywright.name
        elif py_pywright.exists():
            self.pywright_executable_name = py_pywright.name

    def _handle_new_game(self):
        new_game_dialog = NewGameDialog(self.selected_pywright_installation, self)

        if new_game_dialog.exec_():
            self._switch_to_selected_game(new_game_dialog.get_new_game_name())

    def _handle_open_game(self):
        if self.selected_pywright_installation == "":
            QMessageBox.critical(self, "Error", "PyWright root folder is not valid!")
            return

        open_game_dialog = OpenGameDialog(self.selected_pywright_installation, self)
        if open_game_dialog.exec_():
            self._switch_to_selected_game(open_game_dialog.selected_game)

    def _switch_to_selected_game(self, selected_game: str):
        """Switchs the IDE to the selected PyWright game, closing all open tabs in the process"""

        self.selected_game = selected_game
        game_path = str(Path("{}/games/{}".format(self.selected_pywright_installation, self.selected_game)))
        self.game_properties_widget.load_game(game_path)
        self.tab_widget.clear()
        self.directory_view.update_directory_view(game_path)
        self.open_game_properties_tab()
        self._update_toolbar_buttons()

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
        self.tab_widget.removeTab(index)
        self.tab_widget.setMovable(self.tab_widget.count() > 1)

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

    def _update_toolbar_buttons(self):
        has_pywright = self.selected_pywright_installation != ""
        has_pywright_game = self.selected_game != ""

        self.new_pywright_game_action.setEnabled(has_pywright)
        self.open_pywright_game_action.setEnabled(has_pywright)
        self.new_file_action.setEnabled(has_pywright_game)
        self.open_file_action.setEnabled(has_pywright_game)
        # Let's not enable the save button yet.
        self.run_pywright_action.setEnabled(has_pywright)

    def _handle_run_pywright(self):
        self.logger_view.show()
        self.logger_view.run_and_log(self.selected_pywright_installation, self.pywright_executable_name)

    def _handle_about(self):
        QMessageBox.about(self, "About PyWright IDE", "PyWright IDE by LupertEverett\n"
                                                      "This program aims to make developing PyWright games easier\n"
                                                      "Made with PyQt5 and QScintilla")
