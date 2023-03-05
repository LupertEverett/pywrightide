# Music browser for Asset Browser
# Note that Qt on Windows doesn't support playing .ogg files for one reason or another,
# so music playback is not possible for the time being

from pathlib import Path
from enum import Enum

from PyQt5.QtWidgets import (QWidget, QListWidget, QAction, QVBoxLayout, QHBoxLayout, QComboBox,
                             QMenu, QPushButton)
from PyQt5.QtGui import QDesktopServices, QGuiApplication, QClipboard
from PyQt5.QtCore import pyqtSignal, Qt, QUrl

from data.PyWrightGame import PyWrightGame

MUSIC_FOLDER_NAME = "music"
SFX_FOLDER_NAME = "sfx"


class AudioType(Enum):
    Music = 1
    Sfx = 2


class AssetBrowserAudioWidget(QWidget):

    # Sends the URL of the music to play
    audio_play_requested = pyqtSignal(str, AudioType)

    audio_stop_requested = pyqtSignal()

    # Sends the appropriate command
    command_insert_at_cursor_requested = pyqtSignal(str)

    def __init__(self, audio_type: AudioType, parent=None):
        super().__init__(parent)
        self._pywright_dir = ""
        self._selected_game = PyWrightGame()

        self.__audio_type = audio_type
        self.__AUDIO_FOLDER = MUSIC_FOLDER_NAME if audio_type == AudioType.Music else SFX_FOLDER_NAME

        self._audio_list_widget = QListWidget(self)
        self._audio_list_widget.setDragEnabled(False)
        self._audio_list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self._audio_list_widget.customContextMenuRequested.connect(self._handle_audio_context_menu)
        self._audio_list_widget.itemSelectionChanged.connect(self._handle_current_change)
        self._audio_list_widget.doubleClicked.connect(self._handle_play_pressed)

        self._audio_folders_combo_box = QComboBox()
        self._audio_folders_combo_box.currentIndexChanged.connect(self._refresh_music_list_view)

        self._play_button = QPushButton("Play")
        self._play_button.pressed.connect(self._handle_play_pressed)
        self._play_button.setEnabled(len(self._audio_list_widget.selectedItems()) > 0)
        self._stop_button = QPushButton("Stop")
        self._stop_button.pressed.connect(self._handle_stop_pressed)

        media_controls_layout = QHBoxLayout()

        media_controls_layout.addWidget(self._play_button)
        media_controls_layout.addWidget(self._stop_button)

        main_layout = QVBoxLayout()

        main_layout.addLayout(media_controls_layout)
        main_layout.addWidget(self._audio_folders_combo_box)
        main_layout.addWidget(self._audio_list_widget)

        self._available_music_folders = []

        self.setLayout(main_layout)

    def select_pywright(self, pywright_dir: str):
        self._pywright_dir = pywright_dir

    def set_selected_game(self, selected_game: PyWrightGame):
        self._selected_game = selected_game

    def _query_available_folders(self):
        if self._pywright_dir == "":
            return

        if not self._selected_game.is_a_game_selected():
            return

        global_music_folder_path = Path("{}/{}/".format(self._pywright_dir, self.__AUDIO_FOLDER))

        game_music_folder_path = Path("{}/{}/".format(self._selected_game.game_path, self.__AUDIO_FOLDER))

        self._available_music_folders.clear()

        if global_music_folder_path.exists() and global_music_folder_path.is_dir():
            self._available_music_folders.append("Global")

        if game_music_folder_path.exists() and game_music_folder_path.is_dir():
            self._available_music_folders.append("Game specific")

    def refresh_music_folders(self):
        self._audio_folders_combo_box.clear()
        self._query_available_folders()
        self._audio_folders_combo_box.addItems(self._available_music_folders)
        self._refresh_music_list_view()

    def _refresh_music_list_view(self):
        folder_text = self._audio_folders_combo_box.currentText()
        is_global = folder_text == "Global"

        folder_path = Path("{}/{}/".format(self._pywright_dir if is_global else self._selected_game.game_path,
                                           self.__AUDIO_FOLDER))

        items = [str(x.stem) for x in folder_path.iterdir() if x.suffix == ".ogg"]

        self._audio_list_widget.clear()
        self._audio_list_widget.addItems(items)

    def _handle_audio_context_menu(self, position):
        if not self._selected_game.is_a_game_selected():
            return

        menu = QMenu()

        copy_music_name_action = QAction("Copy {} name".format(self.__AUDIO_FOLDER), self)
        copy_music_name_action.triggered.connect(self._handle_audio_name_copy)
        copy_music_name_action.setStatusTip("Copy selected {}'s name to the clipboard".format(self.__AUDIO_FOLDER))

        insert_into_current_script_action = QAction("Insert into current script from cursor position", self)
        insert_into_current_script_action.triggered.connect(self._handle_insert_into_cursor)
        insert_into_current_script_action.setStatusTip("Insert the selected {} as a "
                                                       "command into the currently open "
                                                       "script from the cursor position".format(self.__AUDIO_FOLDER))

        open_folder_action = QAction("Open current folder in File Manager", self)
        open_folder_action.triggered.connect(self._handle_open_current_folder)
        open_folder_action.setStatusTip("Open the current {} folder in the default File Manager".format(
            self.__AUDIO_FOLDER))

        if len(self._audio_list_widget.selectedIndexes()) > 0:
            menu.addAction(copy_music_name_action)
            menu.addAction(insert_into_current_script_action)
            menu.addSeparator()

        menu.addAction(open_folder_action)

        menu.exec(self.mapToGlobal(position))

    def _handle_open_current_folder(self):
        folder_text = self._audio_folders_combo_box.currentText()
        is_global = folder_text == "Global"

        folder_path = Path("{}/{}/".format(self._pywright_dir if is_global else self._selected_game.game_path,
                                           self.__AUDIO_FOLDER))

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder_path)))

    def _handle_audio_name_copy(self):
        clipboard = QGuiApplication.clipboard()
        item = self._audio_list_widget.selectedItems()[0].text()

        clipboard.setText(item + ".ogg", QClipboard.Clipboard)

    def _handle_insert_into_cursor(self):
        audio_name = self._audio_list_widget.selectedItems()[0].text()

        # Construct the final command and emit it
        final_command = "mus {}".format(audio_name) if self.__AUDIO_FOLDER == MUSIC_FOLDER_NAME \
            else "sfx {}".format(audio_name)

        self.command_insert_at_cursor_requested.emit(final_command)

    def _handle_current_change(self):
        self._play_button.setEnabled(len(self._audio_list_widget.selectedItems()) > 0)

    def _handle_play_pressed(self):
        if self._pywright_dir == "":
            return
        if not self._selected_game.is_a_game_selected():
            return

        folder_text = self._audio_folders_combo_box.currentText()
        is_global = folder_text == "Global"

        selected_music = self._audio_list_widget.selectedItems()[0].text()

        file_path = Path("{}/{}/{}.ogg".format(self._pywright_dir if is_global else self._selected_game.game_path,
                                               self.__AUDIO_FOLDER,
                                               selected_music))

        # Construct a path for the Music
        self.audio_play_requested.emit(str(file_path), self.__audio_type)

    def _handle_stop_pressed(self):
        self.audio_stop_requested.emit()
