from PyQt6.QtWidgets import QDialog, QLineEdit, QLabel, QHBoxLayout, QVBoxLayout, QLayout, QGridLayout, QPushButton, \
    QMessageBox
from PIL import Image

from data.PyWrightGame import CurrentPyWrightGame
from data.SpriteSheet import convert_to_spritesheet
from .SpriteViewWidget import SpriteViewWidget

from pathlib import Path

class ImportImageAsCharacterDialog(QDialog):

    def __init__(self, image_path : Path, parent = None):
        super().__init__(parent)

        self._image_path = image_path

        self.setWindowTitle("Import Single Image: {}".format(str(self._image_path.stem)))

        self._image_name_text_edit = QLineEdit()
        self._image_name_text_edit.setEnabled(False)
        self._image_name_text_edit.setText(self._image_path.stem)

        self._character_name_text_edit = QLineEdit()
        self._character_name_text_edit.textEdited.connect(self._handle_text_fields_edited)

        self._emotion_name_text_edit = QLineEdit()
        self._emotion_name_text_edit.textEdited.connect(self._handle_text_fields_edited)

        self._sprite_view_widget = SpriteViewWidget()
        self._sprite_view_widget.resize(768, 576)

        pixmap = self._get_first_frame_of_image(image_path)
        self._sprite_view_widget.setPixmap(pixmap)

        self._import_button = QPushButton("Import")
        self._cancel_button = QPushButton("Cancel")

        self._import_button.setEnabled(False)
        self._import_button.pressed.connect(self._handle_import_pressed)
        self._cancel_button.pressed.connect(self.reject)

        main_layout = QVBoxLayout()

        properties_layout = QGridLayout()
        properties_layout.addWidget(QLabel("Image Name:"), 0, 0)
        properties_layout.addWidget(self._image_name_text_edit, 0, 1)

        properties_layout.addWidget(QLabel("Character Name:"), 1, 0)
        properties_layout.addWidget(self._character_name_text_edit, 1, 1)

        properties_layout.addWidget(QLabel("Emotion Name:"), 2, 0)
        properties_layout.addWidget(self._emotion_name_text_edit, 2, 1)

        bottom_buttons_layout = QHBoxLayout()
        bottom_buttons_layout.addStretch()
        bottom_buttons_layout.addWidget(self._import_button)
        bottom_buttons_layout.addWidget(self._cancel_button)

        main_layout.addLayout(properties_layout)
        main_layout.addWidget(self._sprite_view_widget)
        main_layout.addLayout(bottom_buttons_layout)

        main_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(main_layout)

    def get_character_name(self):
        return self._character_name_text_edit.text()

    def get_emotion_name(self):
        return self._emotion_name_text_edit.text()

    def _get_first_frame_of_image(self, image_path: Path):
        if image_path.suffix not in [".gif", ".webp"]:
            raise ValueError("Input file must be a .gif file or a .webp file")

        with Image.open(image_path) as im:
            return im.toqpixmap()

    def _handle_text_fields_edited(self):
        cond = (len(self._character_name_text_edit.text()) > 0 and not ' ' in self._character_name_text_edit.text()
                and len(self._emotion_name_text_edit.text()) > 0 and not ' ' in self._emotion_name_text_edit.text())
        self._import_button.setEnabled(cond)

    def _handle_import_pressed(self):
        base_path = CurrentPyWrightGame().current_game.game_path / "art" / "port"

        char_name = self._character_name_text_edit.text()
        emotion_name = self._emotion_name_text_edit.text()

        char_path = base_path / char_name
        emotion_path = char_path / "{}.png".format(emotion_name)

        if not char_path.exists() or not char_path.is_dir():
            char_path.mkdir()

        if emotion_path.exists() and not emotion_path.is_dir():
            # There already exists a file with that name
            prompt = QMessageBox.question(self, "Emotion File Already Exists",
                                          "Emotion <b>{}</b> already exists.<br>Are you sure you want to override it?".format(emotion_name),
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                          QMessageBox.StandardButton.No
                                          )

            if prompt == QMessageBox.StandardButton.No:
                return

        convert_to_spritesheet(self._image_path, emotion_path)
        self.accept()
