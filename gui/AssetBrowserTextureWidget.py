# Texture browser for Asset Browser
# Basically a redone IconPickerDialog :V

from pathlib import Path

from PyQt6.QtWidgets import QWidget, QListView, QFileIconProvider, QVBoxLayout, QComboBox, QMenu, QPushButton, \
    QHBoxLayout
from PyQt6.QtGui import QIcon, QPixmap, QDesktopServices, QClipboard, QGuiApplication, QFileSystemModel, QAction
from PyQt6.QtCore import QSize, QDir, Qt, QUrl, pyqtSignal, QFileSystemWatcher

from data.PyWrightGame import PyWrightGameInfo
from data import IconThemes

insertable_folders = ("bg", "ev", "fg")
accepted_types = (".png", ".jpg")
ICON_SIZE = QSize(192, 192)


class AssetManagerTextureWidget(QWidget):

    # Sends the new icon name
    game_icon_change_requested = pyqtSignal(str)

    # Sends the appropriate command
    command_insert_at_cursor_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pywright_dir = ""
        self._game_info: PyWrightGameInfo | None = None

        self._textures_list_view = QListView(self)
        self._textures_list_view.setViewMode(QListView.ViewMode.IconMode)
        self._textures_list_view.setResizeMode(QListView.ResizeMode.Adjust)
        self._textures_list_view.setUniformItemSizes(True)
        self._textures_list_view.setDragEnabled(False)
        self._textures_list_view.setSpacing(5)
        self._textures_list_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._textures_list_view.customContextMenuRequested.connect(self._handle_texture_context_menu)

        self._available_folders: list[str] = []

        self._folders_combo_box = QComboBox()
        self._folders_combo_box.currentIndexChanged.connect(self._handle_combobox_index_changed)

        self._refresh_button = QPushButton()
        self._refresh_button.setIcon(QIcon(IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_REFRESH)))
        self._refresh_button.setToolTip("Refresh current folder")
        self._refresh_button.setMaximumWidth(30)
        self._refresh_button.clicked.connect(self._refresh_texture_view)

        self._refresh_button.setEnabled(self._folders_combo_box.currentIndex() != -1)

        self.__file_system_watcher = QFileSystemWatcher(self)

        self.__file_system_watcher.directoryChanged.connect(self._handle_directory_contents_changed)

        main_layout = QVBoxLayout()

        combobox_layout = QHBoxLayout()
        combobox_layout.addWidget(self._folders_combo_box)
        combobox_layout.addWidget(self._refresh_button)

        main_layout.addLayout(combobox_layout)
        main_layout.addWidget(self._textures_list_view)

        self.setLayout(main_layout)

    def clear(self):
        self._pywright_dir = ""
        self._game_info = None
        self.__file_system_watcher.removePaths(self.__file_system_watcher.directories())

    def select_pywright(self, pywright_dir: str):
        self._pywright_dir = pywright_dir

    def set_selected_game(self, selected_game_info: PyWrightGameInfo):
        self._game_info = selected_game_info

    def _query_available_folders(self):
        self.__file_system_watcher.removePaths(self.__file_system_watcher.directories())

        if self._pywright_dir == "":
            return

        global_art_folder_path = Path("{}/art/".format(self._pywright_dir))

        global_art_folders = ["global/" + x.name for x in global_art_folder_path.iterdir() if x.is_dir()]

        game_art_folder_path = Path("{}/art/".format(self._game_info.game_path))
        game_art_folders = []
        game_art_subfolders = []

        if game_art_folder_path.exists():
            game_art_folders = [x.name for x in game_art_folder_path.iterdir() if x.is_dir()]

            # Iterate over subfolders as well

            game_art_subfolders = []

            for folder in game_art_folders:
                folder_path = Path("{}/art/{}".format(self._game_info.game_path, folder))
                game_art_subfolders.extend([folder + "/" + x.name for x in folder_path.iterdir() if x.is_dir()])

        self._available_folders = global_art_folders + game_art_folders + game_art_subfolders

        self.__file_system_watcher.addPaths(self._available_folders)

    def refresh_art_folders(self):
        self._query_available_folders()
        self._folders_combo_box.clear()
        self._folders_combo_box.addItems(self._available_folders)
        self._refresh_texture_view()

    def _refresh_texture_view(self):
        subfolder_name = self._folders_combo_box.currentText()

        is_global = subfolder_name.startswith("global/")

        root_folder = self._pywright_dir if is_global or self._game_info is None else self._game_info.game_path

        if is_global:
            subfolder_name = subfolder_name.split("global/", maxsplit=1)[1]

        folder_path = Path("{}/art/{}".format(root_folder, subfolder_name))

        fs_model = QFileSystemModel()
        icon_provider = ThumbnailIconProvider()

        fs_model.setIconProvider(icon_provider)

        name_filters = ["*.png", "*.PNG", "*.jpg", "*.JPG"]
        fs_model.setFilter(QDir.Filter.Files)
        fs_model.setNameFilters(name_filters)
        fs_model.setNameFilterDisables(False)

        self._textures_list_view.setModel(fs_model)
        self._textures_list_view.setRootIndex(fs_model.setRootPath(str(folder_path)))

    def _handle_combobox_index_changed(self):
        self._refresh_button.setEnabled(self._folders_combo_box.currentIndex() != -1)
        self._refresh_texture_view()

    def _handle_directory_contents_changed(self, path: str):
        if path == self._folders_combo_box.currentText():
            self._refresh_texture_view()

    def _handle_texture_context_menu(self, position):
        if self._game_info is None:
            return

        indexes = self._textures_list_view.selectedIndexes()

        menu = QMenu()

        # Possible actions on Textures

        use_as_game_icon_action = QAction("Use as Game Icon", self)
        use_as_game_icon_action.triggered.connect(self._handle_use_as_game_icon)
        use_as_game_icon_action.setStatusTip("Use the selected texture as the Game Icon")
        copy_texture_name_action = QAction("Copy Texture\'s name", self)
        copy_texture_name_action.triggered.connect(self._handle_texture_name_copy)
        copy_texture_name_action.setStatusTip("Copy selected texture's name to the clipboard")
        insert_into_current_script_action = QAction("Insert into current script from cursor position", self)
        insert_into_current_script_action.triggered.connect(self._handle_insert_into_cursor)
        insert_into_current_script_action.setStatusTip("Insert the selected texture as a "
                                                       "command into the currently open "
                                                       "script from the cursor position")
        open_folder_action = QAction("Open current folder in File Manager", self)
        open_folder_action.triggered.connect(self._handle_open_current_folder)
        open_folder_action.setStatusTip("Open the current texture folder in the default File Manager")

        # Add the relevant actions for the selected texture, if there is any
        if len(indexes) > 0:
            subfolder_name = self.__get_subfolder_name()

            menu.addAction(copy_texture_name_action)
            if subfolder_name in insertable_folders:
                menu.addAction(use_as_game_icon_action)
                menu.addAction(insert_into_current_script_action)
            menu.addSeparator()

        menu.addAction(open_folder_action)

        menu.exec(self.mapToGlobal(position))

    def _handle_texture_name_copy(self):
        clipboard = QGuiApplication.clipboard()
        index = self._textures_list_view.selectedIndexes()[0]
        model: QFileSystemModel = index.model()
        texture_name = model.fileName(index)  # Obtains the file extension as well

        clipboard.setText(texture_name, QClipboard.Mode.Clipboard)

    def _handle_use_as_game_icon(self):
        subfolder_name = self.__get_subfolder_name()

        index = self._textures_list_view.selectedIndexes()[0]
        model: QFileSystemModel = index.model()

        texture_name = model.fileName(index)  # Obtains the file extension as well

        final_icon_path = "art/{}/{}".format(subfolder_name, texture_name)

        self.game_icon_change_requested.emit(final_icon_path)

    def _handle_insert_into_cursor(self):
        # Obtain the directory name to use as command
        subfolder_name = self.__get_subfolder_name()

        # Obtain the texture name to use as parameter
        index = self._textures_list_view.selectedIndexes()[0]
        model: QFileSystemModel = index.model()

        texture_name = Path(model.fileName(index)).stem

        # Construct the final command and emit it
        final_command = "{} {}".format(subfolder_name, texture_name)

        self.command_insert_at_cursor_requested.emit(final_command)

    def _handle_open_current_folder(self):
        subfolder_name = self._folders_combo_box.currentText()

        is_global = subfolder_name.startswith("global/")

        if self._game_info is not None:
            root_folder = self._pywright_dir if is_global else self._game_info.game_path
        else:
            root_folder = self._pywright_dir

        if is_global:
            subfolder_name = subfolder_name.split("global/", maxsplit=1)[1]

        folder_path = Path("{}/art/{}".format(root_folder, subfolder_name))
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder_path)))

    def __get_subfolder_name(self) -> str:
        subfolder_name = self._folders_combo_box.currentText()
        is_global = subfolder_name.startswith("global/")

        if is_global:
            subfolder_name = subfolder_name.split("global/", maxsplit=1)[1]

        return subfolder_name

    def clear_everything(self):
        self.clear()
        self._textures_list_view.setModel(None)
        self._folders_combo_box.clear()
        self._refresh_button.setEnabled(False)


class ThumbnailIconProvider(QFileIconProvider):
    """Custom Icon Provider class that also provides thumbnails for image files"""

    def __init__(self):
        super().__init__()

    def icon(self, icon_type: QFileIconProvider.IconType) -> QIcon:
        fn: str = icon_type.filePath()

        if fn.endswith(accepted_types):
            a = QPixmap(ICON_SIZE)
            a.load(fn)
            return QIcon(a)

        return super().icon(icon_type)
