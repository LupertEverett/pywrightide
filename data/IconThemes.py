from PyQt5.QtCore import QSettings

from pathlib import Path

from . import IDESettings

# Icon names
ICON_NAME_FIND_PYWRIGHT = "pwicon.png"
ICON_NAME_NEW_GAME = "newgame.png"
ICON_NAME_OPEN_GAME = "opengame.png"
ICON_NAME_NEW_FILE = "newfile.png"
ICON_NAME_OPEN_FILE = "openfile.png"
ICON_NAME_SAVE_FILE = "save.png"
ICON_NAME_FIND_REPLACE = "findreplace.png"
ICON_NAME_RUN_PYWRIGHT = "runpywright.png"
ICON_NAME_SETTINGS = "settings.png"
ICON_NAME_ABOUT = "about.png"
ICON_NAME_DIRECTORY_VIEW_TOGGLE = "directoryviewtoggle.png"
ICON_NAME_ASSET_BROWSER_TOGGLE = "assetbrowsertoggle.png"
ICON_NAME_LOGGER_TOGGLE = "loggertoggle.png"
ICON_NAME_PLUS = "plus.png"
ICON_NAME_DOUBLE_PLUS = "doubleplus.png"
ICON_NAME_MINUS = "minus.png"
ICON_NAME_UP_ARROW = "uparrow.png"
ICON_NAME_DOWN_ARROW = "downarrow.png"

ICONS = [ICON_NAME_FIND_PYWRIGHT, ICON_NAME_NEW_GAME, ICON_NAME_OPEN_GAME, ICON_NAME_NEW_FILE, ICON_NAME_OPEN_FILE,
         ICON_NAME_SAVE_FILE, ICON_NAME_FIND_REPLACE, ICON_NAME_RUN_PYWRIGHT, ICON_NAME_SETTINGS, ICON_NAME_ABOUT,
         ICON_NAME_DIRECTORY_VIEW_TOGGLE, ICON_NAME_ASSET_BROWSER_TOGGLE, ICON_NAME_LOGGER_TOGGLE, ICON_NAME_PLUS,
         ICON_NAME_DOUBLE_PLUS, ICON_NAME_MINUS, ICON_NAME_UP_ARROW, ICON_NAME_DOWN_ARROW]


def icon_path_from_theme(icon_name: str) -> str:
    if icon_name not in ICONS:
        raise ValueError("Invalid icon name")

    icon_theme_name = IDESettings.get_icon_theme()

    full_path = "res/iconthemes/{}/{}".format(icon_theme_name, icon_name)

    if not Path(full_path).exists():
        raise FileNotFoundError("File not found in icon theme in path {}".format(full_path))

    return full_path


def is_icon_theme_folder_valid(theme_folder_name: str) -> bool:
    path_str = "res/iconthemes/{}".format(theme_folder_name)
    path = Path(path_str)
    if not path.exists() or not path.is_dir():
        return False

    for icon in ICONS:
        icon_path = Path("{}/{}".format(path_str, icon))
        if not icon_path.exists() or not icon_path.is_file():
            return False

    return True


def set_icon_theme_folder(new_icon_theme_name: str):
    if not is_icon_theme_folder_valid(new_icon_theme_name):
        return

    IDESettings.set_icon_theme(new_icon_theme_name)


def query_icon_themes() -> list[str]:
    result: list[str] = []

    dirs = [x for x in Path("res/iconthemes").iterdir() if x.is_dir()]

    for currdir in dirs:
        if is_icon_theme_folder_valid(currdir.name):
            result.append(currdir.name)

    return result
