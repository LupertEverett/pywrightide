# Handles the data in intro.txt of the selected PyWright game

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QToolBar, QAction, QMessageBox
from PyQt5.QtGui import QIcon

from .AddNewCaseDialog import AddNewCaseDialog
from .AddExistingCaseDialog import AddExistingCaseDialog

from data.PyWrightGame import PyWrightGame
from data.PyWrightCase import PyWrightCase

import data.IconThemes as IconThemes


class GameIntroWidget(QWidget):

    def __init__(self):
        super().__init__()

        self._selected_game = PyWrightGame()

        self._game_cases_list_widget = QListWidget()
        self._game_cases_list_widget.clicked.connect(self._handle_list_widget_clicked)

        # Buttons

        self._widget_toolbar = QToolBar()

        add_new_case_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_PLUS)
        add_existing_case_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_DOUBLE_PLUS)
        remove_case_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_MINUS)
        case_properties_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_SETTINGS)
        self.add_new_case_action = QAction(QIcon(add_new_case_icon_path),"New Case", self._widget_toolbar)
        self.add_new_case_action.triggered.connect(self._handle_add_new_case)
        self.add_existing_case_action = QAction(QIcon(add_existing_case_icon_path),
                                                "Add Existing Case", self._widget_toolbar)
        self.add_existing_case_action.triggered.connect(self._handle_add_existing_case)
        self.remove_case_action = QAction(QIcon(remove_case_icon_path), "Remove Case", self._widget_toolbar)
        self.remove_case_action.triggered.connect(self._handle_remove_case)
        self.case_properties_action = QAction(QIcon(case_properties_icon_path),
                                              "Case Properties", self._widget_toolbar)
        self.case_properties_action.triggered.connect(self._handle_case_properties)

        # Main Layout
        main_layout = self._prepare_main_layout()
        self.setLayout(main_layout)

        self._update_widget_toolbar_buttons()

    def _prepare_main_layout(self) -> QVBoxLayout:
        result = QVBoxLayout()

        self._widget_toolbar.addAction(self.add_new_case_action)
        self._widget_toolbar.addAction(self.add_existing_case_action)
        self._widget_toolbar.addSeparator()
        self._widget_toolbar.addAction(self.remove_case_action)
        self._widget_toolbar.addSeparator()
        self._widget_toolbar.addAction(self.case_properties_action)

        result.addWidget(self._widget_toolbar)
        result.addWidget(self._game_cases_list_widget)

        result.setContentsMargins(0, 0, 0, 0)

        return result

    def load_intro_txt(self, selected_game: PyWrightGame):
        self._selected_game = selected_game
        if selected_game.is_a_game_selected():
            self._populate_cases_list()

    def save_intro_txt(self):
        if self._selected_game.is_a_game_selected():
            self._selected_game.write_intro_txt()

    def _populate_cases_list(self):
        self._game_cases_list_widget.clear()
        for game_case in self._selected_game.game_cases:
            self._game_cases_list_widget.addItem(game_case)

    def _handle_list_widget_clicked(self):
        # selection = self._game_cases_list_widget.currentItem()
        # self.remove_case_action.setEnabled(selection is not None)
        self._update_widget_toolbar_buttons()

    def _handle_add_new_case(self):
        add_new_case_dialog = AddNewCaseDialog(self._selected_game, None, self)

        if add_new_case_dialog.exec_():
            self._selected_game.create_new_case(add_new_case_dialog.get_case())
            self._populate_cases_list()

    def _handle_add_existing_case(self):
        add_existing_case_dialog = AddExistingCaseDialog(self._selected_game, self)
        if add_existing_case_dialog.exec_():
            self._populate_cases_list()

    def _handle_remove_case(self):
        if QMessageBox.question(self, "Are you sure?", "Are you sure you want to remove this case?",
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.No:
            return

        also_remove_folder = QMessageBox.question(self, "Also remove the folder?",
                                                  "Would you like to remove the folder as well?",
                                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        selected_case: str = self._game_cases_list_widget.currentItem().text()
        self._selected_game.remove_case(selected_case, also_remove_folder == QMessageBox.Yes)
        self._populate_cases_list()

    def _handle_case_properties(self):
        selected_case_name = self._game_cases_list_widget.selectedItems()[0].text()
        selected_case_path = self._selected_game.game_path/selected_case_name
        selected_case = PyWrightCase.from_existing_case_folder(selected_case_path)

        case_properties_dialog = AddNewCaseDialog(self._selected_game, selected_case, self)

        if case_properties_dialog.exec_():
            selected_case.update_case_intro_txt(selected_case_path)
            self._populate_cases_list()

    def _update_widget_toolbar_buttons(self):
        selected_items = self._game_cases_list_widget.selectedItems()
        self.remove_case_action.setEnabled(len(selected_items) > 0)
        self.case_properties_action.setEnabled(len(selected_items) > 0)
