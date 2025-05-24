# Widget that deals with a single file
# Used with the tabs

from pathlib import Path

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QMessageBox
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor

from PyQt6.Qsci import *

import data.EditorThemes as EditorThemes
from data.PyWrightScriptLexer import PyWrightScriptLexer
from .FindReplaceDialog import FindType, ReplaceType, SearchScope

from data import IDESettings


_HIGHLIGHT_INDICATOR_ID = 30


class FileEditWidget(QWidget):

    file_name_changed = pyqtSignal(str)
    file_modified = pyqtSignal()
    # This will signal the IDE on *where* to move
    # For example if FindType is PREVIOUS, this will try to make the IDE switch to a tab that's left to this one.
    move_to_tab_requested = pyqtSignal(str, FindType)
    # This one only goes forwards
    replace_next_in_next_tabs_requested = pyqtSignal(str, str)

    _highlight_in_progress = False
    """Ensures _highlight_all_occurences() runs only once"""

    def __init__(self, pywright_dir, selected_file=""):
        super().__init__()

        self.layout = QVBoxLayout()

        self.sci = QsciScintilla()
        self.sci.setUtf8(True)

        # Enable word wrapping
        self.sci.setWrapMode(QsciScintilla.WrapMode.WrapWord)

        # First margin is the line number margin by default. We set a preset width value to it here.
        self.sci.setMargins(2)
        self.sci.setMarginType(1, QsciScintilla.MarginType.SymbolMarginColor)
        self.sci.setMarginWidth(0, 50)
        self.sci.setMarginWidth(1, 1)
        self.sci.modificationChanged.connect(self._emit_file_modified)

        self._lexer = PyWrightScriptLexer(self.sci)
        self.setup_autocompletion()
        self.sci.setLexer(self._lexer)

        self.pywright_working_dir = pywright_dir

        self.layout.addWidget(self.sci)

        self.layout.setContentsMargins(0, 0, 0, 0)

        self.set_highlight_style(IDESettings.get_highlight_fill_rect())
        self.sci.setIndicatorDrawUnder(True, _HIGHLIGHT_INDICATOR_ID)

        self.sci.selectionChanged.connect(self._highlight_all_occurrences)

        self.setLayout(self.layout)

        self.file_path = selected_file
        self.file_name = "New File"

        self._is_a_new_file = self.file_path == ""

        if not self._is_a_new_file:
            self.file_name = Path(self.file_path).name
            self.fill_the_scintilla(self.file_path)

    def setup_autocompletion(self):
        # The autocompletion should be used from an API source to have a custom list of proposals
        threshold = IDESettings.get_autocompletion_trigger_threshold() if IDESettings.get_enable_autocompletion_check() else 0
        self.sci.setAutoCompletionThreshold(threshold)
        self.sci.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAPIs)

    def fill_the_scintilla(self, selected_file):
        """Fills the text area with the contents loaded from the selected file.
            :param selected_file: Path to the file to read the contents of
            :return: None"""
        # The IDE will try to open files assuming UTF-8 encoding, if it fails, it will fall back to ANSI
        # But it will ALWAYS save the files in UTF-8
        # Text encoding detection using libs like chardet may be used if the need arises
        lines = self._try_read_lines(selected_file)
        text = "".join(lines)
        self.sci.setText(text)
        # Common sense: Newly opened files aren't modified.
        self.sci.setModified(False)
        # Set the cursor at the beginning of file so that searching works without the user having to place it first
        self.sci.setCursorPosition(0, 0)

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
        self.sci.setIndicatorForegroundColor(QColor(EditorThemes.current_editor_theme.match_highlight_color.paper_color),
                                            _HIGHLIGHT_INDICATOR_ID)
        self.sci.setIndicatorOutlineColor(QColor(EditorThemes.current_editor_theme.match_highlight_color.paper_color),
                                          _HIGHLIGHT_INDICATOR_ID)

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

    def set_highlight_style(self, fill: bool):
        style = QsciScintilla.IndicatorStyle.FullBoxIndicator if fill else QsciScintilla.IndicatorStyle.BoxIndicator
        self.sci.indicatorDefine(style, _HIGHLIGHT_INDICATOR_ID)

    def _highlight_all_occurrences(self):
        """Highlights all occurrences of the selected text.
        :return: None"""
        # Don't highlight anything if the setting is not enabled.
        if not IDESettings.get_highlight_matching_text():
            self._clear_all_highlights()
            return

        if self._highlight_in_progress:
            return

        self._highlight_in_progress = True

        # Clear previous highlights (if there's any)
        self._clear_all_highlights()

        # Obtain the text from selection
        (sel_start_line, sel_start_index, sel_end_line, sel_end_index) = self.sci.getSelection()
        start_pos = self.sci.positionFromLineIndex(sel_start_line, sel_start_index)
        end_pos = self.sci.positionFromLineIndex(sel_end_line, sel_end_index)
        text_to_highlight = self.sci.text(start_pos, end_pos)

        text = self.sci.text()

        # We cannot use findFirst() and findNext() here as they will make the text area jump all over the place
        # All we need here is to only highlight the matching text

        if text_to_highlight != "" and not text_to_highlight.isspace():
            pos = text.find(text_to_highlight, 0)

            while pos != -1:
                (start_line, start_index) = self.sci.lineIndexFromPosition(pos)
                (end_line, end_index) = self.sci.lineIndexFromPosition(pos + len(text_to_highlight))
                # Skip the selected text
                if not (sel_start_line == start_line and sel_start_index == start_index):
                    self.sci.fillIndicatorRange(start_line, start_index, end_line, end_index, _HIGHLIGHT_INDICATOR_ID)
                pos = text.find(text_to_highlight, pos + 1)
        else:
            self._clear_all_highlights()

        self._highlight_in_progress = False

    def _clear_all_highlights(self):
        last_line = self.sci.lines() - 1
        last_index = self.sci.lineLength(last_line) - 1
        self.sci.clearIndicatorRange(0, 0, last_line, last_index, _HIGHLIGHT_INDICATOR_ID)
