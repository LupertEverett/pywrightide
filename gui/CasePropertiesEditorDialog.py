# Dialog to add a new case to a selected game.

from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QMessageBox

from .CasePropertiesWidget import CasePropertiesWidget

from data.PyWrightGame import PyWrightGame, PyWrightGameInfo
from data.PyWrightCase import PyWrightCase


class CasePropertiesEditorDialog(QDialog):

    def __init__(self, selected_game_info: PyWrightGameInfo, selected_case: PyWrightCase | None, parent=None):
        """Opens up a dialog to edit a case's properties.
        :param selected_game_info: The PyWright game the case is in
        :param selected_case: The case that's going to be edited, or None if it is a new case
        :param parent: Parent Widget of this dialog"""
        super().__init__(parent)

        self.setFixedSize(300, 200)

        self._selected_game_info = selected_game_info

        self._is_a_new_case: bool = selected_case is None

        if self._is_a_new_case:
            self.setWindowTitle("Add New Case")
            self._selected_case = PyWrightCase("", "scene1")
        else:
            self.setWindowTitle("Case Properties: {}".format(selected_case.case_name))
            self._selected_case = selected_case

        self._case_properties_widget = CasePropertiesWidget(self._selected_case)

        self._buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
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

        # If we're creating a new case, check if a case with the same name doesn't exist first
        if self._is_a_new_case:
            for case in self._selected_game_info.game_cases:
                if self._case_properties_widget.get_case_name_field_text().lower() == case.lower():
                    QMessageBox.critical(self, "Error", "A case with name \"{}\" already exists!".format(case))
                    return

        self._case_properties_widget.save_fields_to_case()
        self.accept()

    def get_case(self):
        return self._selected_case
