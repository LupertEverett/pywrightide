# Widget that deals with a single file
# Used with the tabs

from pathlib import Path

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog
from PyQt5.QtCore import pyqtSignal

from PyQt5.Qsci import *

from data.PyWrightScriptLexer import PyWrightScriptLexer


class FileEditWidget(QWidget):

    file_name_changed = pyqtSignal(str)
    file_modified = pyqtSignal()

    def __init__(self, pywright_dir, selected_file=""):
        super().__init__()

        self.layout = QVBoxLayout()

        self.sci = QsciScintilla()
        self.sci.setUtf8(True)

        # Enable word wrapping
        self.sci.setWrapMode(QsciScintilla.WrapWord)

        # Sets the amount of custom margins, first one being the line counter
        # and the second one *should* be the folding one.
        self.sci.setMargins(2)
        self.sci.setMarginType(1, QsciScintilla.TextMargin)
        # First margin is the line number margin. We set a preset width value to it here.
        self.sci.setMarginWidth(0, 40)
        self.sci.modificationChanged.connect(self._emit_file_modified)

        self._lexer = PyWrightScriptLexer(self.sci)
        self.sci.setLexer(self._lexer)

        self.pywright_working_dir = pywright_dir

        self.layout.addWidget(self.sci)

        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)

        self.file_path = selected_file
        self.file_name = ""

        self._is_a_new_file = self.file_path == ""

        if not self._is_a_new_file:
            self.file_name = Path(self.file_path).name
            self.fill_the_scintilla(self.file_path)

    def fill_the_scintilla(self, selected_file):
        with open(selected_file, "r") as f:
            lines = f.readlines()
            text = "".join(lines)
            self.sci.setText(text)
            # Common sense: Newly opened files aren't modified.
            self.sci.setModified(False)

    def save_to_file(self):
        if not self._is_a_new_file:
            with open(self.file_path, "w") as f:
                f.write(self.sci.text())
            self.sci.setModified(False)
            return

        # The file name is probably empty. Prompt for a new file to save instead
        save_dialog = QFileDialog.getSaveFileName(self, "Save File",
                                                  str(Path("{}/games".format(self.pywright_working_dir))),
                                                  "Text Files (*.txt)")

        if save_dialog != "":
            with open(save_dialog[0], "w") as f:
                f.write(self.sci.text())
                self._is_a_new_file = False
                self.file_path = save_dialog[0]
                self.sci.setModified(False)
                self.file_name = Path(self.file_path).name
                self.file_name_changed.emit(self.file_name)

    def is_file_modified(self) -> bool:
        return self.sci.isModified()

    def _emit_file_modified(self):
        self.sci.setModified(True)
        self.file_modified.emit()
