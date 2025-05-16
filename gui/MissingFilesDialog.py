from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QWidget, QDialogButtonBox, QListWidget, QVBoxLayout, QLabel, QStyle, QHBoxLayout

MISSING_FILES_TEXT = """PyWright IDE has detected that these file(s) below went missing (either moved or deleted) since the IDE last closed.<br>
Because of that the IDE couldn't restore some of the tabs.
"""


class MissingFilesDialog(QDialog):
    def __init__(self, parent: QWidget, files_list: list[str]):
        """Displays a dialog box with a list of files that went missing.
            :param parent: The parent widget.
            :param files_list: List of files that went missing.
        """
        super().__init__(parent)
        self.files_list = files_list

        self.setWindowTitle("Notice: Missing Files")

        # Obtain the information icon
        info_icon_pixmap = QStyle.StandardPixmap.SP_MessageBoxInformation
        info_icon = self.style().standardIcon(info_icon_pixmap)

        # Assign the icon to a label
        info_icon_label = QLabel(self)
        info_icon_label.setPixmap(info_icon.pixmap(info_icon.actualSize(QSize(48, 48))))

        self._text_label = QLabel(MISSING_FILES_TEXT, self)

        info_label_layout = QHBoxLayout()
        info_label_layout.addWidget(info_icon_label)
        info_label_layout.addWidget(self._text_label)

        self._missing_files_list_widget = QListWidget(self)
        self._missing_files_list_widget.addItems(self.files_list)

        self._dialog_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self._dialog_box.accepted.connect(self.accept)

        main_layout = QVBoxLayout()

        main_layout.addLayout(info_label_layout)
        main_layout.addWidget(self._missing_files_list_widget)
        main_layout.addWidget(self._dialog_box)

        self.setLayout(main_layout)