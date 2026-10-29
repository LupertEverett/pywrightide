from pathlib import Path

from PyQt6.QtCore import QSize, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, \
    QCheckBox, QTreeWidget, QTreeWidgetItem, QFileDialog, QMessageBox

from data import IDESettings, IconThemes, PyWrightFolder
from data.PyWrightGame import PyWrightGameInfo
from gui.NewGameDialog import NewGameDialog
from gui.OpenGameDialog import OpenGameDialog

_welcome_label_text = "<h1>Welcome to PyWright IDE!</h1>"

_folder_does_not_exist_notice_text = """<b>Notice:</b> Last open game ({})'s folder has been either moved or deleted. Please select a different folder from below.
""".format(Path(IDESettings.get_autoload_last_game_path()).stem)

FALLBACK_GAME_ICON_PATH = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_PYWRIGHT)


class WelcomeWidget(QWidget):
    game_path_selected = pyqtSignal(Path)
    settings_selected = pyqtSignal()
    about_selected = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self._recent_docs = [path for path in IDESettings.get_recent_games()
                             if Path(path).exists() and Path(path).is_dir()]

        # Header widgets
        ide_icon_label = QLabel("")
        icon_pixmap = QPixmap("res/icons/ideicon.png")
        icon_pixmap = icon_pixmap.scaled(48, 48)
        ide_icon_label.setPixmap(icon_pixmap)
        label_size = QSize(icon_pixmap.width() + 2, icon_pixmap.height() + 2)
        ide_icon_label.setFixedSize(label_size)
        welcome_label = QLabel(_welcome_label_text)

        last_game_path = Path(IDESettings.get_autoload_last_game_path())
        last_game_exists = last_game_path.exists() and last_game_path.is_dir()

        info_label = InfoBannerWidget(_folder_does_not_exist_notice_text, self)

        info_label.setVisible(not last_game_exists)

        separator_line = QFrame()
        separator_line.setFrameShape(QFrame.Shape.VLine)

        self._new_game_button = QPushButton("Create New Game")
        new_game_icon = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_NEW_GAME)
        self._new_game_button.setIcon(QIcon(new_game_icon))
        self._new_game_button.setStyleSheet("text-align: left")
        self._new_game_button.setFlat(True)
        self._new_game_button.pressed.connect(self._handle_new_game_clicked)

        self._open_game_button = QPushButton("Open Game")
        open_game_icon = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_OPEN_GAME)
        self._open_game_button.setIcon(QIcon(open_game_icon))
        self._open_game_button.setStyleSheet("text-align: left")
        self._open_game_button.setFlat(True)
        self._open_game_button.pressed.connect(self._handle_load_game_clicked)

        self._settings_button = QPushButton("Settings")
        settings_icon = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_SETTINGS)
        self._settings_button.setIcon(QIcon(settings_icon))
        self._settings_button.setStyleSheet("text-align: left")
        self._settings_button.setFlat(True)
        self._settings_button.pressed.connect(lambda: self.settings_selected.emit())

        self._about_button = QPushButton("About")
        about_icon = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_ABOUT)
        self._about_button.setIcon(QIcon(about_icon))
        self._about_button.setStyleSheet("text-align: left")
        self._about_button.setFlat(True)
        self._about_button.pressed.connect(lambda: self.about_selected.emit())

        self._always_autoload_checkbox = QCheckBox("Always load the last opened game at startup (skips this screen)")
        self._always_autoload_checkbox.setChecked(IDESettings.get_autoload_last_game_check())
        self._always_autoload_checkbox.checkStateChanged.connect(lambda: IDESettings.set_autoload_last_game_check(self._always_autoload_checkbox.isChecked()))

        self.previous_games_list = QTreeWidget()

        self.previous_games_list.setColumnCount(3)
        self.previous_games_list.setHeaderLabels(["Name", "Author", "Path"])
        self.previous_games_list.setIconSize(QSize(64, 64))

        self.previous_games_list.clicked.connect(self._handle_load_selected_clicked)

        for path in self._recent_docs:
            self.__add_item_to_model(path)

        self.previous_games_list.resizeColumnToContents(0)
        self.previous_games_list.resizeColumnToContents(1)

        buttons_layout = QVBoxLayout()

        previous_games_layout = QVBoxLayout()

        header_layout = QHBoxLayout()

        body_layout = QHBoxLayout()

        main_layout = QVBoxLayout()

        header_layout.addStretch()
        header_layout.addWidget(ide_icon_label)
        header_layout.addWidget(welcome_label)
        header_layout.addStretch()

        buttons_layout.addWidget(self._new_game_button)
        buttons_layout.addWidget(self._open_game_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self._settings_button)
        buttons_layout.addWidget(self._about_button)

        previous_games_layout.addWidget(QLabel("Previous Games:"))
        previous_games_layout.addWidget(self.previous_games_list)
        previous_games_layout.addWidget(self._always_autoload_checkbox)

        body_layout.addSpacing(20)
        body_layout.addLayout(buttons_layout)
        body_layout.addWidget(separator_line)
        body_layout.addLayout(previous_games_layout)
        body_layout.addSpacing(20)

        main_layout.addSpacing(20)
        main_layout.addLayout(header_layout)
        main_layout.addWidget(info_label)
        main_layout.addLayout(body_layout)
        main_layout.addSpacing(20)

        self.setLayout(main_layout)

    def _handle_new_game_clicked(self):
        new_game_dialog = NewGameDialog("", self)

        if new_game_dialog.exec():
            game_path = new_game_dialog.get_new_game().game_path

            if str(game_path) not in self._recent_docs:
                self._recent_docs.insert(0, str(game_path))
                IDESettings.set_recent_games(self._recent_docs)

            self._emit_game_path_selected(game_path)

    def _handle_load_game_clicked(self):
        picker = QFileDialog.getExistingDirectory(self)

        if picker != "":
            picker = Path(picker)  # Correct the folder separators

            if PyWrightGameInfo.is_valid_game_folder(Path(picker)):
                if str(picker) not in self._recent_docs:
                    self._recent_docs.insert(0, str(picker))
                    IDESettings.set_recent_games(self._recent_docs)

                self._emit_game_path_selected(picker)
            elif PyWrightFolder.is_valid_pywright_folder(str(picker)):
                open_game_dialog = OpenGameDialog(str(picker), self)

                if open_game_dialog.exec():
                    final_path = picker / "games" / open_game_dialog.selected_game

                    # Check if the item has already added before
                    if str(final_path) not in self._recent_docs:
                        self._recent_docs.insert(0, str(final_path))
                        IDESettings.set_recent_games(self._recent_docs)

                    self._emit_game_path_selected(final_path)
            else:
                QMessageBox.critical(self, "Error", "Could not find a PyWright game!")

    def _handle_load_selected_clicked(self):
        indexes = self.previous_games_list.selectedIndexes()

        if len(indexes) < 1:
            return

        idx = indexes[0].row()

        game_path = self._recent_docs.pop(idx)

        # Move the selected path to the top
        self._recent_docs.insert(0, game_path)

        self._emit_game_path_selected(Path(game_path))

    def _emit_game_path_selected(self, path: Path):
        IDESettings.set_autoload_last_game_check(self._always_autoload_checkbox.isChecked())
        if self._always_autoload_checkbox.isChecked():
            IDESettings.set_autoload_last_game_path(str(path))

        self.game_path_selected.emit(path)

    def is_autoload_checkbox_ticked(self):
        return self._always_autoload_checkbox.isChecked()

    def set_autoload_checkbox_ticked(self, new_value: bool):
        self._always_autoload_checkbox.setChecked(new_value)

    def __add_item_to_model(self, text: str):
        try:
            (title, author, version, icon_path) = PyWrightGameInfo.get_game_data_info(Path(text))
            # Try to load the game's icon
            # Use the fallback icon if loading fails
            if str(icon_path) != "":
                icon_pixmap = QPixmap(str(icon_path))
            else:
                icon_pixmap = QPixmap(FALLBACK_GAME_ICON_PATH)

            if title != "":
                title = Path(text).stem

            if author == "":
                author = "Unknown Author"

            new_row = QTreeWidgetItem()
            new_row.setIcon(0, QIcon(icon_pixmap))
            new_row.setText(0, title)
            new_row.setText(1, author)
            new_row.setText(2, text)

            self.previous_games_list.addTopLevelItem(new_row)

        except FileNotFoundError:
            pass


class InfoBannerWidget(QFrame):

    def __init__(self, text: str, parent):
        super().__init__(parent)

        self._info_label = QLabel(text)
        self._quit_button = QPushButton("X")
        self.setObjectName("InfoBox")

        self._quit_button.setFixedWidth(25)
        self._quit_button.setFlat(True)
        self._quit_button.pressed.connect(self.hide)
        self._quit_button.setToolTip("Dismiss")
        self.setFrameStyle(QFrame.Shape.StyledPanel)

        self.setStyleSheet(""" QFrame#InfoBox {
            background-color: #62fcd8;
            border: 1px solid #1bd3a8;
            border-radius: 4px;
        }""")

        self._quit_button.setStyleSheet("""QPushButton:hover {
            color: white;
            background-color: #e52d3d;
            border: 1px solid #ef1527;
            border-radius: 4px;
        }
        QPushButton:pressed {
            color: white;
            background-color: #ef1527;
            border: 1px solid #e52d3d;
            border-radius: 4px;
        }
        """)

        main_layout = QHBoxLayout()

        main_layout.addWidget(self._info_label)
        main_layout.addStretch()
        main_layout.addWidget(self._quit_button)

        self.setLayout(main_layout)

    def set_info_text(self, new_text: str):
        self._info_label.setText(new_text)