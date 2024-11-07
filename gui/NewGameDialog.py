# Opens up a dialog for creating a basic PyWright Game.

from pathlib import Path

from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox, \
    QPushButton, QFileDialog

from .GameDataWidget import GameDataWidget
from data.PyWrightGame import PyWrightGameInfo
from data import PyWrightFolder


class NewGameDialog(QDialog):
    """A dialog for creating a new PyWright game"""

    def __init__(self, pywright_root_path: str = "", parent=None):
        super().__init__(parent)

        self.setWindowTitle("New PyWright Game")
        self.setFixedSize(500, 250)

        self._pywright_path_edit = QLineEdit()
        self._pywright_path_edit.setText(pywright_root_path)
        self._pywright_path_edit.setFixedWidth(255)
        self._folder_name_edit = QLineEdit()
        self._folder_name_edit.setFixedWidth(300)

        self._pywright_path_browse_button = QPushButton("...")
        self._pywright_path_browse_button.setFixedWidth(40)

        self._pywright_path_browse_button.clicked.connect(self._handle_browse_button_clicked)

        pywright_folder_path_box = QHBoxLayout()
        pywright_folder_path_box.addWidget(QLabel("PyWright Folder Path:"))
        pywright_folder_path_box.addWidget(self._pywright_path_edit)
        pywright_folder_path_box.addWidget(self._pywright_path_browse_button)

        folder_name_box = QHBoxLayout()
        folder_name_box.addWidget(QLabel("Game (Folder) Name:"))
        folder_name_box.addStretch()
        folder_name_box.addWidget(self._folder_name_edit)

        self._game_data_widget = GameDataWidget(pywright_root_path)

        self._new_game: PyWrightGameInfo | None = None

        self._dialog_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self._dialog_box.accepted.connect(self._handle_accepted)
        self._dialog_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()

        main_layout.addLayout(pywright_folder_path_box)
        main_layout.addLayout(folder_name_box)
        main_layout.addWidget(self._game_data_widget)
        main_layout.addWidget(self._dialog_box)

        self.setLayout(main_layout)

    def _handle_browse_button_clicked(self):
        picker = Path(QFileDialog.getExistingDirectory())

        if PyWrightFolder.is_valid_pywright_folder(str(picker)):
            self._pywright_path_edit.setText(str(picker))
            self._game_data_widget.change_pywright_path(str(picker))
        else:
            QMessageBox.critical(self, "Error", "Selected folder is not a PyWright folder.",
                                 QMessageBox.StandardButton.Ok)

    def _handle_accepted(self):
        folder = self._folder_name_edit.text()
        root_path = Path(self._pywright_path_edit.text())

        title = self._game_data_widget.get_game_title()
        icon_path = self._game_data_widget.get_game_icon_path()
        author = self._game_data_widget.get_game_author()
        version = self._game_data_widget.get_game_version()
        try:
            self._new_game = PyWrightGameInfo.create_new_game(root_path, folder, version, title, icon_path, author)
            self.accept()
        except ValueError as err:
            QMessageBox.critical(self, "Error", str(err))
        except FileExistsError:
            QMessageBox.critical(self, "Error", "A folder named {} already exists!".format(folder))

    def get_new_game(self):
        return self._new_game
