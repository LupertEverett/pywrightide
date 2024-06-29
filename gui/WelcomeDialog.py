from PyQt6.QtCore import QModelIndex, QSize
from PyQt6.QtWidgets import QLabel, QDialog, QListView, QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox, QFileDialog, \
    QMessageBox
from PyQt6.QtGui import QStandardItem, QStandardItemModel, QIcon, QCloseEvent, QPixmap

from data import IDESettings, IconThemes, PyWrightFolder

from pathlib import Path


_welcome_label_text = """<h1>Welcome to PyWright IDE {}!</h1>
<p>Please select a PyWright folder below to start editing cases!</p>
""".format(IDESettings.IDE_VERSION_STRING)


class WelcomeDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyWright IDE: Welcome!")
        self.setWindowIcon(QIcon("res/icons/ideicon.png"))
        self.setMinimumSize(600, 600)

        self._recent_docs = [path for path in IDESettings.get_recent_docs()
                             if Path(path).exists() and Path(path).is_dir()]

        self._recent_docs_view = QListView()
        self._recent_docs_model = QStandardItemModel(self._recent_docs_view)
        self._recent_docs_view.clicked.connect(self._handle_list_view_clicked)
        self._recent_docs_view.doubleClicked.connect(self._handle_load_selected_clicked)
        self._recent_docs_view.setIconSize(QSize(32, 32))

        self.__selected_folder_path = ""

        pywright_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_FIND_PYWRIGHT)

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
        self._always_autoload_checkbox.setChecked(IDESettings.get_autoload_last_project_check())

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
            if not PyWrightFolder.is_valid_pywright_folder(picker):
                QMessageBox.critical(self, "Error", "Could not find a PyWright installation")
                return

            # Check if the item has already added before
            items = self._recent_docs_model.findItems(picker)
            if len(items) > 0:
                QMessageBox.information(self, "Notice", "Selected folder is already in the list!")
                return

            self.__add_item_to_model(picker, IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_FIND_PYWRIGHT))
            self._recent_docs.append(picker)

    def __add_item_to_model(self, text: str, icon_path: str):
        item = QStandardItem(text)
        item.setIcon(QIcon(icon_path))
        item.setEditable(False)
        self._recent_docs_model.appendRow(item)

    def _handle_load_selected_clicked(self):
        indexes = self._recent_docs_view.selectedIndexes()

        if len(indexes) < 1:
            return

        idx = indexes[0]
        self.__selected_folder_path = self._recent_docs_model.item(idx.row()).text()
        if self._always_autoload_checkbox.isChecked():
            IDESettings.set_autoload_last_project_path(self.__selected_folder_path)
            IDESettings.set_autoload_last_game_name("")  # Should be set after closing the main window instead
            IDESettings.set_autoload_last_project_check(True)
        self.accept()

    def get_selected_folder_path(self) -> str:
        return self.__selected_folder_path

    def closeEvent(self, event: QCloseEvent):
        IDESettings.set_recent_docs(self._recent_docs)
        event.accept()
