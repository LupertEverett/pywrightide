# ScriptsViewWidget: Like DirectoryViewWidget, but focuses entirely on scripts themselves
import dataclasses, os
from pathlib import Path

from PyQt6.QtCore import pyqtSignal, QModelIndex
from PyQt6.QtWidgets import QDockWidget, QTreeView, QLabel, QVBoxLayout, QWidget, QStyle, QAbstractItemView
from PyQt6.QtGui import QStandardItem, QStandardItemModel


@dataclasses.dataclass
class FileInfo:
    file_name: str
    is_macro: bool
    has_examine: bool
    has_move: bool
    has_talk: bool
    has_present: bool


class ScriptsViewItem(QStandardItem):
    path_str = ""


class ScriptsViewModel(QStandardItemModel):

    open_new_tab = pyqtSignal(str)
    directory_switched = pyqtSignal(str)

    def __init__(self, initial_dir="", parent: QAbstractItemView = None):
        super().__init__(parent)

        self.setColumnCount(5)

        self._standard_dir_icon = parent.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        self._standard_file_icon = parent.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)

    def populate(self, directory: Path):
        self.clear()

        prohibited_dirs = ("art", "fonts", "sfx", "movies", "music")
        allowed_types = (".txt", ".mcro")

        # This should return the folders with the case names
        dirs = [x for x in os.scandir(directory) if x.is_dir() and x.name not in prohibited_dirs]

        # Add the dirs as the root items
        for iterdirectory in dirs:
            diritem = ScriptsViewItem()
            diritem.setIcon(self._standard_dir_icon)
            diritem.setText(iterdirectory.name)
            diritem.setEditable(False)
            diritem.path_str = iterdirectory.name

            # also iterate through folder
            files = [y for y in os.scandir("{}/{}".format(directory, iterdirectory.name)) if y.is_file() and y.name.endswith(allowed_types)]

            for iterfile in files:
                fileitem = ScriptsViewItem(iterfile.name)
                fileitem.setEditable(False)
                fileitem.setIcon(self._standard_file_icon)
                fileitem.path_str = str(Path(diritem.path_str) / iterfile.name)
                diritem.appendRow(fileitem)

            self.appendRow(diritem)


class ScriptsViewWidget(QWidget):

    open_new_tab = pyqtSignal(str)
    open_game_properties_tab = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Scripts View")
        self.setObjectName("ScriptsViewWidget")

        self._tree_view = QTreeView()
        self._tree_view.doubleClicked.connect(self._handle_tree_view_double_clicked)

        self._standard_dir_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        self._standard_file_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)

        self._tree_view.setHeaderHidden(True)

        self._item_model = ScriptsViewModel(parent=self._tree_view)
        self._tree_view.setModel(self._item_model)

        self._directory = Path()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._tree_view)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(main_layout)

    def switch_to_directory(self, directory: Path):
        self._item_model.populate(directory)
        self._directory = directory

    def _handle_tree_view_double_clicked(self, index: QModelIndex):
        selected_index = self._tree_view.selectedIndexes()[0]
        selected_item : ScriptsViewItem = self._item_model.itemFromIndex(selected_index)
        item_path = str(self._directory / selected_item.path_str)

        if not Path(item_path).is_dir():
            self.open_new_tab.emit(item_path)
