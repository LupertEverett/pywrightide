import shutil
from pathlib import Path

from PyQt6.QtWidgets import QDialog, QLineEdit, QLabel, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QLayout, \
    QMessageBox

from data.PyWrightGame import CurrentPyWrightGame
from data.SpriteSheet import convert_to_spritesheet


def _is_folder_empty(path: Path):
    result = True

    for x in path.iterdir():
        result = False
        break

    return result


class ImportFolderAsCharacterDialog(QDialog):

    def __init__(self, folder_path: Path, parent = None):
        super().__init__(parent)

        self._input_folder_path = folder_path
        self.setWindowTitle("Import Folder as Character")
        info_label = QLabel("The following files will be imported from the selected folder:")

        self._character_line_edit = QLineEdit()
        self._character_line_edit.textEdited.connect(self._handle_line_edit_edited)

        self._images_list_widget = QListWidget()

        self._populate_images_list()

        self._import_button = QPushButton("Import All")
        self._cancel_button = QPushButton("Cancel")

        self._import_button.setEnabled(False)
        self._import_button.pressed.connect(self._handle_import_pressed)
        self._cancel_button.pressed.connect(self.reject)

        main_layout = QVBoxLayout()

        character_name_layout = QHBoxLayout()
        character_name_layout.addWidget(QLabel("Character Name:"))
        character_name_layout.addStretch()
        character_name_layout.addWidget(self._character_line_edit)

        buttons_layout = QHBoxLayout()

        buttons_layout.addStretch()
        buttons_layout.addWidget(self._import_button)
        buttons_layout.addWidget(self._cancel_button)

        main_layout.addLayout(character_name_layout)
        main_layout.addWidget(info_label)
        main_layout.addWidget(self._images_list_widget)
        main_layout.addLayout(buttons_layout)

        main_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(main_layout)

    def _handle_line_edit_edited(self):
        cond = len(self._character_line_edit.text()) > 0 and not ' ' in self._character_line_edit.text() and self._images_list_widget.count() > 0
        self._import_button.setEnabled(cond)

    def _populate_images_list(self):
        self._images_list_widget.clear()
        self._images_list_widget.addItems([x.name for x in self._input_folder_path.iterdir() if not x.is_dir() and x.suffix in (".gif", ".webp")])

    def get_character_name(self):
        return self._character_line_edit.text()

    def _handle_import_pressed(self):
        output_folder = CurrentPyWrightGame().current_game.game_path / "art" / "port" / self._character_line_edit.text()

        if not output_folder.exists() or not output_folder.is_dir():
            output_folder.mkdir()

        if not _is_folder_empty(output_folder):
            msgbox = QMessageBox(self)
            msgbox.setWindowTitle("Character Already Exists")
            msgbox.setIcon(QMessageBox.Icon.Question)
            msgbox.setText("Character <b>{}</b> already exists.<br>What would you like to do?".format(self._character_line_edit.text()))

            replace_all_button = QPushButton("Replace All Emotions")
            import_new_button = QPushButton("Import New Emotions")
            cancel_button = QPushButton("Cancel")

            msgbox.addButton(replace_all_button, QMessageBox.ButtonRole.NoRole)
            msgbox.addButton(import_new_button, QMessageBox.ButtonRole.NoRole)
            msgbox.addButton(cancel_button, QMessageBox.ButtonRole.NoRole)

            if not msgbox.exec() or msgbox.clickedButton() == cancel_button:
                return

            if msgbox.clickedButton() == replace_all_button:
                shutil.rmtree(output_folder)
                output_folder.mkdir()

        # Copy the files over
        input_files = [x for x in self._input_folder_path.iterdir() if not x.is_dir() and x.suffix in (".gif", ".webp")]

        for file in input_files:
            output_file = output_folder / file.with_suffix(".png").name
            convert_to_spritesheet(file, output_file)

        self.accept()
