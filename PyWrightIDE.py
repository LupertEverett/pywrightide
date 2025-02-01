if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    from gui.IDEMainWindow import IDEMainWindow
    from gui.WelcomeDialog import WelcomeDialog
    from data import IDESettings
    from pathlib import Path

    import sys

    app = QApplication(sys.argv)

    # App style looks horrible when the app is run from Windows for some reason, this works around that
    # Perhaps switching to Qt6 was a mistake
    if sys.platform == "win32":
        app.setStyle("WindowsVista")

    # Check if the autoload path exists and is still a valid path
    # If that's the case, then launch the IDE, otherwise launch the Welcome dialog instead
    game_folder_path = Path(IDESettings.get_autoload_last_game_path())
    game_folder_exists = game_folder_path.exists() and game_folder_path.is_dir()

    if not IDESettings.get_autoload_last_game_check() or not game_folder_exists:
        welcome_dialog = WelcomeDialog()
        if welcome_dialog.exec():
            main_window = IDEMainWindow(welcome_dialog.get_selected_folder_path())
            main_window.show()
            app.exec()
    else:
        main_window = IDEMainWindow()
        main_window.show()
        app.exec()
