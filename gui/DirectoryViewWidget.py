# Provides a directory view, and some ways to interact with the said directory.

from pathlib import Path

from PyQt5.QtWidgets import (QTreeView, QFileSystemModel, QFileIconProvider,
                             QWidget, QDockWidget, QHBoxLayout,
                             QLabel, QPushButton)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QModelIndex, pyqtSignal


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

        self._directory_view = QTreeView()
        self._directory_view.doubleClicked.connect(self._handle_tree_view_double_clicked)

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
