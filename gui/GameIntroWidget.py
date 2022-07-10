# Handles the data in intro.txt of the selected PyWright game

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QToolBar, QAction
from PyQt5.QtGui import QIcon

from .AddNewCaseDialog import AddNewCaseDialog

from data.PyWrightGame import PyWrightGame


class GameIntroWidget(QWidget):

    def __init__(self):
        super().__init__()

        self._selected_game = PyWrightGame()

        self._game_cases_list_widget = QListWidget()
        self._game_cases_list_widget.clicked.connect(self._handle_list_widget_clicked)

        # TODO: Add buttons to add/remove cases
        # Buttons

        self._widget_toolbar = QToolBar()

        self.add_new_case_action = QAction(QIcon("res/icons/plus.png"),"New Case", self._widget_toolbar)
        self.add_new_case_action.triggered.connect(self._handle_add_new_case)
        self.add_existing_case_action = QAction(QIcon("res/icons/doubleplus.png"),
                                                "Add Existing Case", self._widget_toolbar)
        self.remove_case_action = QAction(QIcon("res/icons/minus.png"), "Remove Case", self._widget_toolbar)
        self.case_properties_action = QAction(QIcon("res/icons/gameproperties.png"),
                                              "Case Properties", self._widget_toolbar)

        # Main Layout
        main_layout = self._prepare_main_layout()
        self.setLayout(main_layout)

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
            self._selected_game.load_intro_txt()
            self._populate_cases_list()

    def save_intro_txt(self):
        if self._selected_game.is_a_game_selected():
            self._selected_game.write_intro_txt()

    def _populate_cases_list(self):
        self._game_cases_list_widget.clear()
        for game_case in self._selected_game.game_cases:
            self._game_cases_list_widget.addItem(game_case)

    def _handle_list_widget_clicked(self):
        selection = self._game_cases_list_widget.currentItem()
        self.remove_case_action.setEnabled(selection is not None)

    def _handle_add_new_case(self):
        add_new_case_dialog = AddNewCaseDialog(self._selected_game, self)

        if add_new_case_dialog.exec_():
            self._selected_game.create_new_case(add_new_case_dialog.new_case)
            self._populate_cases_list()
