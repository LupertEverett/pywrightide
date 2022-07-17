# A Dialog that allows the user to pick the PyWright Game they wish to edit.

from pathlib import Path

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QListWidget


class OpenGameDialog(QDialog):
    """Provides a dialog for opening an existing PyWright game"""

    def __init__(self, pywright_root_dir: str, parent=None):
        super().__init__(parent)

        self.selected_game: str = ""

        self.setWindowTitle("Pick a Game")

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._handle_accept)
        self.buttonBox.rejected.connect(self.reject)

        self.list_widget = QListWidget()
        self.list_widget.doubleClicked.connect(self._handle_list_widget_double_click)

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.list_widget)
        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)

        self._populate_list(pywright_root_dir)

    def _populate_list(self, pywright_root_dir: str):
        p = Path("{}/games".format(pywright_root_dir))

        games = [x for x in p.iterdir() if x.is_dir()]

        for game in games:
            self.list_widget.addItem(str(game.stem))

    def _handle_list_widget_double_click(self):
        if len(self.list_widget.selectedIndexes()) > 0:
            self._handle_accept()

    def _handle_accept(self):
        self.selected_game = self.list_widget.currentItem().text()
        self.accept()
