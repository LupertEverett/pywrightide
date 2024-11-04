# Custom Icon Picker Dialog.
# Checks through the subfolders in {PyWright Dir}/art/

from pathlib import Path

from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QComboBox, QCheckBox,
                             QListView, QFileIconProvider,
                             QHBoxLayout, QVBoxLayout, QMessageBox)
from PyQt6.QtGui import QPixmap, QIcon, QFileSystemModel
from PyQt6.QtCore import QDir, QSize, Qt

from data.PyWrightGame import PyWrightGame, PyWrightGameInfo

accepted_types = (".png", ".jpg")
ICON_SIZE = QSize(128, 128)


class IconPickerDialog(QDialog):

    def __init__(self, pywright_root_dir: str, selected_game_info: PyWrightGameInfo | None = None, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Pick an Icon")

        self._pywright_root_dir = pywright_root_dir

        self._selected_game_info = selected_game_info

        self._subfolder_combobox = QComboBox()
        self._subfolder_combobox.currentIndexChanged.connect(self._refresh_icon_view)

        self._global_folder_checkbox = QCheckBox("Check the global art folder?")
        self._global_folder_checkbox.setChecked(True)
        enabled_condition = self._selected_game_info is not None and (self._selected_game_info.game_path / "art").exists()
        # enabled_condition = self._selected_game.is_a_game_selected() \
        #                     and Path("{}/art/".format(self._selected_game.game_path)).exists()
        self._global_folder_checkbox.setEnabled(enabled_condition)
        self._global_folder_checkbox.clicked.connect(self._refresh_subfolders)
        self._global_folder_checkbox.setWhatsThis("If checked, the icon picker will query the jpg and png files in the "
                                                  "art folder of PyWright installation, otherwise it will "
                                                  "query the selected game's art folder instead, if it exists.")

        self._icons_list_view = QListView()
        self._icons_list_view.setViewMode(QListView.ViewMode.IconMode)
        self._icons_list_view.setResizeMode(QListView.ResizeMode.Adjust)
        self._icons_list_view.setUniformItemSizes(True)
        self._icons_list_view.setSpacing(5)
        self._icons_list_view.doubleClicked.connect(self._handle_accept)

        self._dialog_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self._dialog_box.accepted.connect(self._handle_accept)
        self._dialog_box.rejected.connect(self.reject)

        self._art_subfolders = []
        self._refresh_subfolders()

        self.selected_icon = ""

        self.setLayout(self._prepare_layout())

    def _prepare_layout(self) -> QVBoxLayout:
        result = QVBoxLayout()

        top_bar = QHBoxLayout()
        top_bar.addWidget(self._subfolder_combobox)
        top_bar.addStretch()
        top_bar.addWidget(self._global_folder_checkbox)

        result.addLayout(top_bar)
        result.addWidget(self._icons_list_view)
        result.addWidget(self._dialog_box)

        return result

    def _refresh_subfolders(self):
        self._art_subfolders = self._query_subfolders()
        self._subfolder_combobox.clear()
        self._subfolder_combobox.addItems(self._art_subfolders)
        self._refresh_icon_view()

    def _query_subfolders(self):
        checking_root_art = self._global_folder_checkbox.isChecked()

        selected_root_folder = self._pywright_root_dir if checking_root_art else str(self._selected_game_info.game_path)

        art_folder_path = Path("{}/art/".format(selected_root_folder))

        if not art_folder_path.exists() or not art_folder_path.is_dir():
            raise FileNotFoundError("art folder doesn't exist!")

        return [x.name for x in art_folder_path.iterdir() if x.is_dir()]

    def _refresh_icon_view(self):
        subfolder_name = self._subfolder_combobox.currentText()

        checking_root_art = self._global_folder_checkbox.isChecked()
        selected_root_folder = self._pywright_root_dir if checking_root_art else str(self._selected_game_info.game_path)

        folder_path = Path("{}/art/{}".format(selected_root_folder, subfolder_name))

        fs_model = QFileSystemModel()
        icon_provider = ThumbnailIconProvider()

        fs_model.setIconProvider(icon_provider)

        name_filters = ["*.png", "*.jpg"]
        fs_model.setFilter(QDir.Filter.Files)
        fs_model.setNameFilters(name_filters)
        fs_model.setNameFilterDisables(False)

        self._icons_list_view.setModel(fs_model)
        self._icons_list_view.setRootIndex(fs_model.setRootPath(str(folder_path)))

    def _handle_accept(self):
        if len(self._icons_list_view.selectedIndexes()) <= 0:
            QMessageBox.critical(self, "Error", "Nothing has selected!")
            return

        name = self._icons_list_view.model().data(self._icons_list_view.selectedIndexes()[0],
                                                  Qt.ItemDataRole.DisplayRole)
        self.selected_icon = "art/" + self._subfolder_combobox.currentText() + "/" + name
        self.accept()


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
