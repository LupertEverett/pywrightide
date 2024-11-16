from PyQt6.QtCore import QSize, QT_VERSION_STR, PYQT_VERSION_STR
from PyQt6.Qsci import QSCINTILLA_VERSION_STR
from pygame import ver as pygame_ver

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QDialog, QDialogButtonBox, QVBoxLayout, QLayout, QLabel, QTabWidget, \
    QHBoxLayout, QTextEdit


from data import IDESettings


_version_info_text = ("""<h1>PyWright IDE</h1><h2>Version {} ({})</h2>"""
                      .format(IDESettings.IDE_VERSION_STRING, IDESettings.IDE_BUILD_STRING))

_about_text = """<p>This program aims to make developing PyWright games easier.</p>
<h3>Libraries Used:</h3>
<p><b>Qt:</b> {}</p>
<p><b>PyQt:</b> {}</p>
<p><b>QScintilla:</b> {}</p>
<p><b>PyGame:</b> {}</p>
""".format(QT_VERSION_STR, PYQT_VERSION_STR, QSCINTILLA_VERSION_STR, pygame_ver)

_links_text = """<h3><a href="https://github.com/LupertEverett/pywrightide/">Project Homepage</a> 
| <a href="https://forums.court-records.net/viewtopic.php?f=36&t=33857">Court Records Forums Thread</a></h3>
"""

_credits_text = """<h2>Thanks to:</h2>
<p>Zetrypio: Basic autocompletion support.</p>
<p>in1tiate: Script Lexer improvements.</p>
<p>Everyone on the <a href="https://forums.court-records.net/viewtopic.php?f=36&t=33857">Court Records forums thread</a> who provided their feedback!</p>
<h2>Special Thanks:</h2>
<ul>
<li>CAPCOM for the Ace Attorney franchise, which inspired PyWright.</li>
<li>Saluk for creating <a href="https://pywright.dawnsoft.org/">PyWright</a> itself.</li>
<li>BirbIsTheWord, for being the inspiration behind PyWright IDE, not to mention the countless amounts of testing and feedback.</li>
</ul>
"""


def about_pywright_ide(parent: QWidget):
    about_dialog = AboutDialog(parent)
    about_dialog.exec()


class AboutDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("About PyWright IDE")

        self._ide_icon = QPixmap("res/icons/ideicon.png")
        self._ide_icon_label = QLabel(self)
        self._ide_icon_label.setPixmap(self._ide_icon)
        ide_icon_width = self._ide_icon.width() + 2
        ide_icon_height = self._ide_icon.height() + 2
        self._ide_icon_label.setFixedSize(QSize(ide_icon_width, ide_icon_height))

        self._version_info_label = QLabel(self)
        self._version_info_label.setText(_version_info_text)

        top_level_layout = QHBoxLayout()

        top_level_layout.addWidget(self._ide_icon_label)
        top_level_layout.addWidget(self._version_info_label)

        self._about_label = QLabel(self)
        self._about_label.setText(_about_text)

        self._links_label = QLabel(self)
        self._links_label.setText(_links_text)
        self._links_label.setOpenExternalLinks(True)

        self._credits_label = QLabel(self)
        self._credits_label.setText(_credits_text)

        self._about_page_widget = QWidget(self)

        about_page_layout = QVBoxLayout()

        about_page_layout.addWidget(self._about_label)
        about_page_layout.addStretch()
        about_page_layout.addWidget(self._links_label)

        self._about_page_widget.setLayout(about_page_layout)

        self._credits_page_widget = QWidget(self)

        credits_page_layout = QVBoxLayout()

        credits_page_layout.addWidget(self._credits_label)
        credits_page_layout.addStretch()

        self._credits_page_widget.setLayout(credits_page_layout)

        self._license_page_widget = QWidget(self)

        self._license_page_textarea = QTextEdit(self)
        self._license_page_textarea.setReadOnly(True)

        with open("LICENSE", "r") as file:
            license_text = file.read()
            self._license_page_textarea.setText(license_text)

        license_page_layout = QVBoxLayout()

        license_page_layout.addWidget(self._license_page_textarea)
        license_page_layout.setContentsMargins(0, 0, 0, 0)

        self._license_page_widget.setLayout(license_page_layout)

        self._tabs = QTabWidget(self)

        self._tabs.addTab(self._about_page_widget, "About")
        self._tabs.addTab(self._credits_page_widget, "Credits")
        self._tabs.addTab(self._license_page_widget, "License")

        self._button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)

        self._ok_button = self._button_box.button(QDialogButtonBox.StandardButton.Ok)

        self._ok_button.clicked.connect(self.accept)

        main_layout = QVBoxLayout()

        main_layout.addLayout(top_level_layout)
        main_layout.addWidget(self._tabs)
        main_layout.addWidget(self._button_box)

        main_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(main_layout)
