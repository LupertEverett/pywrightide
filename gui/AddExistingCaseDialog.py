# Add Existing Case Dialog
# Checks through the folders that could be possible Case folders and prompts the user to pick one to add
from pathlib import Path

from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QListWidget, QVBoxLayout, QPushButton

from data.PyWrightGame import PyWrightGameInfo

# These folders will NEVER appear in the dialog, as they're definitely NOT case folders
disallowed_folders = ("art", "sfx", "music", "movies")


class AddExistingCaseDialog(QDialog):

    def __init__(self, selected_game_info: PyWrightGameInfo, parent):
        super().__init__(parent)

        self._selected_game_info = selected_game_info

        self.setWindowTitle("Add Existing Case")

        self._available_cases_list_widget = QListWidget()
        self._available_cases_list_widget.itemSelectionChanged.connect(self._update_ok_button)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self._handle_accept)
        self.buttonBox.rejected.connect(self.reject)

        self._ok_button: QPushButton = self.buttonBox.button(QDialogButtonBox.StandardButton.Ok)
        self._update_ok_button()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._available_cases_list_widget)
        main_layout.addWidget(self.buttonBox)

        self.setLayout(main_layout)

        self._populate_cases_list()

    def _populate_cases_list(self):
        # Get a list of folders
        p = self._selected_game_info.game_path

        folders = [x.stem for x in p.iterdir() if x.is_dir()
                   and x.stem not in disallowed_folders
                   and x.stem not in self._selected_game_info.game_cases
                   and self._is_valid_case(p/x)]

        self._available_cases_list_widget.addItems(folders)

    def _update_ok_button(self):
        self._ok_button.setEnabled(self._available_cases_list_widget.count() > 0)

    def _is_valid_case(self, case_path: Path):
        # Every valid case folder must include an intro.txt,
        # rather easily foolable but should be fine in almost all cases
        file = case_path/"intro.txt"
        return file.exists() and file.is_file()

    def _handle_accept(self):
        self._selected_game_info.game_cases.append(self._available_cases_list_widget.selectedItems()[0].text())
        self.accept()
