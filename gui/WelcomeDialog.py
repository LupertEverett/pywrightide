from PyQt6.QtCore import QModelIndex, QSize, Qt, QRect, QRectF
from PyQt6.QtWidgets import QLabel, QDialog, QListView, QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox, QFileDialog, \
    QMessageBox, QStyledItemDelegate, QStyleOption, QStyle, QStyleOptionViewItem, QApplication
from PyQt6.QtGui import QStandardItem, QStandardItemModel, QIcon, QCloseEvent, QPixmap, QTextDocument, \
    QAbstractTextDocumentLayout, QPalette, QImage, QImageReader

from .OpenGameDialog import OpenGameDialog

from data import IDESettings, IconThemes, PyWrightFolder

from data.PyWrightGame import PyWrightGameInfo
from data.PyWrightGamePathItem import PyWrightGamePathItem

from pathlib import Path


_welcome_label_text = """<h1>Welcome to PyWright IDE {}!</h1>
<p>Please select a PyWright game folder below to start editing cases!</p>
""".format(IDESettings.IDE_VERSION_STRING)

_folder_does_not_exist_notice_text = """<p><b>Notice:</b> Last open game ({})'s folder has been either moved or deleted.</p>
<p>Please select a different folder from below.</p>
""".format(Path(IDESettings.get_autoload_last_game_path()).stem)


class WelcomeDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyWright IDE: Welcome!")
        self.setWindowIcon(QIcon("res/icons/ideicon.png"))
        self.setMinimumSize(600, 600)

        self._recent_docs = [path for path in IDESettings.get_recent_games()
                             if Path(path).exists() and Path(path).is_dir()]

        self._recent_docs_view = QListView()

        self._recent_docs_view.setItemDelegate(RichTextDelegate(self))

        self._recent_docs_model = QStandardItemModel(self._recent_docs_view)
        self._recent_docs_view.clicked.connect(self._handle_list_view_clicked)
        self._recent_docs_view.doubleClicked.connect(self._handle_load_selected_clicked)
        self._recent_docs_view.setIconSize(QSize(32, 32))

        self.__selected_folder_path = ""

        pywright_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_PYWRIGHT)

        last_game_path = Path(IDESettings.get_autoload_last_game_path())
        last_game_exists = last_game_path.exists() and last_game_path.is_dir()

        for doc_path in self._recent_docs:
            self.__add_item_to_model(doc_path, pywright_icon_path)

        self._recent_docs_view.setModel(self._recent_docs_model)

        ide_icon_label = QLabel("")
        icon_pixmap = QPixmap("res/icons/ideicon.png")
        ide_icon_label.setPixmap(icon_pixmap)
        label_size = QSize(icon_pixmap.width() + 2, icon_pixmap.height() + 2)
        ide_icon_label.setFixedSize(label_size)
        welcome_label = QLabel(_welcome_label_text)

        # Buttons
        self.load_selected_button = QPushButton("Load selected folder")
        self.load_selected_button.setEnabled(False)
        self.load_selected_button.clicked.connect(self._handle_load_selected_clicked)

        self.add_folder_button = QPushButton("Add folder")
        self.add_folder_button.clicked.connect(self._handle_add_folder_clicked)

        self._always_autoload_checkbox = QCheckBox("Always load the selected folder at startup (skips this dialog)")
        self._always_autoload_checkbox.setChecked(IDESettings.get_autoload_last_game_check())

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_folder_button)
        button_layout.addStretch()
        button_layout.addWidget(self.load_selected_button)

        welcome_label_layout = QHBoxLayout()

        welcome_label_layout.addWidget(ide_icon_label)
        welcome_label_layout.addWidget(welcome_label)

        main_layout = QVBoxLayout()

        main_layout.addLayout(welcome_label_layout)
        if not last_game_exists:
            main_layout.addWidget(QLabel(_folder_does_not_exist_notice_text))
        main_layout.addWidget(self._recent_docs_view)
        main_layout.addWidget(self._always_autoload_checkbox)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def _handle_list_view_clicked(self, index: QModelIndex):
        sel_row = index.row()

        self.load_selected_button.setEnabled(sel_row >= 0)

    def _handle_add_folder_clicked(self):
        picker = QFileDialog.getExistingDirectory()

        if picker != "":
            picker = Path(picker)  # Correct the folder separators

            if PyWrightGameInfo.is_valid_game_folder(Path(picker)):
                # Check if the item has already added before
                items = self._recent_docs_model.findItems(str(picker))
                if len(items) > 0:
                    QMessageBox.information(self, "Notice", "Selected folder is already in the list!")
                    return

                self.__add_item_to_model(str(picker),
                                         IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_PYWRIGHT))
                self._recent_docs.append(str(picker))
            elif PyWrightFolder.is_valid_pywright_folder(str(picker)):
                open_game_dialog = OpenGameDialog(str(picker), self)

                if open_game_dialog.exec():
                    final_path = picker / "games" / open_game_dialog.selected_game

                    # Check if the item has already added before
                    items = self._recent_docs_model.findItems(str(final_path))
                    if len(items) > 0:
                        QMessageBox.information(self, "Notice", "Selected folder is already in the list!")
                        return

                    self.__add_item_to_model(str(final_path),
                                             IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_PYWRIGHT))
                    self._recent_docs.append(str(final_path))
            else:
                QMessageBox.critical(self, "Error", "Could not find a PyWright game!")

    def __add_item_to_model(self, text: str, icon_path: str):
        item = PyWrightGamePathItem(text)
        self._recent_docs_model.appendRow(item)

    def _handle_load_selected_clicked(self):
        indexes = self._recent_docs_view.selectedIndexes()

        if len(indexes) < 1:
            return

        idx = indexes[0]
        self.__selected_folder_path = self._recent_docs_model.item(idx.row()).get_path_str()
        if self._always_autoload_checkbox.isChecked():
            IDESettings.set_autoload_last_game_path(self.__selected_folder_path)
            IDESettings.set_autoload_last_game_check(True)

        IDESettings.set_recent_games(self._recent_docs)
        self.accept()

    def get_selected_folder_path(self) -> str:
        return self.__selected_folder_path

    def closeEvent(self, event: QCloseEvent):
        IDESettings.set_recent_games(self._recent_docs)
        event.accept()


"""A custom delegate to make HTML tags work in QStandardItems' text contents"""
class RichTextDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)
        self.doc = QTextDocument()

    def paint(self, painter, option, index):
        self.initStyleOption(option, index)
        painter.save()
        self.doc.setTextWidth(option.rect.width())
        self.doc.setHtml(option.text)
        self.doc.setDefaultFont(option.font)
        option.text = ''
        option.widget.style().drawControl(QStyle.ControlElement.CE_ItemViewItem, option, painter)

        iconSize = option.icon.actualSize(option.rect.size())

        painter.translate(option.rect.left() + iconSize.width() + 4, option.rect.top())
        clip = QRectF(0, 0, option.rect.width() + iconSize.width() + 4, option.rect.height())
        painter.setClipRect(clip)
        ctx = QAbstractTextDocumentLayout.PaintContext()
        ctx.clip = clip
        self.doc.documentLayout().draw(painter, ctx)
        painter.restore()

    def sizeHint(self, option, index):
        self.initStyleOption(option, index)

        doc = QTextDocument()
        doc.setHtml(option.text)
        doc.setTextWidth(option.rect.width())

        icon_size = option.icon.actualSize(option.rect.size())
        # Use icon height instead to be more consistent
        return QSize(int(doc.idealWidth()), icon_size.height() + 4)