# Holds the information regarding a PyWright game
# Basically "visualizes" data.txt and intro.txt

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QPushButton

from .GameDataWidget import GameDataWidget
from .GameIntroWidget import GameIntroWidget

from data.PyWrightGame import PyWrightGame


class GamePropertiesWidget(QWidget):

    def __init__(self, pywright_root_dir: str):
        super().__init__()

        self._selected_game = PyWrightGame()

        self.main_layout = QVBoxLayout()

        self.game_data_widget = GameDataWidget(pywright_root_dir)
        self.game_data_widget.data_txt_fields_changed.connect(self._handle_data_txt_fields_change)
        self._game_intro_widget = GameIntroWidget()

        self._save_data_button = QPushButton("Save")
        self._save_data_button.clicked.connect(self.game_data_widget.save_data_txt)
        self._revert_data_button = QPushButton("Revert")
        self._revert_data_button.clicked.connect(self.game_data_widget.populate_game_info)

        data_txt_group = self._create_data_txt_group_box()
        intro_txt_group = self._create_intro_txt_group_box()

        self.main_layout.addWidget(data_txt_group)
        self.main_layout.addWidget(intro_txt_group)
        self.main_layout.addStretch()

        self._handle_data_txt_fields_change()

        self.setLayout(self.main_layout)

    def _create_data_txt_group_box(self) -> QGroupBox:
        result = QGroupBox("data.txt - Game Info")

        data_txt_group_layout = QVBoxLayout()
        data_txt_group_layout.addWidget(self.game_data_widget)

        buttons_layout = QHBoxLayout()

        buttons_layout.addStretch()
        buttons_layout.addWidget(self._save_data_button)
        buttons_layout.addWidget(self._revert_data_button)

        data_txt_group_layout.addLayout(buttons_layout)

        result.setLayout(data_txt_group_layout)
        return result

    def _create_intro_txt_group_box(self) -> QGroupBox:
        result = QGroupBox("intro.txt - Available Cases")

        intro_txt_group_layout = QVBoxLayout()
        intro_txt_group_layout.addWidget(self._game_intro_widget)

        result.setLayout(intro_txt_group_layout)
        return result

    def load_game(self, selected_game: PyWrightGame):
        self._selected_game = selected_game
        self.game_data_widget.load_data_txt(self._selected_game)
        self._game_intro_widget.load_intro_txt(self._selected_game)

    def save_game(self):
        self.game_data_widget.save_data_txt()
        self._game_intro_widget.save_intro_txt()

    def _handle_data_txt_fields_change(self):
        valid_to_change = self._selected_game.is_a_game_selected() and \
                          self.game_data_widget.are_data_txt_areas_different()
        self._save_data_button.setEnabled(valid_to_change)
        self._revert_data_button.setEnabled(valid_to_change)

    def set_game_icon_path(self, new_path: str):
        self.game_data_widget.set_game_icon_path_textfield(new_path)

