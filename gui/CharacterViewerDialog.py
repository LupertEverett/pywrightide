from PyQt6.QtCore import QSize, Qt, QTimer, pyqtSignal

from PyQt6.QtGui import QPixmap, QIcon, QGuiApplication, QAction
from PyQt6.QtWidgets import QDialog, QComboBox, QLabel, QVBoxLayout, QHBoxLayout, QSpinBox, QLayout, QPushButton, \
    QSlider, QGroupBox, QToolBar, QFileDialog

from .SpriteViewWidget import SpriteViewWidget
from .ImportImageAsCharacterDialog import ImportImageAsCharacterDialog
from .ImportFolderAsCharacterDialog import ImportFolderAsCharacterDialog

from data.PyWrightGame import CurrentPyWrightGame
from data.SpriteSheet import SpriteSheet
from data import IconThemes

from pathlib import Path

GAME_TICK_RATE = 1000 / 60 # 60 FPS


class CharacterViewerDialog(QDialog):

    # Sends the appropriate command
    command_insert_at_cursor_requested = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__(parent)

        self.setWindowTitle("Character Viewer")

        self._character_combobox = QComboBox(self)
        self._character_combobox.currentIndexChanged.connect(self._handle_character_combobox_changed)
        self._emotion_combobox = QComboBox(self)
        self._emotion_combobox.currentIndexChanged.connect(self._handle_emotion_combobox_changed)

        self._toolbar = QToolBar(self)

        # These have to be created earlier than frame number spinbox
        self._frame_delay_spinbox = QSpinBox(self)
        self._frame_delay_spinbox.setRange(0, 1000)
        self._frame_delay_spinbox.setValue(6)
        self._frame_delay_spinbox.setEnabled(False) # Disable for now

        self._frame_sfx_picker = QComboBox()
        self._populate_sfx_combobox()
        self._frame_sfx_picker.setEnabled(False) # Disable for now

        self._frame_number_spinbox = QSpinBox()
        self._frame_number_spinbox.valueChanged.connect(self._handle_frame_number_value_changed)
        self._frame_count_label = QLabel("of 1")

        self._image_label = SpriteViewWidget()
        self._current_frame_pixmap = QPixmap()
        self._image_label.resize(768, 576)
        self._image_label.setPixmap(self._current_frame_pixmap)

        play_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_AUDIO_PLAY)
        stop_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_AUDIO_STOP)
        self._play_icon = QIcon(play_icon_path)
        self._stop_icon = QIcon(stop_icon_path)

        self._play_button = QPushButton()
        self._play_button.setIcon(self._play_icon)
        self._play_button.setToolTip("Play animation")
        self._play_button.clicked.connect(self._handle_play_button_pressed)

        self._frame_slider = QSlider(Qt.Orientation.Horizontal)
        self._frame_slider.valueChanged.connect(self._handle_slider_value_changed)

        self._copy_to_clipboard_button = QPushButton("Copy to clipboard")
        self._copy_to_clipboard_button.setToolTip("Copy the current character and emotion to clipboard as a command")
        self._copy_to_clipboard_button.clicked.connect(self._handle_copy_to_clipboard_pressed)

        self._close_button = QPushButton("Close")
        self._close_button.clicked.connect(self.accept)

        self._insert_into_current_cursor_position_button = QPushButton("Insert into cursor position")
        self._insert_into_current_cursor_position_button.setToolTip("Insert the command for the current character and emotion into the current cursor position")
        self._insert_into_current_cursor_position_button.clicked.connect(self._handle_insert_to_cursor_button_pressed)

        self._spritesheet : SpriteSheet | None = None

        self._populate_character_combobox()

        self._is_playing_anim = False

        self._next_frame_timer : QTimer | None = None

        # Toolbar items
        self._toolbar.setIconSize(QSize(32, 32))

        import_single_image_icon = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_IMPORT_IMAGE_AS_CHARACTER)
        self._import_single_image_action = QAction(QIcon(import_single_image_icon), "Import Single Image")
        self._import_single_image_action.triggered.connect(self._handle_single_image_action_triggered)

        import_image_folder_icon = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_IMPORT_FOLDER_AS_CHARACTER)
        self._import_image_folder_action = QAction(QIcon(import_image_folder_icon), "Import Folder as Character")
        self._import_image_folder_action.triggered.connect(self._handle_image_folder_action_triggered)

        self._toolbar.addAction(self._import_single_image_action)
        self._toolbar.addAction(self._import_image_folder_action)

        #  Layout
        main_layout = QVBoxLayout()
        sub_layout = QHBoxLayout()

        frame_info_layout = QHBoxLayout()

        viewer_layout = QVBoxLayout()

        character_layout = QHBoxLayout()
        character_layout.addWidget(QLabel("Character:"))
        character_layout.addWidget(self._character_combobox)

        emotion_layout = QHBoxLayout()
        emotion_layout.addWidget(QLabel("Emotion:"))
        emotion_layout.addWidget(self._emotion_combobox)

        frame_selector_layout = QHBoxLayout()
        frame_selector_layout.addWidget(self._play_button)
        frame_selector_layout.addWidget(self._frame_slider)
        frame_selector_layout.addWidget(QLabel("Frame: "))
        frame_selector_layout.addWidget(self._frame_number_spinbox)
        frame_selector_layout.addWidget(self._frame_count_label)

        bottom_buttons_layout = QHBoxLayout()
        bottom_buttons_layout.addWidget(self._copy_to_clipboard_button)
        bottom_buttons_layout.addWidget(self._insert_into_current_cursor_position_button)
        bottom_buttons_layout.addStretch()
        bottom_buttons_layout.addWidget(self._close_button)

        frame_info_layout.addWidget(QLabel("Frame Delay (in ticks):"))
        frame_info_layout.addStretch()
        frame_info_layout.addWidget(self._frame_delay_spinbox)
        frame_info_layout.addStretch()
        frame_info_layout.addWidget(QLabel("SFX to play:"))
        frame_info_layout.addStretch()
        frame_info_layout.addWidget(self._frame_sfx_picker)

        viewer_layout.addLayout(character_layout)
        viewer_layout.addLayout(emotion_layout)
        viewer_layout.addLayout(frame_selector_layout)
        viewer_layout.addLayout(frame_info_layout)
        viewer_layout.addWidget(self._image_label)
        viewer_layout.addLayout(bottom_buttons_layout)

        sub_layout.addLayout(viewer_layout)

        sub_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        main_layout.addWidget(self._toolbar)
        main_layout.addLayout(sub_layout)

        self.setLayout(main_layout)

    def _populate_character_combobox(self):
        port_path = CurrentPyWrightGame().current_game.game_path / "art" / "port"

        self._character_combobox.addItems(sorted([x.stem for x in port_path.iterdir() if x.is_dir()], key=str.casefold))

    def _handle_character_combobox_changed(self):
        if self._character_combobox.count() == 0:
            return

        self._populate_emotion_combobox()

    def _handle_emotion_combobox_changed(self):
        if self._emotion_combobox.count() == 0:
            return

        character = self._character_combobox.currentText()
        emotion = self._emotion_combobox.currentText() + ".png"
        file_path = CurrentPyWrightGame().current_game.game_path / "art" / "port" / character / emotion

        self._spritesheet = SpriteSheet(file_path)

        self._play_button.setEnabled(self._spritesheet.num_frames > 1)
        self._frame_slider.setEnabled(self._spritesheet.num_frames > 1)
        self._frame_number_spinbox.setEnabled(self._spritesheet.num_frames > 1)

        self._frame_count_label.setText("of {}".format(self._spritesheet.num_frames))
        self._frame_number_spinbox.setRange(1, self._spritesheet.num_frames)
        self._frame_slider.setRange(1, self._spritesheet.num_frames)
        self._frame_number_spinbox.setValue(1) # This will also set the frame_slider's value implicitly

        frame = self._spritesheet.get_frame(0)
        self._current_frame_pixmap = QPixmap.fromImage(frame).scaled(self._image_label.width(), self._image_label.height(), Qt.AspectRatioMode.KeepAspectRatio)
        self._image_label.setPixmap(self._current_frame_pixmap)

    def _populate_emotion_combobox(self):
        self._emotion_combobox.clear()
        character_path = CurrentPyWrightGame().current_game.game_path / "art" / "port" / self._character_combobox.currentText()

        self._emotion_combobox.addItems([x.stem for x in character_path.iterdir() if x.is_file() and x.suffix == ".png"])

    def _populate_sfx_combobox(self):
        self._frame_sfx_picker.clear()
        self._frame_sfx_picker.addItem("<None>")

        game_sfx_path = CurrentPyWrightGame().current_game.game_path / "sfx"
        global_sfx_path = CurrentPyWrightGame().current_pywright_folder_path / "sfx"

        # Game SFX files should take precedence
        # To do that we query the files in both global and game specific folders
        # Then "remove" the repeating entries in global folders
        new_sfx_list = {x.name for x in game_sfx_path.iterdir() if x.is_file() and x.suffix == ".ogg"}
        global_sfx_list = {x.name for x in global_sfx_path.iterdir() if x.is_file() and x.suffix == ".ogg"}

        new_sfx_list = sorted(new_sfx_list.union(global_sfx_list))

        self._frame_sfx_picker.addItems(new_sfx_list)

    def _handle_frame_number_value_changed(self):
        frame_num = self._frame_number_spinbox.value() - 1

        if self._frame_slider.value() != self._frame_number_spinbox.value():
            self._frame_slider.setValue(self._frame_number_spinbox.value())

        frame = self._spritesheet.get_frame(frame_num)
        self._current_frame_pixmap = QPixmap.fromImage(frame)
        self._image_label.setPixmap(self._current_frame_pixmap)

        self._frame_delay_spinbox.setValue(self._spritesheet.get_framedelay_for_frame(frame_num))

        # Set the value of SFX picker
        sfx = self._spritesheet.get_sfx_path_for_frame(frame_num)

        idx = -1

        if sfx != "":
            idx = self._frame_sfx_picker.findText(sfx)

        if idx != -1:
            self._frame_sfx_picker.setCurrentIndex(idx)
        else:
            self._frame_sfx_picker.setCurrentIndex(0)


    def _handle_slider_value_changed(self):
        if self._frame_slider.value() != self._frame_number_spinbox.value():
            self._frame_number_spinbox.setValue(self._frame_slider.value())

    def _handle_insert_to_cursor_button_pressed(self):
        command = "char {} e={}".format(self._character_combobox.currentText(), self._emotion_combobox.currentText())
        self.command_insert_at_cursor_requested.emit(command)

    def _handle_copy_to_clipboard_pressed(self):
        command = "char {} e={}".format(self._character_combobox.currentText(), self._emotion_combobox.currentText())
        clipboard = QGuiApplication.clipboard()

        clipboard.setText(command)

    def _handle_play_button_pressed(self):
        frame_num = self._frame_number_spinbox.value() - 1

        if frame_num >= self._spritesheet.num_frames - 1:
            self._frame_number_spinbox.setValue(1)
            frame_num = 0

        self._is_playing_anim = not self._is_playing_anim

        self._play_button.setIcon(self._stop_icon if self._is_playing_anim else self._play_icon)
        self._play_button.setToolTip("Stop animation" if self._is_playing_anim else "Play animation")

        self._frame_number_spinbox.setEnabled(not self._is_playing_anim)
        self._frame_slider.setEnabled(not self._is_playing_anim)
        self._character_combobox.setEnabled(not self._is_playing_anim)
        self._emotion_combobox.setEnabled(not self._is_playing_anim)

        if not self._is_playing_anim:
            self._next_frame_timer.stop()
            return

        self._next_frame_timer = QTimer()
        self._next_frame_timer.setSingleShot(True)
        self._next_frame_timer.timeout.connect(self._handle_next_frame_timeout)
        self._next_frame_timer.start(0)

    def _handle_next_frame_timeout(self):
        frame_num = self._frame_number_spinbox.value() - 1
        
        if frame_num >= self._spritesheet.num_frames - 1:
            self._frame_number_spinbox.setValue(1)
            frame_num = 0
        else:
            frame_num += 1
            self._frame_number_spinbox.setValue(frame_num + 1)
            
        current_framedelay = self._spritesheet.get_framedelay_for_frame(frame_num)
        self._next_frame_timer.start(int(current_framedelay * GAME_TICK_RATE))

    def _handle_single_image_action_triggered(self):
        file_name = QFileDialog.getOpenFileName(self, "Open .gif/.webp File",
                                                str(CurrentPyWrightGame().current_pywright_folder_path),
                                                "Animated Image Files (*.gif *.webp)")

        if file_name[0] != "":
            dialog = ImportImageAsCharacterDialog(Path(file_name[0]), self)
            if dialog.exec():
                self._character_combobox.clear()
                self._populate_character_combobox()
                # Switch to the newly added character/emotion
                idx = self._character_combobox.findText(dialog.get_character_name())

                if idx != -1:
                    self._character_combobox.setCurrentIndex(idx)

                idx = self._emotion_combobox.findText(dialog.get_emotion_name())

                if idx != -1:
                    self._emotion_combobox.setCurrentIndex(idx)


    def _handle_image_folder_action_triggered(self):
        folder_name = QFileDialog.getExistingDirectory(self, "Import Folder as Character", str(CurrentPyWrightGame().current_pywright_folder_path))

        if folder_name != "":
            dialog = ImportFolderAsCharacterDialog(Path(folder_name), self)

            if dialog.exec():
                self._character_combobox.clear()
                self._populate_character_combobox()
                # Switch to the newly added character
                idx = self._character_combobox.findText(dialog.get_character_name())

                if idx != -1:
                    self._character_combobox.setCurrentIndex(idx)
