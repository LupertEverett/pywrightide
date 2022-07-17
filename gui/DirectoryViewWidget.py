# Provides a directory view, and some ways to interact with the said directory.

from pathlib import Path

from PyQt5.QtWidgets import (QTreeView, QFileSystemModel, QFileIconProvider,
                             QWidget, QDockWidget, QHBoxLayout,
                             QLabel, QPushButton, QMenu, QAction, QMessageBox)
from PyQt5.QtGui import QIcon, QMouseEvent, QDesktopServices
from PyQt5.QtCore import Qt, QModelIndex, pyqtSignal, QUrl

from .AddNewCaseDialog import AddNewCaseDialog
from data.PyWrightGame import PyWrightGame


class DirectoryViewWidget(QDockWidget):

    open_new_tab = pyqtSignal(str)
    open_game_properties_tab = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._game_title_label = QLabel()

        self._game_properties_button = QPushButton(QIcon("res/icons/gameproperties.png"), "")
        self._game_properties_button.setToolTip("Game Properties")
        self._game_properties_button.setEnabled(False)
        self._game_properties_button.setFlat(True)
        self._game_properties_button.setMaximumWidth(30)
        self._game_properties_button.clicked.connect(self._handle_properties_button_clicked)

        self._directory_view = DeselectableTreeView()
        self._directory_view.doubleClicked.connect(self._handle_tree_view_double_clicked)
        self._directory_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._directory_view.customContextMenuRequested.connect(self._handle_view_context_menu)

        self._pywright_game = PyWrightGame()

        self.setWidget(self._directory_view)
        self.setTitleBarWidget(self._create_custom_title_bar())
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.setMinimumWidth(300)

    def update_directory_view(self, game_root_path: str):
        fs_model = QFileSystemModel()
        icon_provider = QFileIconProvider()

        fs_model.setIconProvider(icon_provider)

        name_filter = ["*.txt"]
        fs_model.setNameFilters(name_filter)
        fs_model.setNameFilterDisables(False)

        self._game_title_label.setText(Path(game_root_path).name)

        self._directory_view.setModel(fs_model)
        self._directory_view.setRootIndex(fs_model.setRootPath(game_root_path))
        self._directory_view.setIndentation(20)
        self._directory_view.setSortingEnabled(True)
        self._directory_view.sortByColumn(0, Qt.AscendingOrder)
        self._directory_view.header().hide()
        self._directory_view.hideColumn(1)
        self._directory_view.hideColumn(2)
        self._directory_view.hideColumn(3)

        self._pywright_game.set_game_path(game_root_path)

        self._game_properties_button.setEnabled(True)

    def clear_directory_view(self):
        self._directory_view.setModel(None)
        self._game_title_label.setText("")
        self._game_properties_button.setEnabled(False)

    def _handle_tree_view_double_clicked(self, index: QModelIndex):
        item_path = QFileSystemModel.filePath(self._directory_view.model(), index)
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
        new_script_action.setStatusTip("Add a new script to the selected case folder")

        open_dir_action = QAction("Open Folder in File Manager", self)
        open_dir_action.triggered.connect(self._handle_open_dir_action)
        open_dir_action.setStatusTip("Open selected folder in the default File Manager")

        rename_file_action = QAction("Rename", self)
        rename_file_action.setStatusTip("Rename selected item")

        remove_file_action = QAction("Remove", self)
        remove_file_action.triggered.connect(self._handle_remove_file_action)
        remove_file_action.setStatusTip("Remove selected item")

        if len(indexes) > 0:
            index = self._directory_view.selectedIndexes()[0]
            model: QFileSystemModel = index.model()

            # Any folder that isn't these are gonna be treated as case folders (for now?)
            non_case_folders = ("art", "music", "movies", "sfx")

            if model.isDir(index) and model.fileName(index) not in non_case_folders:
                menu.addAction(new_script_action)
            elif model.fileName(index).endswith((".txt", ".mcro")):
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

    def _handle_open_dir_action(self):
        if len(self._directory_view.selectedIndexes()) == 0:
            # Open the Game's root dir instead.
            QDesktopServices.openUrl(QUrl.fromLocalFile(self._pywright_game.game_path))
            return

        index = self._directory_view.selectedIndexes()[0]
        model: QFileSystemModel = index.model()
        dir_path = model.filePath(index)
        QDesktopServices.openUrl(QUrl.fromLocalFile(dir_path))

    def _handle_remove_file_action(self):
        if len(self._directory_view.selectedIndexes()) == 0:
            return

        index = self._directory_view.selectedIndexes()[0]
        model: QFileSystemModel = index.model()

        if model.isDir(index):
            return

        important_files = ("data.txt", "intro.txt", "evidence.txt")

        file_name = model.fileName(index)

        if file_name in important_files:
            QMessageBox.critical(self, "Error", "Important file \"{}\" cannot be removed!".format(file_name),
                                 QMessageBox.Ok)
            return

        prompt = QMessageBox.question(self, "Question", "Are you sure you want to remove \"{}\"?".format(file_name),
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if prompt == QMessageBox.Yes:
            model.remove(index)


class DeselectableTreeView(QTreeView):
    """Custom Tree View that has the ability to unselect items when clicked on an empty area"""
    def mousePressEvent(self, event: QMouseEvent):
        self.clearSelection()
        QTreeView.mousePressEvent(self, event)
