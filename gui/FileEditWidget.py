# Widget that deals with a single file
# Used with the tabs

from pathlib import Path

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor

from PyQt5.Qsci import *

import data.EditorThemes as EditorThemes
from data.PyWrightScriptLexer import PyWrightScriptLexer
from .FindReplaceDialog import FindType, ReplaceType, SearchScope


class FileEditWidget(QWidget):

    file_name_changed = pyqtSignal(str)
    file_modified = pyqtSignal()
    # This will signal the IDE on *where* to move
    # For example if FindType is PREVIOUS, this will try to make the IDE switch to a tab that's left to this one.
    move_to_tab_requested = pyqtSignal(str, FindType)
    # This one only goes forwards
    replace_next_in_next_tabs_requested = pyqtSignal(str, str)

    def __init__(self, pywright_dir, selected_file=""):
        super().__init__()

        self.layout = QVBoxLayout()

        self.sci = QsciScintilla()
        self.sci.setUtf8(True)

        # Enable word wrapping
        self.sci.setWrapMode(QsciScintilla.WrapWord)

        # First margin is the line number margin by default. We set a preset width value to it here.
        self.sci.setMargins(2)
        self.sci.setMarginType(1, QsciScintilla.MarginType.SymbolMarginColor)
        self.sci.setMarginWidth(0, 50)
        self.sci.setMarginWidth(1, 1)
        self.sci.modificationChanged.connect(self._emit_file_modified)

        self._lexer = PyWrightScriptLexer(self.sci)
        self.sci.setLexer(self._lexer)

        self.pywright_working_dir = pywright_dir

        self.layout.addWidget(self.sci)

        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)

        self.file_path = selected_file
        self.file_name = "New File"

        self._is_a_new_file = self.file_path == ""

        if not self._is_a_new_file:
            self.file_name = Path(self.file_path).name
            self.fill_the_scintilla(self.file_path)

    def fill_the_scintilla(self, selected_file):
        # The IDE will try to open files assuming UTF-8 encoding, if it fails, it will fall back to ANSI
        # But it will ALWAYS save the files in UTF-8
        # Text encoding detection using libs like chardet may be used if the need arises
        lines = self._try_read_lines(selected_file)
        text = "".join(lines)
        self.sci.setText(text)
        # Common sense: Newly opened files aren't modified.
        self.sci.setModified(False)

    def _try_read_lines(self, selected_file) -> list[str]:
        # newline="" so the IDE does not mess with the EOL chars, fixes the gaps in new lines bug
        f = open(selected_file, "r", newline="", encoding="utf-8")
        try:
            result = f.readlines()
        except UnicodeDecodeError:
            f.close()
            f = open(selected_file, "r", newline="", encoding="ansi")
            result = f.readlines()
        finally:
            f.close()

        return result


    def supply_builtin_macros_to_lexer(self, builtin_macros: list[str]):
        self._lexer.set_builtin_macros(builtin_macros)

    def supply_game_macros_to_lexer(self, game_macros: list[str]):
        self._lexer.set_game_macros(game_macros)

    def supply_font_properties_to_lexer(self, font_name: str, font_size: int, bold_font: bool):
        self._lexer.set_font_properties(font_name, font_size, bold_font)

    def supply_editor_color_theme_to_lexer(self):
        self._lexer.set_editor_color_theme()
        self.sci.setMarginsBackgroundColor(QColor(EditorThemes.current_editor_theme.editor_margin_color.paper_color))
        self.sci.setMarginsForegroundColor(QColor(EditorThemes.current_editor_theme.editor_margin_color.text_color))
        self.sci.setMarginBackgroundColor(1, QColor(EditorThemes.current_editor_theme.
                                                    editor_margin_border_color.paper_color))
        self.sci.setCaretForegroundColor(QColor(EditorThemes.current_editor_theme.caret_color.paper_color))

    def save_to_file(self):
        if not self._is_a_new_file:
            # newline="" so the IDE does not mess with the EOL chars, fixes the gaps in new lines bug
            # The IDE will assume ALL the text files that are opened with it is utf-8 encoded, this should be a safe bet
            # Text encoding detection using libs like chardet may be used if the need arises
            with open(self.file_path, "w", newline="", encoding="utf-8") as f:
                f.write(self.sci.text())
            self.sci.setModified(False)
            return

        # The file name is probably empty. Prompt for a new file to save instead
        save_dialog = QFileDialog.getSaveFileName(self, "Save File",
                                                  str(Path("{}/games".format(self.pywright_working_dir))),
                                                  "Text Files (*.txt)")

        if save_dialog[0] != "":
            with open(save_dialog[0], "w") as f:
                f.write(self.sci.text())
                self._is_a_new_file = False
                self.file_path = save_dialog[0]
                self.sci.setModified(False)
                self.file_name = Path(self.file_path).name
                self.file_name_changed.emit(self.file_name)

    def insert_at_cursor_position(self, text: str):
        [line, index] = self.sci.getCursorPosition()

        if self.sci.lineLength(line) == 0 or index < self.sci.lineLength(line) - 1:
            self.sci.insertAt(text + "\n", line, 0)
        else:
            self.sci.insert("\n" + text)

    def is_file_modified(self) -> bool:
        return self.sci.isModified()

    def _emit_file_modified(self):
        self.sci.setModified(True)
        self.file_modified.emit()

    def search_in_file(self, text_to_find: str, find_type: FindType, search_scope: SearchScope):
        if find_type == FindType.FIND_NEXT:
            self.find_next_in_file(text_to_find, search_scope, from_top=False)
        elif find_type == FindType.FIND_PREVIOUS:
            self.find_previous_in_file(text_to_find, search_scope, from_bottom=False)

    def find_next_in_file(self, text_to_find: str, search_scope: SearchScope, from_top: bool):
        if from_top:
            self.sci.SendScintilla(QsciScintilla.SCI_SETCURRENTPOS, 0, 0)
        cursor_pos = self.sci.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS, 0, 0)
        self.sci.SendScintilla(QsciScintilla.SCI_SETTARGETSTART, cursor_pos, 0)
        self.sci.SendScintilla(QsciScintilla.SCI_SETTARGETEND, len(self.sci.text()), 0)
        pos = self.sci.SendScintilla(QsciScintilla.SCI_SEARCHINTARGET, len(text_to_find), text_to_find.encode("utf-8"))

        if pos == -1 and search_scope == SearchScope.SINGLE_FILE:
            QMessageBox.information(self.parent(), "Find/Replace", "End of file reached")
            return pos
        if pos == -1 and search_scope == SearchScope.OPEN_TABS:
            self.move_to_tab_requested.emit(text_to_find, FindType.FIND_NEXT)
            return pos

        self.sci.SendScintilla(QsciScintilla.SCI_SETSEL, pos, pos + len(text_to_find))
        return pos

    def find_previous_in_file(self, text_to_find: str, search_scope: SearchScope, from_bottom: bool):
        if from_bottom:
            self.sci.SendScintilla(QsciScintilla.SCI_SETANCHOR, len(self.sci.text()), 0)
        cursor_pos = self.sci.SendScintilla(QsciScintilla.SCI_GETANCHOR, 0, 0)
        self.sci.SendScintilla(QsciScintilla.SCI_SETTARGETSTART, cursor_pos, 0)
        self.sci.SendScintilla(QsciScintilla.SCI_SETTARGETEND, 0, 0)  # Position at 0 so Scintilla searches backwards
        pos = self.sci.SendScintilla(QsciScintilla.SCI_SEARCHINTARGET, len(text_to_find), text_to_find.encode("utf-8"))

        if pos == -1 and search_scope == SearchScope.SINGLE_FILE:
            QMessageBox.information(self.parent(), "Find/Replace", "Beginning of file reached")
            return
        if pos == -1 and search_scope == SearchScope.OPEN_TABS:
            self.move_to_tab_requested.emit(text_to_find, FindType.FIND_PREVIOUS)
            return

        self.sci.SendScintilla(QsciScintilla.SCI_SETSEL, pos, pos + len(text_to_find))

    def replace_in_file(self, text_to_find: str, text_to_replace: str, replace_type: ReplaceType, search_scope: SearchScope):
        if replace_type == ReplaceType.REPLACE_NEXT:
            self.replace_next_in_file(text_to_find, text_to_replace, search_scope)
        elif replace_type == ReplaceType.REPLACE_ALL:
            self.replace_all_in_file(text_to_find, text_to_replace)

    def replace_next_in_file(self, text_to_find: str, text_to_replace: str, search_scope: SearchScope):
        find_pos = self.find_next_in_file(text_to_find, SearchScope.SINGLE_FILE, from_top=False)

        if find_pos == -1 and search_scope == SearchScope.OPEN_TABS:
            self.replace_next_in_next_tabs_requested.emit(text_to_find, text_to_replace)
            return

        self.sci.SendScintilla(QsciScintilla.SCI_REPLACESEL, 0, text_to_replace.encode("utf-8"))

        # Select the newly replaced text.
        pos = self.sci.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS, 0, 0)
        self.sci.SendScintilla(QsciScintilla.SCI_SETSEL, pos - len(text_to_replace), pos)

    def replace_all_in_file(self, text_to_find: str, text_to_replace: str):
        pos = self.find_next_in_file(text_to_find, SearchScope.SINGLE_FILE, from_top=True)
        while True:
            if pos == -1:
                return

            self.sci.SendScintilla(QsciScintilla.SCI_REPLACESEL, 0, text_to_replace.encode("utf-8"))
            pos = self.find_next_in_file(text_to_find, SearchScope.SINGLE_FILE, from_top=False)
