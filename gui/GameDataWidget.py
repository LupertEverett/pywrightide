# Handles the data in data.txt of the selected PyWright game

from pathlib import Path

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import pyqtSignal

from .IconPickerDialog import IconPickerDialog
from data.PyWrightGame import PyWrightGameInfo


class GameDataWidget(QWidget):

    data_txt_fields_changed = pyqtSignal()

    def __init__(self, pywright_root_dir: str):
        super().__init__()

        self._game_info: PyWrightGameInfo | None = None

        self._pywright_root_dir = pywright_root_dir

        # LineEdits
        self._game_title_lineedit = QLineEdit(self)
        self._game_title_lineedit.setFixedWidth(300)
        self._game_title_lineedit.textChanged.connect(self._handle_data_txt_fields_change)

        self._game_version_lineedit = QLineEdit(self)
        self._game_version_lineedit.setFixedWidth(300)
        self._game_version_lineedit.textChanged.connect(self._handle_data_txt_fields_change)

        self._game_author_lineedit = QLineEdit(self)
        self._game_author_lineedit.setFixedWidth(300)
        self._game_author_lineedit.textChanged.connect(self._handle_data_txt_fields_change)

        self._game_icon_lineedit = QLineEdit(self)
        self._game_icon_lineedit.setDisabled(True)
        self._game_icon_lineedit.setFixedWidth(250)
        self._game_icon_lineedit.textChanged.connect(self._handle_data_txt_fields_change)

        # Buttons
        self._game_icon_picker_button = QPushButton("...")
        self._game_icon_picker_button.setMaximumWidth(40)
        self._game_icon_picker_button.clicked.connect(self._handle_icon_picker_clicked)

        self._handle_data_txt_fields_change()

        # Main Layout
        main_layout = self._prepare_main_layout()
        self.setLayout(main_layout)

    def _prepare_main_layout(self) -> QVBoxLayout:
        result = QVBoxLayout()

        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Game Title:"))
        title_layout.addStretch()
        title_layout.addWidget(self._game_title_lineedit)

        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel("Version:"))
        version_layout.addStretch()
        version_layout.addWidget(self._game_version_lineedit)

        author_layout = QHBoxLayout()
        author_layout.addWidget(QLabel("Author:"))
        author_layout.addStretch()
        author_layout.addWidget(self._game_author_lineedit)

        icon_layout = QHBoxLayout()
        icon_layout.addWidget(QLabel("Game Icon:"))
        icon_layout.addStretch()
        icon_layout.addWidget(self._game_icon_lineedit)
        icon_layout.addWidget(self._game_icon_picker_button)

        result.addLayout(title_layout)
        result.addLayout(version_layout)
        result.addLayout(author_layout)
        result.addLayout(icon_layout)
        result.setContentsMargins(0, 0, 0, 0)

        return result

    def change_pywright_path(self, new_path: str):
        self._pywright_root_dir = new_path

    def load_data_txt(self, selected_game_info: PyWrightGameInfo):
        self._game_info = selected_game_info
        self.populate_game_info()

    def save_data_txt(self):
        if self._game_info is not None:
            self._game_info.game_version = self._game_version_lineedit.text()
            self._game_info.game_title = self._game_title_lineedit.text()
            self._game_info.game_icon_path = self._game_icon_lineedit.text()
            self._game_info.game_author = self._game_author_lineedit.text()
            self._game_info.write_data_txt()
            self._handle_data_txt_fields_change()

    def populate_game_info(self):
        if self._game_info is not None:
            self._game_title_lineedit.setText(self._game_info.game_title)
            self._game_version_lineedit.setText(self._game_info.game_version)
            self._game_icon_lineedit.setText(str(self._game_info.game_icon_path))
            self._game_author_lineedit.setText(self._game_info.game_author)

    def set_game_icon_path_textfield(self, new_path: str):
        self._game_icon_lineedit.setText(new_path)
        self._handle_data_txt_fields_change()

    def _handle_data_txt_fields_change(self):
        self.data_txt_fields_changed.emit()

    def are_data_txt_areas_different(self) -> bool:
        return not self.are_data_txt_areas_empty() and (
                self._game_title_lineedit.text() != self._game_info.game_title
                or self._game_icon_lineedit.text() != str(self._game_info.game_icon_path)
                or self._game_version_lineedit.text() != self._game_info.game_version
                or self._game_author_lineedit.text() != self._game_info.game_author)

    def are_data_txt_areas_empty(self) -> bool:
        return self._game_title_lineedit.text() == "" \
               or self._game_icon_lineedit.text() == "" \
               or self._game_author_lineedit.text() == "" \
               or self._game_version_lineedit.text() == ""

    def get_game_title(self) -> str:
        return self._game_title_lineedit.text()

    def get_game_icon_path(self) -> str:
        return self._game_icon_lineedit.text()

    def get_game_author(self) -> str:
        return self._game_author_lineedit.text()

    def get_game_version(self) -> str:
        return self._game_version_lineedit.text()

    def _handle_icon_picker_clicked(self):
        if self._pywright_root_dir != "":
            icon_picker = IconPickerDialog(self._pywright_root_dir, self._game_info, self)

            if icon_picker.exec():
                self._game_icon_lineedit.setText(icon_picker.selected_icon)
