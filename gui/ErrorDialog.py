# Error dialog functionality
# Based on: https://timlehr.com/2018/01/python-exception-hooks-with-qt-message-box/index.html

from .IDEMainWindow import IDEMainWindow

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QDialog, QLabel, QPlainTextEdit, QVBoxLayout, QDialogButtonBox, QPushButton, QApplication

import sys
import traceback
import logging

_ERROR_LABEL_TEXT = """PyWright IDE has encountered a fatal error and will be shut down.<br>
Error message and stack trace is available down below:"""

_ide_main_window_ref : IDEMainWindow | None = None

log = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
log.addHandler(handler)


def set_ide_main_window(main_window: IDEMainWindow):
    """Set the main window the Error Dialog will be parented on"""
    global _ide_main_window_ref
    _ide_main_window_ref = main_window

def show_error_dialog(log_msg):
    """Shows the Error Dialog if QApplication is running"""
    if QApplication.instance() is not None:
        errordialog = ErrorDialog(_ide_main_window_ref, log_msg)
        errordialog.exec()
    else:
        log.debug("No QApplication instance available.")

class UncaughtHook(QObject):
    _exception_caught = pyqtSignal(object)

    def __init__(self):
        super().__init__()

        sys.excepthook = self.exception_hook

        self._exception_caught.connect(show_error_dialog)

    def exception_hook(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Ignore KeyboardInterrupt
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        else:
            exc_info = (exc_type, exc_value, exc_traceback)
            log_msg = "\n".join([''.join(traceback.format_tb(exc_traceback)),
                                 "{0}: {1}".format(exc_type.__name__, exc_value)])
            log.critical("Uncaught exception:\n {0}".format(log_msg), exc_info=exc_info)

            self._exception_caught.emit(log_msg)

class ErrorDialog(QDialog):
    """Notifies the user of an error occuring, and allows them to copy the stack trace to clipboard"""

    def __init__(self, parent: IDEMainWindow | None, stacktrace: str = ""):
        super().__init__(parent)

        self.setWindowTitle("PyWright IDE - Fatal Error")

        self._error_title_label = QLabel(self)
        self._error_title_label.setText(_ERROR_LABEL_TEXT)

        self._stack_trace_textedit = QPlainTextEdit(self)
        self._stack_trace_textedit.setPlainText(stacktrace)
        self._stack_trace_textedit.setEnabled(False)

        self._copy_to_clipboard_button = QPushButton("Copy to Clipboard", self)
        self._copy_to_clipboard_button.clicked.connect(self._handle_copy_to_clipboard)

        self._quit_pywright_ide_button = QPushButton("Quit PyWright IDE", self)
        self._quit_pywright_ide_button.clicked.connect(self._handle_quit_ide)

        self._dialog_button_box = QDialogButtonBox()

        self._dialog_button_box.addButton(self._copy_to_clipboard_button, QDialogButtonBox.ButtonRole.NoRole)
        self._dialog_button_box.addButton(self._quit_pywright_ide_button, QDialogButtonBox.ButtonRole.NoRole)

        main_layout = QVBoxLayout()

        main_layout.addWidget(self._error_title_label)
        main_layout.addWidget(self._stack_trace_textedit)
        main_layout.addWidget(self._dialog_button_box)

        self.setLayout(main_layout)

    def _handle_copy_to_clipboard(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self._stack_trace_textedit.toPlainText())

    def _handle_quit_ide(self):
        QApplication.instance().quit()

# Register hook
uncaught_exception_hook = UncaughtHook()