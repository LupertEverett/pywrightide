from PyQt5.QtWidgets import QWidget, QMessageBox

from data import IDESettings


__about_text = "<h1>PyWright IDE</h1>" +\
               "<h2>Version {} ({})</h2>".format(IDESettings.IDE_VERSION_STRING, IDESettings.IDE_BUILD_STRING) +\
               "<h3>by LupertEverett</h3>" +\
               "This program aims to make developing PyWright games easier.<br>" +\
               "Made with PyQt5, QScintilla and pygame."


def about_pywright_ide(parent: QWidget):
    QMessageBox.about(parent, "About PyWright IDE", __about_text)
