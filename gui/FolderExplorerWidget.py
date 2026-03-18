"""
Folder Explorer Widget: Contains two views for the current PyWright Game directory
- Scripts View, which only lists scripts contained within the cases, and
- Directory View, which displays the whole folder
"""
from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon, QFileSystemModel
from PyQt6.QtWidgets import QDockWidget, QTabWidget, QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QTreeView

from .ScriptsViewWidget import ScriptsViewWidget
from .DirectoryViewWidget import DirectoryViewWidget
from .FolderBrowserView import FolderBrowserView

from data import IconThemes
from data.PyWrightGame import PyWrightGameInfo


class FolderExplorerWidget(QDockWidget):

    open_new_tab = pyqtSignal(str)
    open_game_properties_tab = pyqtSignal()
    directory_changed = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("Folder Explorer")
        self.setObjectName("FolderExplorerWidget")

        self._pywright_game_info: PyWrightGameInfo | None = None

        self._game_title_label = QLabel()

        game_properties_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_SETTINGS)
        self._game_properties_button = QPushButton(QIcon(game_properties_icon_path), "")
        self._game_properties_button.setToolTip("Game Properties")
        self._game_properties_button.setEnabled(False)
        self._game_properties_button.setFlat(True)
        self._game_properties_button.setMaximumWidth(30)
        self._game_properties_button.clicked.connect(self._handle_properties_button_clicked)

        self._scripts_view_widget = ScriptsViewWidget(self)
        self._directory_view_widget = FolderBrowserView(self)

        self._tab_widget = QTabWidget(self)
        # self._tab_widget.setTabPosition(QTabWidget.TabPosition.West)
        self._tab_widget.addTab(self._scripts_view_widget, "Scripts View")
        self._tab_widget.addTab(self._directory_view_widget, "Directory View")

        self._directory_view_widget.open_new_tab.connect(self._handle_open_new_tab_signal)
        self._scripts_view_widget.open_new_tab.connect(self._handle_open_new_tab_signal)

        dummy_title_bar = QWidget(self)
        dummy_title_bar.setLayout(QHBoxLayout())
        dummy_title_bar.layout().setContentsMargins(2, 2, 2, 2)

        self._top_widget = self._create_custom_title_bar()

        self._main_widget = QWidget()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._top_widget)
        main_layout.addWidget(self._tab_widget)

        self._main_widget.setLayout(main_layout)

        self.setTitleBarWidget(dummy_title_bar)
        self.setWidget(self._main_widget)

    def set_pywright_game(self, game_info: PyWrightGameInfo):
        self._pywright_game_info = game_info
        self._game_title_label.setText(self._pywright_game_info.game_title)
        self._switch_to_folder(self._pywright_game_info.game_path)
        self._directory_view_widget.select_pywright_game(game_info)

    def _handle_properties_button_clicked(self):
        self.open_game_properties_tab.emit()

    def _handle_open_new_tab_signal(self, folder_path: str):
        self.open_new_tab.emit(folder_path)

    def _switch_to_folder(self, folder_path: Path):
        self._scripts_view_widget.switch_to_directory(folder_path)

    def _create_custom_title_bar(self):
        result = QWidget()

        layout = QHBoxLayout()
        layout.addWidget(self._game_title_label)
        layout.addStretch()
        layout.addWidget(self._game_properties_button)
        layout.setContentsMargins(4, 0, 2, 0)

        result.setLayout(layout)
        return result
