import re

from PyQt6.Qsci import QsciScintilla
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QKeyEvent

from data import EditorThemes, IDESettings
from data.PyWrightScriptLexer import PyWrightScriptLexer


_HIGHLIGHT_INDICATOR_ID = 30
_PARAM_HILIGHT_INDICATOR_ID = 31 # why do we start at 30?


class IDEScintillaWidget(QsciScintilla):
    """Custom Scintilla component with jumping to next parameter with tab support"""

    _highlight_in_progress = False
    """Ensures _highlight_all_occurences() runs only once"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setUtf8(True)

        # Enable word wrapping
        self.setWrapMode(QsciScintilla.WrapMode.WrapWord)

        # First margin is the line number margin by default. We set a preset width value to it here.
        self.setMargins(2)
        self.setMarginType(1, QsciScintilla.MarginType.SymbolMarginColor)
        self.setMarginWidth(0, 50)
        self.setMarginWidth(1, 1)

        self.set_highlight_style(IDESettings.get_highlight_fill_rect())
        self.setIndicatorDrawUnder(True, _HIGHLIGHT_INDICATOR_ID)

        # For parameter autocompletion with tab:
        #self.parameter_amount: int = 0 # Amount of parameters coming from autocompletion DEPRECATED
        self.parameter_position_pairs: list[(int, int)] = []    # empty if no parameters
        self.parameter_line: int = -1
        self.parameter_line_text: str|None = None
        self.indicatorDefine(QsciScintilla.IndicatorStyle.BoxIndicator, _PARAM_HILIGHT_INDICATOR_ID)
        self.textChanged.connect(self.textInserted)

        self._lexer = PyWrightScriptLexer(self)
        self.setup_autocompletion()
        self.setLexer(self._lexer)

    def startParameterInsertion(self, line: int, indices:list[int], parameter_amount: int):
        print("<> startParameterInsertion()")
        pairs = list((i, j+1) for i, j in zip(indices[::2], indices[1::2]))
        if len(indices)%2 == 1:
            pairs += (indices[-1], indices[-1])

        self.parameter_position_pairs = pairs
        self.parameter_line = line
        self.parameter_line_text = self.text(self.positionFromLineIndex(line, 0), self.positionFromLineIndex(line+1, 0))

        # Draw the boxes TODO : Make it better
        for start, end in pairs:
            self.fillIndicatorRange(line, start, line, end, _PARAM_HILIGHT_INDICATOR_ID)
        
        # Select the first occurence
        indexA = indices[0]
        indexB = indices[1] + 1 # +1 because we need the selection to go after the % sign
        self.setSelection(line, indexA, line, indexB)
        #self.parameter_amount = parameter_amount

    def textInserted(self):
        print("<> textInserted()")
        if not len(self.parameter_position_pairs) > 0:
            return

        line, index = self.getCursorPosition()
        # Not on the same line?
        if line != self.parameter_line:
            self.endParameterInsertion()
            return

        new_line_text = self.text(self.positionFromLineIndex(line, 0), self.positionFromLineIndex(line+1, 0))
        delta = len(new_line_text) - len(self.parameter_line_text)
        self.parameter_line_text = new_line_text

        # Update
        for k, (i, j) in enumerate(self.parameter_position_pairs):
            if index < i:
                self.parameter_position_pairs[k] = (i+delta, j+delta)
            elif index <= j:
                if j+delta < 0 or j+delta < i:
                    self.endParameterInsertion()
                    return
                self.parameter_position_pairs[k] = (i, j+delta)
                # Update the box area so that it wraps written text
                self.fillIndicatorRange(line, i, line, j+delta, _PARAM_HILIGHT_INDICATOR_ID)


    def endParameterInsertion(self):
        print("<> endParameterInsertion()")
        self.parameter_line = -1
        self.parameter_position_pairs = []
        self._clear_all_highlights(_PARAM_HILIGHT_INDICATOR_ID)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape and len(self.parameter_position_pairs) > 0:
            self.endParameterInsertion()
            return

        if event.key() in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab) and len(self.parameter_position_pairs) > 0:
            line, index = self.getCursorPosition()
            
            # Not on the same line?
            if line != self.parameter_line:
                self.endParameterInsertion()
                return

            # Find the current box, previous and next:
            previousPair = None
            currentPair = None
            nextPair = None
            nextIsLast = False
            for k, (i, j) in enumerate(self.parameter_position_pairs):
                if currentPair is not None:
                    nextPair = (i, j)
                    if k == len(self.parameter_position_pairs) - 1:
                        nextIsLast = True
                    break
                if i <= index and index <= j:
                    currentPair = (i, j)
            previousPair = self.parameter_position_pairs[k-1] if k > 0 else None

            # Was not in parameter selection box? (ie user moved it before pressing tab again)
            if currentPair is None:
                self.endParameterInsertion()
                return

            goBackward: bool = (event.modifiers() & Qt.KeyboardModifier.ShiftModifier).value != 0
            pairToSelect = previousPair if goBackward else nextPair

            if pairToSelect is None:
                if goBackward:
                    return
                else:
                    self.setCursorPosition(line, currentPair[1])
                    self.endParameterInsertion()
                    return

            # Select the next pair or previous pair
            self.setSelection(line, pairToSelect[0], line, pairToSelect[1])

            # If the next is actually a singular position, and is the last one
            if not goBackward and nextIsLast and nextPair[0] == nextPair[1]:
                self.setCursorPosition(line, nextPair[0])
                self.endParameterInsertion()
                return
        else:
            super().keyPressEvent(event)

    def setup_autocompletion(self):
        # The autocompletion should be used from an API source to have a custom list of proposals
        threshold = IDESettings.get_autocompletion_trigger_threshold() if IDESettings.get_enable_autocompletion_check() else 0
        self.setAutoCompletionThreshold(threshold)
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAPIs)

    def set_highlight_style(self, fill: bool):
        style = QsciScintilla.IndicatorStyle.FullBoxIndicator if fill else QsciScintilla.IndicatorStyle.BoxIndicator
        self.indicatorDefine(style, _HIGHLIGHT_INDICATOR_ID)

    def _handle_move_cursor_request(self, line: int, index: int):
        self.setCursorPosition(line, index)

    def _handle_lexer_selection_request(self, line_begin: int, index_begin: int, line_end: int, index_end: int):
        self.setSelection(line_begin, index_begin, line_end, index_end)

    def supply_builtin_macros_to_lexer(self, builtin_macros: list[str]):
        self._lexer.set_builtin_macros(builtin_macros)

    def supply_game_macros_to_lexer(self, game_macros: list[str]):
        self._lexer.set_game_macros(game_macros)

    def supply_font_properties_to_lexer(self, font_name: str, font_size: int, bold_font: bool):
        self._lexer.set_font_properties(font_name, font_size, bold_font)

    def supply_editor_color_theme_to_lexer(self):
        self._lexer.set_editor_color_theme()
        self.setMarginsBackgroundColor(QColor(EditorThemes.current_editor_theme.editor_margin_color.paper_color))
        self.setMarginsForegroundColor(QColor(EditorThemes.current_editor_theme.editor_margin_color.text_color))
        self.setMarginBackgroundColor(1, QColor(EditorThemes.current_editor_theme.
                                                editor_margin_border_color.paper_color))
        self.setCaretForegroundColor(QColor(EditorThemes.current_editor_theme.caret_color.paper_color))
        self.setIndicatorForegroundColor(QColor(EditorThemes.current_editor_theme.match_highlight_color.paper_color),
                                         _HIGHLIGHT_INDICATOR_ID)
        self.setIndicatorOutlineColor(QColor(EditorThemes.current_editor_theme.match_highlight_color.paper_color),
                                      _HIGHLIGHT_INDICATOR_ID)

    def highlight_all_occurrences(self):
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
        (sel_start_line, sel_start_index, sel_end_line, sel_end_index) = self.getSelection()
        start_pos = self.positionFromLineIndex(sel_start_line, sel_start_index)
        end_pos = self.positionFromLineIndex(sel_end_line, sel_end_index)
        text_to_highlight = self.text(start_pos, end_pos)

        text = self.text()

        # We cannot use findFirst() and findNext() here as they will make the text area jump all over the place
        # All we need here is to only highlight the matching text

        if text_to_highlight != "" and not text_to_highlight.isspace():
            pos = text.find(text_to_highlight, 0)

            while pos != -1:
                (start_line, start_index) = self.lineIndexFromPosition(pos)
                (end_line, end_index) = self.lineIndexFromPosition(pos + len(text_to_highlight))
                # Skip the selected text
                if not (sel_start_line == start_line and sel_start_index == start_index):
                    self.fillIndicatorRange(start_line, start_index, end_line, end_index, _HIGHLIGHT_INDICATOR_ID)
                pos = text.find(text_to_highlight, pos + 1)
        else:
            self._clear_all_highlights()

        self._highlight_in_progress = False

    def _clear_all_highlights(self, id=_HIGHLIGHT_INDICATOR_ID):
        last_line = self.lines() - 1
        last_index = self.lineLength(last_line) - 1
        self.clearIndicatorRange(0, 0, last_line, last_index, id)