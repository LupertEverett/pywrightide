"""Just a status bar with a custom separator"""

from PyQt6.QtWidgets import QStatusBar, QLabel, QFrame


class MainWindowStatusBar(QStatusBar):

    def __init__(self, parent=None):
        super(MainWindowStatusBar, self).__init__(parent)

        self.setSizeGripEnabled(False)

        self._selection_length_info_label = QLabel()
        self._line_col_info_label = QLabel()
        self._installation_path_label = QLabel("No PyWright folder selected")

        self._selection_length_info_label.setContentsMargins(4, 0, 4, 0)
        self._line_col_info_label.setContentsMargins(4, 0, 4, 0)
        self._installation_path_label.setContentsMargins(4, 0, 4, 0)

        self.addPermanentWidget(self._selection_length_info_label)
        self.addPermanentWidget(self._line_col_info_label)
        self.addPermanentWidget(self._installation_path_label)

        self.setContentsMargins(4, 2, 4, 2)

    def set_selection_length_info(self, selection_length: int):
        if selection_length > 0:
            self._selection_length_info_label.setText("{} characters selected".format(selection_length))
        else:
            self._selection_length_info_label.setText("")

    def set_installation_path_info(self, installation_path: str):
        self._installation_path_label.setText(installation_path)

    def set_cursor_position_info(self, line: int, col: int):
        """Displays cursor position in a line/column manner.
        Will show nothing when either line or col is non-positive.
        :param line: Line number
        :param col: Column number"""
        if line > 0 and col > 0:
            self._line_col_info_label.setText("Ln: {}, Col: {}".format(line, col))
        else:
            self._line_col_info_label.setText("")
