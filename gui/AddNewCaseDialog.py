# Dialog to add a new case to a selected game.

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QMessageBox

from .CasePropertiesWidget import CasePropertiesWidget

from data.PyWrightGame import PyWrightGame
from data.PyWrightCase import PyWrightCase


class AddNewCaseDialog(QDialog):

    def __init__(self, selected_game: PyWrightGame, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add New Case")
        self.setFixedSize(300, 200)

        self._selected_game = selected_game

        self.new_case = PyWrightCase("", "scene1")

        self._case_properties_widget = CasePropertiesWidget(self.new_case)

        self._buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self._buttonBox.accepted.connect(self._handle_accept)
        self._buttonBox.rejected.connect(self.reject)

        main_layout = self._prepare_main_layout()
        self.setLayout(main_layout)

    def _prepare_main_layout(self) -> QVBoxLayout:
        result = QVBoxLayout()

        result.addWidget(self._case_properties_widget)
        result.addStretch()
        result.addWidget(self._buttonBox)

        return result

    def _handle_accept(self):
        if not self._case_properties_widget.check_input_validity():
            QMessageBox.critical(self, "Error", "One or more important fields are empty!")
            return

        # Check if a case with the same name doesn't exist first
        for case in self._selected_game.game_cases:
            if self._case_properties_widget.get_case_name_field_text().lower() == case.lower():
                QMessageBox.critical(self, "Error", "A case with name \"{}\" already exists!".format(case))
                return

        self._case_properties_widget.save_fields_to_case()
        self.accept()
