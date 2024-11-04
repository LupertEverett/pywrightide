# Music/SFX browser component for Asset Browser

from pathlib import Path
from enum import Enum

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                             QMenu, QPushButton, QListView)
from PyQt6.QtGui import QDesktopServices, QGuiApplication, QClipboard, QAction, QIcon, QStandardItemModel, QStandardItem
from PyQt6.QtCore import pyqtSignal, Qt, QUrl, QFileSystemWatcher, QModelIndex

from data.PyWrightGame import PyWrightGame, PyWrightGameInfo
from data import IconThemes

MUSIC_FOLDER_NAME = "music"
SFX_FOLDER_NAME = "sfx"


class AudioType(Enum):
    Music = 1
    Sfx = 2


class AssetBrowserAudioWidget(QWidget):
    # Sends the URL of the music to play
    audio_play_requested = pyqtSignal(str)

    audio_stop_requested = pyqtSignal()

    # Sends the appropriate command
    command_insert_at_cursor_requested = pyqtSignal(str)

    def __init__(self, audio_type: AudioType, parent=None):
        super().__init__(parent)
        self._pywright_dir = ""
        # self._selected_game = PyWrightGame()
        self._game_info: PyWrightGameInfo | None = None

        self.__audio_type = audio_type
        self.__AUDIO_FOLDER = MUSIC_FOLDER_NAME if audio_type == AudioType.Music else SFX_FOLDER_NAME

        self._audio_list_view = QListView(self)
        self._audio_list_model = QStandardItemModel()

        self._audio_list_view.setDragEnabled(False)
        self._audio_list_view.setModel(self._audio_list_model)
        self._audio_list_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._audio_list_view.customContextMenuRequested.connect(self._handle_audio_context_menu)
        self._audio_list_view.clicked.connect(self._handle_current_change)
        self._audio_list_view.doubleClicked.connect(self._handle_play_pressed)

        self._audio_folders_combo_box = QComboBox()
        self._audio_folders_combo_box.currentIndexChanged.connect(self._handle_combobox_index_changed)

        self._refresh_button = QPushButton()
        self._refresh_button.setIcon(QIcon(IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_REFRESH)))
        self._refresh_button.setMaximumWidth(30)
        self._refresh_button.setToolTip("Refresh current folder")
        self._refresh_button.clicked.connect(self._refresh_audio_list_view)
        self._refresh_button.setEnabled(self._audio_folders_combo_box.currentIndex() != -1)

        self._play_button = QPushButton()
        self._play_button.setIcon(QIcon(IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_AUDIO_PLAY)))
        self._play_button.setToolTip("Play")
        self._play_button.pressed.connect(self._handle_play_pressed)
        self._play_button.setEnabled(len(self._audio_list_view.selectedIndexes()) > 0)
        self._stop_button = QPushButton()
        self._stop_button.setIcon(QIcon(IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_AUDIO_STOP)))
        self._stop_button.setToolTip("Stop")
        self._stop_button.pressed.connect(self._handle_stop_pressed)

        self.__file_system_watcher = QFileSystemWatcher(self)

        media_controls_layout = QHBoxLayout()

        media_controls_layout.addWidget(self._play_button)
        media_controls_layout.addWidget(self._stop_button)

        main_layout = QVBoxLayout()

        combobox_layout = QHBoxLayout()
        combobox_layout.addWidget(self._audio_folders_combo_box)
        combobox_layout.addWidget(self._refresh_button)

        main_layout.addLayout(combobox_layout)
        main_layout.addLayout(media_controls_layout)
        main_layout.addWidget(self._audio_list_view)

        self._available_audio_folders = []

        self._currently_playing_index: QModelIndex | None = None
        self._currently_playing_folder: str = ""

        self.setLayout(main_layout)

    def select_pywright(self, pywright_dir: str):
        self._pywright_dir = pywright_dir

    def set_selected_game(self, selected_game_info: PyWrightGameInfo):
        self._game_info = selected_game_info

    def _query_available_folders(self):
        self.__file_system_watcher.removePaths(self.__file_system_watcher.directories())
        if self._pywright_dir == "":
            return

        if self._game_info is None:
            return

        global_audio_folder_path = Path("{}/{}/".format(self._pywright_dir, self.__AUDIO_FOLDER))

        game_audio_folder_path = Path("{}/{}/".format(self._game_info.game_path, self.__AUDIO_FOLDER))

        self._available_audio_folders.clear()

        if global_audio_folder_path.exists() and global_audio_folder_path.is_dir():
            self.__file_system_watcher.addPath(str(global_audio_folder_path))
            self._available_audio_folders.append("Global")

        if game_audio_folder_path.exists() and game_audio_folder_path.is_dir():
            self.__file_system_watcher.addPath(str(game_audio_folder_path))
            self._available_audio_folders.append("Game specific")

        # Also add the relevant folders in Cases if they exist
        for current_case in self._game_info.game_cases:
            case_audio_folder_path = Path("{}/{}/{}/".format(
                self._game_info.game_path,
                current_case,
                self.__AUDIO_FOLDER
            ))

            if case_audio_folder_path.exists() and case_audio_folder_path.is_dir():
                self._available_audio_folders.append("{}/{}".format(current_case, self.__AUDIO_FOLDER))

    def refresh_audio_folders(self):
        self._audio_folders_combo_box.clear()
        self._query_available_folders()
        self._audio_folders_combo_box.addItems(self._available_audio_folders)
        self._refresh_audio_list_view()

    def _handle_combobox_index_changed(self):
        self._refresh_button.setEnabled(self._audio_folders_combo_box.currentIndex() != -1)
        self._refresh_audio_list_view()

    def _refresh_audio_list_view(self):
        folder_path = self._get_selected_audio_folder_path()

        if not folder_path.exists() or not folder_path.is_dir():
            return

        items = [x.stem for x in folder_path.iterdir() if x.suffix == ".ogg"]

        self._audio_list_model.clear()

        for item in items:
            self._add_item_to_model(item)

        folder_text = self._audio_folders_combo_box.currentText()

        if self._currently_playing_index is not None and self._currently_playing_folder == folder_text:
            self.set_currently_playing_icon()

    def _add_item_to_model(self, item_name: str):
        item = QStandardItem(QIcon(self._get_audio_icon_name()), item_name)
        item.setEditable(False)
        self._audio_list_model.appendRow(item)

    def _handle_audio_context_menu(self, position):
        if self._game_info is None:
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

        insert_into_current_script_loop_action = QAction("Insert into cursor position as looping music", self)
        insert_into_current_script_loop_action.triggered.connect(self._handle_insert_music_loop_into_cursor)
        insert_into_current_script_loop_action.setStatusTip("Insert the selected music as a looping music command "
                                                            "into the currently open script from the cursor position")

        open_folder_action = QAction("Open current folder in File Manager", self)
        open_folder_action.triggered.connect(self._handle_open_current_folder)
        open_folder_action.setStatusTip("Open the current {} folder in the default File Manager".format(
            self.__AUDIO_FOLDER))

        if len(self._audio_list_view.selectedIndexes()) > 0:
            menu.addAction(copy_music_name_action)
            menu.addAction(insert_into_current_script_action)
            if self.__audio_type == AudioType.Music:
                menu.addAction(insert_into_current_script_loop_action)
            menu.addSeparator()

        menu.addAction(open_folder_action)

        menu.exec(self.mapToGlobal(position))

    def _get_selected_audio_folder_path(self):
        folder_text = self._audio_folders_combo_box.currentText()

        is_case_specific_folder = folder_text != "Global" and folder_text != "Game specific"

        if is_case_specific_folder:
            case_text = folder_text.split('/', maxsplit=1)[0]
            if case_text == "":
                return Path()

            return Path("{}/{}/{}/".format(self._game_info.game_path, case_text, self.__AUDIO_FOLDER))
        else:
            is_global = folder_text == "Global"

            return Path("{}/{}/".format(self._pywright_dir if is_global else self._game_info.game_path,
                                        self.__AUDIO_FOLDER))

    def _handle_open_current_folder(self):
        folder_text = self._audio_folders_combo_box.currentText()
        is_global = folder_text == "Global"

        folder_path = Path("{}/{}/".format(self._pywright_dir if is_global else self._game_info.game_path,
                                           self.__AUDIO_FOLDER))

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder_path)))

    def _handle_audio_name_copy(self):
        clipboard = QGuiApplication.clipboard()
        selected_index = self._audio_list_view.selectedIndexes()[0].row()
        item = self._audio_list_model.item(selected_index).text()

        clipboard.setText(item + ".ogg", QClipboard.Mode.Clipboard)

    def _handle_insert_into_cursor(self):
        selected_index = self._audio_list_view.selectedIndexes()[0].row()
        audio_name = self._audio_list_model.item(selected_index).text()

        # Construct the final command and emit it
        final_command = "mus {}".format(audio_name) if self.__AUDIO_FOLDER == MUSIC_FOLDER_NAME \
            else "sfx {}".format(audio_name)

        self.command_insert_at_cursor_requested.emit(final_command)

    def _handle_insert_music_loop_into_cursor(self):
        selected_index = self._audio_list_view.selectedIndexes()[0].row()
        audio_name = self._audio_list_model.item(selected_index).text()

        final_command = "set _music_loop {}".format(audio_name)

        self.command_insert_at_cursor_requested.emit(final_command)

    def _handle_current_change(self):
        self._play_button.setEnabled(len(self._audio_list_view.selectedIndexes()) > 0)

    def _handle_play_pressed(self):
        if self._pywright_dir == "":
            return
        if self._game_info is None:
            return

        folder_text = self._audio_folders_combo_box.currentText()

        folder_path = self._get_selected_audio_folder_path()

        # Revert the previous item back to its original icon
        if self._currently_playing_index is not None:
            self._audio_list_model.item(self._currently_playing_index.row()).setIcon(QIcon(self._get_audio_icon_name()))

        selected_index = self._audio_list_view.selectedIndexes()[0].row()
        selected_music = self._audio_list_model.item(selected_index).text()

        file_path = folder_path / "{}.ogg".format(selected_music)

        self._currently_playing_index = self._audio_list_view.selectedIndexes()[0]
        self._currently_playing_folder = folder_text
        self._audio_list_model.item(selected_index).setIcon(QIcon(self._get_playing_icon_name()))

        # Construct a path for the Music
        self.audio_play_requested.emit(str(file_path))

    def _get_audio_icon_name(self) -> str:
        return IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_AUDIO_FILE
                                               if self.__audio_type == AudioType.Sfx
                                               else IconThemes.ICON_NAME_MUSIC_FILE)

    def _get_playing_icon_name(self) -> str:
        return IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_AUDIO_FILE_PLAYING
                                               if self.__audio_type == AudioType.Sfx
                                               else IconThemes.ICON_NAME_AUDIO_PLAY)

    def _handle_stop_pressed(self):
        self.audio_stop_requested.emit()
        self.unset_currently_playing_icon()

    def set_currently_playing_icon(self):
        if self._currently_playing_index is not None:
            self._audio_list_model.item(self._currently_playing_index.row()).setIcon(
                QIcon(self._get_playing_icon_name())
            )

    def unset_currently_playing_icon(self):
        # Revert back to the original icon
        if self._currently_playing_index is not None:
            self._audio_list_model.item(self._currently_playing_index.row()).setIcon(QIcon(self._get_audio_icon_name()))
            self._currently_playing_index = None

    def clear_everything(self):
        self._game_info = None
        self._audio_list_model.removeRows(0, self._audio_list_model.rowCount())
        self._audio_folders_combo_box.clear()
        self._play_button.setEnabled(False)
        self._refresh_button.setEnabled(False)
