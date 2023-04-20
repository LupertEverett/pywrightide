# A find/replace dialog
# Can search and replace within the single file/all open tabs/entire project

from enum import Enum

from PyQt5.QtWidgets import (QDialog, QPushButton, QRadioButton,
                             QButtonGroup, QGroupBox, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QLabel, QMessageBox)
from PyQt5.QtCore import pyqtSignal


class SearchScope(Enum):
    SINGLE_FILE = 0
    OPEN_TABS = 1
    # ENTIRE_PROJECT = 2


class FindType(Enum):
    FIND_PREVIOUS = 0
    FIND_NEXT = 1
    FIND_ALL = 2


class ReplaceType(Enum):
    REPLACE_NEXT = 0
    REPLACE_ALL = 1


class FindReplaceDialog(QDialog):

    find_requested = pyqtSignal(str, FindType, SearchScope)
    replace_requested = pyqtSignal(str, str, ReplaceType, SearchScope)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Find/Replace")

        self._find_line_edit = QLineEdit()
        self._find_line_edit.setMaximumWidth(500)
        self._replace_line_edit = QLineEdit()
        self._replace_line_edit.setMaximumWidth(500)

        self._find_previous_button = QPushButton("Find Previous")
        self._find_previous_button.pressed.connect(self._handle_find_previous)
        self._find_next_button = QPushButton("Find Next")
        self._find_next_button.pressed.connect(self._handle_find_next)
        self._find_all_button = QPushButton("Find All")

        self._replace_next_button = QPushButton("Replace Next")
        self._replace_next_button.pressed.connect(self._handle_replace_next)
        self._replace_all_button = QPushButton("Replace All")

        self._close_button = QPushButton("Close")
        self._close_button.pressed.connect(self.close)

        self.search_scope: SearchScope = SearchScope.SINGLE_FILE

        self._scope_single_file_radio_button = QRadioButton("Single File")
        self._scope_single_file_radio_button.setChecked(self.search_scope == SearchScope.SINGLE_FILE)
        self._scope_single_file_radio_button.clicked.connect(self._handle_radio_buttons)
        self._scope_open_tabs_radio_button = QRadioButton("Open Tabs")
        self._scope_open_tabs_radio_button.setChecked(self.search_scope == SearchScope.OPEN_TABS)
        self._scope_open_tabs_radio_button.clicked.connect(self._handle_radio_buttons)
        # self._scope_entire_project_radio_button = QRadioButton("Entire Project")
        # self._scope_entire_project_radio_button.setChecked(self.search_scope == SearchScope.ENTIRE_PROJECT)
        # self._scope_entire_project_radio_button.clicked.connect(self._handle_radio_buttons)

        self._scope_group_box = QGroupBox("Search Scope")
        self._scope_group_box_layout = QVBoxLayout()

        self._scope_radio_buttons_group = QButtonGroup()
        self._scope_radio_buttons_group.addButton(self._scope_single_file_radio_button)
        self._scope_radio_buttons_group.addButton(self._scope_open_tabs_radio_button)
        # self._scope_radio_buttons_group.addButton(self._scope_entire_project_radio_button)

        self._scope_group_box_layout.addWidget(self._scope_single_file_radio_button)
        self._scope_group_box_layout.addWidget(self._scope_open_tabs_radio_button)
        # self._scope_group_box_layout.addWidget(self._scope_entire_project_radio_button)
        self._scope_group_box.setLayout(self._scope_group_box_layout)

        find_row_layout = QHBoxLayout()
        find_row_layout.addWidget(QLabel("Find:"))
        find_row_layout.addWidget(self._find_line_edit)

        replace_row_layout = QHBoxLayout()
        replace_row_layout.addWidget(QLabel("Replace:"))
        replace_row_layout.addWidget(self._replace_line_edit)

        bottom_buttons_layout = QHBoxLayout()

        bottom_buttons_layout.addWidget(self._find_previous_button)
        bottom_buttons_layout.addWidget(self._find_next_button)
        bottom_buttons_layout.addWidget(self._find_all_button)
        bottom_buttons_layout.addWidget(self._replace_next_button)
        bottom_buttons_layout.addWidget(self._replace_all_button)
        bottom_buttons_layout.addWidget(self._close_button)

        main_layout = QVBoxLayout()

        main_layout.addLayout(find_row_layout)
        main_layout.addLayout(replace_row_layout)
        main_layout.addWidget(self._scope_group_box)
        main_layout.addLayout(bottom_buttons_layout)

        self.setLayout(main_layout)

    def _handle_radio_buttons(self):
        if self._scope_single_file_radio_button.isChecked():
            self.search_scope = SearchScope.SINGLE_FILE
        elif self._scope_open_tabs_radio_button.isChecked():
            self.search_scope = SearchScope.OPEN_TABS
        # elif self._scope_entire_project_radio_button.isChecked():
        #     self.search_scope = SearchScope.ENTIRE_PROJECT

    def _handle_find_previous(self):
        find_text = self._find_line_edit.text()
        if find_text != "":
            self.find_requested.emit(find_text, FindType.FIND_PREVIOUS, self.search_scope)

    def _handle_find_next(self):
        find_text = self._find_line_edit.text()
        if find_text != "":
            self.find_requested.emit(find_text, FindType.FIND_NEXT, self.search_scope)

    def _handle_replace_next(self):
        find_text = self._find_line_edit.text()
        replace_text = self._replace_line_edit.text()

        if find_text.isspace() or find_text == "":
            QMessageBox.critical(self, "Error", "Find text cannot be empty!")
            return

        if replace_text.isspace() or replace_text == "":
            QMessageBox.critical(self, "Error", "Replace text cannot be empty!")
            return

        self.replace_requested.emit(find_text, replace_text, ReplaceType.REPLACE_NEXT, self.search_scope)
