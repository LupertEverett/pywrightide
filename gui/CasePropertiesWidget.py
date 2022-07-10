# Contains properties of the selected case.

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QSpinBox

from data.PyWrightCase import PyWrightCase


class CasePropertiesWidget(QWidget):

    def __init__(self, selected_case: PyWrightCase = PyWrightCase()):
        super().__init__()

        self._selected_case = selected_case

        self.case_name_line_edit = QLineEdit()
        self.case_name_line_edit.setWhatsThis("This will be the name of your case. It will appear in "
                                              "the case selection menu, and it will be the name of the folder "
                                              "that's going to be created.")
        self.case_initial_script_line_edit = QLineEdit()
        self.case_initial_script_line_edit.setWhatsThis("Indicates the name of the script that'll be run "
                                                        "when starting this case from the beginning.")
        self.case_textbox_wrap_checkbox = QCheckBox()
        self.case_textbox_wrap_checkbox.setWhatsThis("Check this to enable auto wrapping of the text in textbox.\n"
                                                     "If unchecked, {n} must be used to switch to new line.")
        self.case_textbox_lines_spinbox = QSpinBox()
        self.case_textbox_lines_spinbox.setWhatsThis("Indicates how many lines of text the textbox will show.\n"
                                                     "Default is 3 lines (or 2 lines for the Japanese version).")
        self.case_textbox_lines_spinbox.setMinimum(2)
        self.case_textbox_lines_spinbox.setMaximum(30)

        self._fill_fields_from_case()

        main_layout = self._prepare_main_layout()
        self.setLayout(main_layout)

    def _prepare_main_layout(self) -> QVBoxLayout:
        result = QVBoxLayout()

        case_name_box = QHBoxLayout()
        case_name_box.addWidget(QLabel("Case Name:"))
        case_name_box.addStretch()
        case_name_box.addWidget(self.case_name_line_edit)

        initial_script_name_box = QHBoxLayout()
        initial_script_name_box.addWidget(QLabel("Initial Script:"))
        initial_script_name_box.addStretch()
        initial_script_name_box.addWidget(self.case_initial_script_line_edit)

        textbox_wrap_box = QHBoxLayout()
        textbox_wrap_box.addWidget(QLabel("Textbox (Auto)Wrap:"))
        textbox_wrap_box.addStretch()
        textbox_wrap_box.addWidget(self.case_textbox_wrap_checkbox)

        textbox_lines_box = QHBoxLayout()
        textbox_lines_box.addWidget(QLabel("Textbox Lines:"))
        textbox_lines_box.addStretch()
        textbox_lines_box.addWidget(self.case_textbox_lines_spinbox)

        result.addLayout(case_name_box)
        result.addLayout(initial_script_name_box)
        result.addLayout(textbox_wrap_box)
        result.addLayout(textbox_lines_box)
        result.setContentsMargins(0, 0, 0, 0)

        return result

    def _fill_fields_from_case(self):
        self.case_name_line_edit.setText(self._selected_case.case_name)
        self.case_initial_script_line_edit.setText(self._selected_case.initial_script_name)
        self.case_textbox_wrap_checkbox.setChecked(self._selected_case.textbox_wrap)
        self.case_textbox_lines_spinbox.setValue(self._selected_case.textbox_lines)

    def check_input_validity(self):
        return self.case_name_line_edit.text() != "" and self.case_initial_script_line_edit.text() != ""

    def get_case_name_field_text(self):
        return self.case_name_line_edit.text()

    def save_fields_to_case(self):
        self._selected_case.case_name = self.case_name_line_edit.text()
        self._selected_case.initial_script_name = self.case_initial_script_line_edit.text()
        self._selected_case.textbox_wrap = self.case_textbox_wrap_checkbox.isChecked()
        self._selected_case.textbox_lines = self.case_textbox_lines_spinbox.value()
