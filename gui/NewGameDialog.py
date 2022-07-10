# Opens up a dialog for creating a basic PyWright Game.

from pathlib import Path

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox

from .GameDataWidget import GameDataWidget
from data.PyWrightGame import PyWrightGame


class NewGameDialog(QDialog):
    """A dialog for creating a new PyWright game"""

    def __init__(self, pywright_root_path: str, parent=None):
        super().__init__(parent)

        self.setWindowTitle("New PyWright Game")
        self.setFixedSize(500, 250)

        self._pywright_root_path = pywright_root_path

        self._folder_name_edit = QLineEdit()
        self._folder_name_edit.setFixedWidth(300)

        folder_name_box = QHBoxLayout()
        folder_name_box.addWidget(QLabel("Game (Folder) Name:"))
        folder_name_box.addStretch()
        folder_name_box.addWidget(self._folder_name_edit)

        self._game_data_widget = GameDataWidget(self._pywright_root_path)

        self._new_game = PyWrightGame()

        self._dialog_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self._dialog_box.accepted.connect(self._handle_accepted)
        self._dialog_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()

        main_layout.addLayout(folder_name_box)
        main_layout.addWidget(self._game_data_widget)
        main_layout.addWidget(self._dialog_box)

        self.setLayout(main_layout)

    def _handle_accepted(self):
        folder = self._folder_name_edit.text()
        creation_path = Path("{}/games/{}".format(self._pywright_root_path, folder)) if folder != "" else ""

        title = self._game_data_widget.get_game_title()
        icon_path = self._game_data_widget.get_game_icon_path()
        author = self._game_data_widget.get_game_author()
        version = self._game_data_widget.get_game_version()
        try:
            self._new_game.create_new_game(str(creation_path), version, title, icon_path, author)
            self.accept()
        except ValueError as err:
            QMessageBox.critical(self, "Error", str(err))
        except FileExistsError:
            QMessageBox.critical(self, "Error", "A folder named {} already exists!".format(folder))

    def get_new_game_name(self):
        return self._folder_name_edit.text()
