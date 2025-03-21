from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem, QPixmap

from pathlib import Path

from data import IconThemes
from data.PyWrightGame import PyWrightGameInfo

TEXT_HTML = """
    <h2 style="margin:0; line-height: 20px; height: 10px;">{}</h2>
    <h4 style="margin:0; line-height: 5px; height: 5px;">{}</h4>
    {}
"""

FALLBACK_GAME_ICON_PATH = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_PYWRIGHT)


class PyWrightGamePathItem(QStandardItem):

    def __init__(self, path_str: str):
        super().__init__()

        self.path_str = path_str
        self.parent_path = Path(self.path_str).parent
        self.game_name = Path(self.path_str).stem

        # Try to load the game's icon
        # Use the fallback icon if the loading fails
        try:
            (title, author, version, icon_path) = PyWrightGameInfo.get_game_data_info(Path(path_str))
            if str(icon_path) != "":
                icon_pixmap = QPixmap(str(icon_path))
            else:
                icon_pixmap = QPixmap(FALLBACK_GAME_ICON_PATH)
        except FileNotFoundError:
            author = "Unknown Author"
            icon_pixmap = QPixmap(FALLBACK_GAME_ICON_PATH)

        author_text = "By " + author if author != "" else ""
        path_text = TEXT_HTML.format(self.game_name, author_text, self.parent_path)
        self.setText(path_text)

        icon_pixmap = icon_pixmap.scaled(64, 64,
                                         Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation)
        self.setData(icon_pixmap, Qt.ItemDataRole.DecorationRole)
        self.setEditable(False)

    def get_path_str(self):
        return self.path_str