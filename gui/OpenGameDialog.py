# A Dialog that allows the user to pick the PyWright Game they wish to edit.

from pathlib import Path

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QListView

from data import IconThemes


class OpenGameDialog(QDialog):
    """Provides a dialog for opening an existing PyWright game"""

    def __init__(self, pywright_root_dir: str, parent=None):
        super().__init__(parent)

        self.selected_game: str = ""

        self.setWindowTitle("Pick a Game")

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self._handle_accept)
        self.buttonBox.rejected.connect(self.reject)

        self._list_view = QListView()
        self._item_model = QStandardItemModel()
        self._list_view.setModel(self._item_model)
        self._list_view.setIconSize(QSize(32, 32))
        self._list_view.doubleClicked.connect(self._handle_list_view_double_click)

        self.layout = QVBoxLayout()

        self.layout.addWidget(self._list_view)
        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)

        self._populate_list(pywright_root_dir)

    def _populate_list(self, pywright_root_dir: str):
        p = Path("{}/games".format(pywright_root_dir))

        games = [x for x in p.iterdir() if x.is_dir()]

        game_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_OPEN_GAME)

        for game in games:
            self._add_item_to_model(game_icon_path, game.stem)

    def _add_item_to_model(self, icon_path: str, item_text: str):
        item = QStandardItem(QIcon(icon_path), item_text)
        item.setEditable(False)
        self._item_model.appendRow(item)

    def _handle_list_view_double_click(self):
        if len(self._list_view.selectedIndexes()) > 0:
            self._handle_accept()

    def _handle_accept(self):
        idx = self._list_view.currentIndex().row()
        self.selected_game = self._item_model.item(idx).text()
        self.accept()
