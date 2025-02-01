from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem, QPixmap

from pathlib import Path

from data import IconThemes

class PyWrightGamePathItem(QStandardItem):

    def __init__(self, path_str: str):
        super().__init__()

        self.path_str = path_str
        self.parent_path = Path(self.path_str).parent
        self.game_name = Path(self.path_str).stem

        path_text = "<h2>{}</h2><p>{}</p>".format(self.game_name, self.parent_path)
        self.setText(path_text)
        icon_pixmap = QPixmap(IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_PYWRIGHT))
        icon_pixmap = icon_pixmap.scaled(64, 64,
                                         Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation)
        self.setData(icon_pixmap, Qt.ItemDataRole.DecorationRole)
        self.setEditable(False)

    def get_path_str(self):
        return self.path_str