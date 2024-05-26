if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    from gui.IDEMainWindow import IDEMainWindow

    import sys

    app = QApplication(sys.argv)

    # App style looks horrible when the app is run from Windows for some reason, this works around that
    # Perhaps switching to Qt6 was a mistake
    if sys.platform == "win32":
        app.setStyle("WindowsVista")

    main_window = IDEMainWindow()

    main_window.show()

    app.exec()
