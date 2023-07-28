from pathlib import Path

from PyQt5.QtWidgets import QWidget, QDockWidget, QPlainTextEdit, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QIcon, QHideEvent
from PyQt5.QtCore import QProcess

import data.IconThemes as IconThemes

class PyWrightLoggerWidget(QDockWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Logger")
        self.setObjectName("LoggerWidget")

        self.logger_text_edit = QPlainTextEdit()
        self.logger_text_edit.setEnabled(False)

        self.pywright_process = QProcess(None)
        self.pywright_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.pywright_process.started.connect(self._on_process_started)
        self.pywright_process.readyReadStandardOutput.connect(self._log_to_text_edit)
        self.pywright_process.finished.connect(self._on_process_finished)

        self.setWidget(self.logger_text_edit)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)

        hide_icon_path = IconThemes.icon_path_from_theme(IconThemes.ICON_NAME_MINUS)
        self._hide_button = QPushButton(QIcon(hide_icon_path), "")
        self._hide_button.setFlat(True)
        self._hide_button.clicked.connect(self.hide)
        self._hide_button.setFixedWidth(30)

        self.setTitleBarWidget(self._create_title_bar_widget())

        self._program_path = ""
        self._executable_name = ""

    def run_and_log(self, pywright_path: str, executable_name: str):
        self.logger_text_edit.clear()
        final_path = Path("{}/{}".format(pywright_path, executable_name))
        self.pywright_process.setProgram(str(final_path))
        self.pywright_process.setWorkingDirectory(pywright_path)
        self._program_path = pywright_path
        self._executable_name = executable_name
        self.pywright_process.setArguments([])
        self.pywright_process.start()

    def _create_title_bar_widget(self):
        result = QWidget()

        layout = QHBoxLayout()

        layout.addWidget(QLabel("Logger"))
        layout.addStretch()
        layout.addWidget(self._hide_button)
        layout.setContentsMargins(4, 0, 2, 4)

        result.setLayout(layout)
        return result

    def _log_to_text_edit(self):
        output = bytearray(self.pywright_process.readAllStandardOutput())
        self.logger_text_edit.appendPlainText(output.decode("UTF-8").strip())

    def _on_process_started(self):
        full_path = Path("{}/{}".format(self._program_path, self._executable_name))
        self.logger_text_edit.appendPlainText("Running PyWright executable in path {}".format(str(full_path)))

    def _on_process_finished(self, exit_code, exit_status):
        if exit_code == 0:
            self.logger_text_edit.appendPlainText("PyWright exited successfully!")
        else:
            self.logger_text_edit.appendPlainText("PyWright exited with code {} ({})".format(exit_code, exit_status))

    def hideEvent(self, a0: QHideEvent) -> None:
        from .IDEMainWindow import IDEMainWindow
        ide_main_window: IDEMainWindow = self.parent()
        ide_main_window.update_toolbar_toggle_buttons()
