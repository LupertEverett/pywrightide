# Provides a directory view, and some ways to interact with the said directory.

from pathlib import Path

from PyQt5.QtWidgets import (QTreeView, QFileIconProvider, QFileSystemModel, QAction,
                             QWidget, QDockWidget, QHBoxLayout,
                             QLabel, QPushButton, QMenu,
                             QMessageBox, QInputDialog, QLineEdit)
from PyQt5.QtGui import QIcon, QMouseEvent, QDesktopServices
from PyQt5.QtCore import Qt, QModelIndex, pyqtSignal, QUrl

from .AddNewCaseDialog import AddNewCaseDialog
from data.PyWrightGame import PyWrightGame

import data.IconThemes as IconThemes

important_files = ("data.txt", "intro.txt", "evidence.txt")
non_sub_scriptable_extensions = (".mcro",
                                 ".examine.txt", ".move.txt", ".talk.txt", ".present.txt",
                                 "menu.txt", "menu.script.txt")
# Any folder that isn't these are gonna be treated as case folders (for now?)
non_case_folders = ("art", "music", "movies", "sfx")


class DirectoryViewWidget(QDockWidget):

    open_new_tab = pyqtSignal(str)
    open_game_properties_tab = pyqtSignal()
    file_renamed_from_directory_view = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Directory View")
        self.visibilityChanged.connect(self._handle_visibility_change)

        self._game_title_label = QLabel()

        game_properties_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_SETTINGS)
        self._game_properties_button = QPushButton(QIcon(game_properties_icon_path), "")
        self._game_properties_button.setToolTip("Game Properties")
        self._game_properties_button.setEnabled(False)
        self._game_properties_button.setFlat(True)
        self._game_properties_button.setMaximumWidth(30)
        self._game_properties_button.clicked.connect(self._handle_properties_button_clicked)

        self._directory_view = DeselectableTreeView()
        self._directory_view.doubleClicked.connect(self._handle_tree_view_double_clicked)
        self._directory_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._directory_view.customContextMenuRequested.connect(self._handle_view_context_menu)

        self._top_widget = self._create_custom_title_bar()

        self._pywright_game = PyWrightGame()

        self.setWidget(self._directory_view)
        self.setTitleBarWidget(self._create_custom_title_bar())
        self.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)
        self.setMinimumWidth(300)

    def update_directory_view(self, selected_game: PyWrightGame):
        fs_model = QFileSystemModel()
        icon_provider = QFileIconProvider()

        fs_model.setIconProvider(icon_provider)

        name_filter = ["*.txt", "*.mcro"]
        fs_model.setNameFilters(name_filter)
        fs_model.setNameFilterDisables(False)

        self._pywright_game = selected_game

        self._game_title_label.setText(self._pywright_game.get_game_name())

        self._directory_view.setModel(fs_model)
        self._directory_view.setRootIndex(fs_model.setRootPath(str(self._pywright_game.game_path)))
        self._directory_view.setIndentation(20)
        self._directory_view.setSortingEnabled(True)
        self._directory_view.sortByColumn(0, Qt.AscendingOrder)
        self._directory_view.header().hide()
        self._directory_view.hideColumn(1)
        self._directory_view.hideColumn(2)
        self._directory_view.hideColumn(3)

        self._game_properties_button.setEnabled(True)

    def clear_directory_view(self):
        self._directory_view.setModel(None)
        self._game_title_label.setText("")
        self._game_properties_button.setEnabled(False)

    def _handle_tree_view_double_clicked(self, index: QModelIndex):
        item_path = QFileSystemModel().filePath(index)
        if not Path(item_path).is_dir():
            self.open_new_tab.emit(item_path)

    def _create_custom_title_bar(self):
        result = QWidget()

        layout = QHBoxLayout()
        layout.addWidget(self._game_title_label)
        layout.addStretch()
        layout.addWidget(self._game_properties_button)
        layout.setContentsMargins(4, 2, 2, 2)

        result.setLayout(layout)
        return result

    def _handle_properties_button_clicked(self):
        self.open_game_properties_tab.emit()

    def _handle_view_context_menu(self, position):
        indexes = self._directory_view.selectedIndexes()

        if self._game_title_label.text() == "":
            return

        menu = QMenu()

        new_case_action = QAction("Add New Case", self)
        new_case_action.triggered.connect(self._handle_add_new_case_action)
        new_case_action.setStatusTip("Add a new case to the current game")

        new_script_action = QAction("Add New Script", self)
        new_script_action.triggered.connect(self._handle_new_script_action)
        new_script_action.setStatusTip("Add a new script to the selected case folder")

        open_dir_action = QAction("Open Folder in File Manager", self)
        open_dir_action.triggered.connect(self._handle_open_dir_action)
        open_dir_action.setStatusTip("Open selected folder in the default File Manager")

        rename_file_action = QAction("Rename", self)
        rename_file_action.triggered.connect(self._handle_rename_file_action)
        rename_file_action.setStatusTip("Rename selected item")

        remove_file_action = QAction("Remove", self)
        remove_file_action.triggered.connect(self._handle_remove_file_action)
        remove_file_action.setStatusTip("Remove selected item")

        create_examine_script_action = QAction("Create Examine Script", self)
        create_examine_script_action.triggered.connect(lambda: self._create_sub_script_file("examine"))
        create_examine_script_action.setStatusTip("Create Examine script for the selected scene")

        create_move_script_action = QAction("Create Move Script", self)
        create_move_script_action.triggered.connect(lambda: self._create_sub_script_file("move"))
        create_move_script_action.setStatusTip("Create Move script for the selected scene")

        create_present_script_action = QAction("Create Present Script", self)
        create_present_script_action.triggered.connect(lambda: self._create_sub_script_file("present"))
        create_present_script_action.setStatusTip("Create Present script for the selected scene")

        create_talk_script_action = QAction("Create Talk Script", self)
        create_talk_script_action.triggered.connect(lambda: self._create_sub_script_file("talk"))
        create_talk_script_action.setStatusTip("Create Talk script for the selected scene")

        if len(indexes) > 0:
            index = self._directory_view.selectedIndexes()[0]
            model: QFileSystemModel = index.model()

            file_name = model.fileName(index)

            if model.isDir(index) and model.fileName(index) not in non_case_folders:
                menu.addAction(new_script_action)
            elif file_name.endswith((".txt", ".mcro")) and file_name not in important_files:
                if not file_name.endswith(non_sub_scriptable_extensions):
                    menu.addAction(create_examine_script_action)
                    menu.addAction(create_move_script_action)
                    menu.addAction(create_present_script_action)
                    menu.addAction(create_talk_script_action)
                menu.addAction(rename_file_action)
                menu.addAction(remove_file_action)
            menu.addSeparator()
        menu.addAction(new_case_action)

        if len(indexes) == 0 or model.isDir(index):
            menu.addSeparator()
            menu.addAction(open_dir_action)

        menu.exec_(self._directory_view.mapToGlobal(position))

    def _handle_add_new_case_action(self):
        add_dialog = AddNewCaseDialog(self._pywright_game, self)

        if add_dialog.exec_():
            self._pywright_game.create_new_case(add_dialog.new_case)

    def _handle_new_script_action(self):
        index = self._directory_view.selectedIndexes()[0]
        model: QFileSystemModel = index.model()

        if not model.isDir(index):
            return

        dir_path = model.filePath(index)

        name, ok = QInputDialog.getText(self, "New Script", "Enter file name", QLineEdit.Normal)

        if ok and name != "":
            if not name.endswith((".mcro", ".txt")):
                name = name + ".txt"
            final_path = Path("{}/{}".format(dir_path, name))
            if final_path.exists():
                QMessageBox.critical(self, "Error", "File already exists!", QMessageBox.Ok)
                return

            with open(final_path, "x"):
                pass

    def _create_sub_script_file(self, sub_script_name: str):
        index = self._directory_view.selectedIndexes()[0]
        model: QFileSystemModel = index.model()

        dir_path = Path("{}/..".format(model.filePath(index)))
        file_name = model.fileName(index)

        # Analyze if the file has an extra .script suffix first
        script_name_sections = file_name.split(sep=".")

        if len(script_name_sections) < 2:
            return

        base_script_name = script_name_sections[0]

        resulting_script_name = base_script_name + "." + sub_script_name + ".txt"

        menu_script_name = base_script_name + "menu"
        menu_script_name += ("." + script_name_sections[1]) if script_name_sections[1].lower() == "script" else ""
        menu_script_name += ".txt"

        menu_script_full_path = dir_path/menu_script_name

        if not (menu_script_full_path.is_file() and menu_script_full_path.exists()):
            with open(menu_script_full_path, "x"):
                pass

        full_file_path = dir_path/resulting_script_name

        if full_file_path.exists() and full_file_path.is_file():
            QMessageBox.critical(self, "Error", "Script named \"{}\" already exists!".format(resulting_script_name),
                                 QMessageBox.Ok)
            return

        with open(full_file_path, "w"):
            pass

    def _handle_open_dir_action(self):
        if len(self._directory_view.selectedIndexes()) == 0:
            # Open the Game's root dir instead.
            QDesktopServices.openUrl(QUrl.fromLocalFile(self._pywright_game.game_path))
            return

        index = self._directory_view.selectedIndexes()[0]
        model: QFileSystemModel = index.model()
        dir_path = model.filePath(index)
        QDesktopServices.openUrl(QUrl.fromLocalFile(dir_path))

    def _handle_rename_file_action(self):
        if len(self._directory_view.selectedIndexes()) == 0:
            return

        index = self._directory_view.selectedIndexes()[0]
        model: QFileSystemModel = index.model()
        was_read_only = model.isReadOnly()
        old_name = model.fileName(index)
        
        dir_path = model.filePath(index)

        if old_name in important_files:
            QMessageBox.critical(self, "Error", "Important file \"{}\" cannot be renamed!".format(old_name),
                                 QMessageBox.Ok)
            return

        new_name, ok = QInputDialog.getText(self, "Rename File", "Enter file name",
                                            QLineEdit.Normal, old_name)

        if not ok:
            return

        if new_name == "":
            QMessageBox.critical(self, "Error", "Name cannot be empty!", QMessageBox.Ok)
            return

        if new_name == old_name:
            QMessageBox.critical(self, "Error", "New name cannot be the same as old name!", QMessageBox.Ok)
            return

        # dir_path contains the full path, including the name, so we gotta "move up" to get its directory.
        final_path = Path("{}/../{}".format(dir_path, new_name))

        if final_path.exists() and final_path.is_file():
            QMessageBox.critical(self, "Error", "File \"{}\" already exists!".format(final_path.name),
                                 QMessageBox.Ok)
            return

        model.setReadOnly(False)
        model.setData(index, new_name)
        model.setReadOnly(was_read_only)

    def _handle_remove_file_action(self):
        if len(self._directory_view.selectedIndexes()) == 0:
            return

        index = self._directory_view.selectedIndexes()[0]
        model: QFileSystemModel = index.model()

        if model.isDir(index):
            return

        file_name = model.fileName(index)

        if file_name in important_files:
            QMessageBox.critical(self, "Error", "Important file \"{}\" cannot be removed!".format(file_name),
                                 QMessageBox.Ok)
            return

        prompt = QMessageBox.question(self, "Question", "Are you sure you want to remove \"{}\"?".format(file_name),
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if prompt == QMessageBox.Yes:
            model.remove(index)

    def _handle_visibility_change(self):
        from .IDEMainWindow import IDEMainWindow
        ide_main_window: IDEMainWindow = self.parent()
        ide_main_window.update_toolbar_toggle_buttons()

class DeselectableTreeView(QTreeView):
    """Custom Tree View that has the ability to unselect items when clicked on an empty area"""
    def mousePressEvent(self, event: QMouseEvent):
        self.clearSelection()
        QTreeView.mousePressEvent(self, event)
