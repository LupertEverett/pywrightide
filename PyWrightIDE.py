if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    from gui.IDEMainWindow import IDEMainWindow

    import sys

    app = QApplication(sys.argv)

    main_window = IDEMainWindow()

    main_window.show()

    app.exec_()
