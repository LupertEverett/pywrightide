# Mainly for storing the key names
from PyQt6.QtCore import QSettings, QByteArray

IDE_VERSION_STRING = "1.3.1"
IDE_BUILD_STRING = "24.11.21"

__program_settings = QSettings("PyWrightIDE", "PyWrightIDE")


# Key Names
FONT_NAME_KEY = "editor/font/name"
FONT_SIZE_KEY = "editor/font/size"
FONT_BOLD_KEY = "editor/font/bold"
AUTOLOAD_LAST_GAME_KEY = "autoload_last_game"
AUTOLOAD_LAST_GAME_PATH_KEY = "last_game_path"
WINDOW_GEOMETRY_KEY = "window_geometry"
WINDOW_STATE_KEY = "window_state"
ICON_THEME_KEY = "icon_theme"
COLOR_THEME_KEY = "color_theme"
EDITOR_THEME_KEY = "editor/color_theme"
RECENT_GAMES_KEY = "recent_games"
LAST_OPEN_TABS_KEY = "last_open_tabs"
LAST_OPEN_TAB_INDEX_KEY = "last_open_tab_index"
ENABLE_AUTOCOMPLETION_KEY = "enable_autocompletion"
AUTOCOMPLETION_THRESHOLD_KEY = "autocompletion_suggestions_threshold"

# Functions


def get_font_name() -> str:
    return __program_settings.value(FONT_NAME_KEY, "Consolas", str)


def set_font_name(new_name: str):
    __program_settings.setValue(FONT_NAME_KEY, new_name)


def get_font_size() -> int:
    return __program_settings.value(FONT_SIZE_KEY, 10, int)


def set_font_size(new_size: int):
    __program_settings.setValue(FONT_SIZE_KEY, new_size)


def get_font_boldness() -> bool:
    return __program_settings.value(FONT_BOLD_KEY, True, bool)


def set_font_boldness(new_value: bool):
    return __program_settings.setValue(FONT_BOLD_KEY, new_value)


def get_autoload_last_game_check() -> bool:
    return __program_settings.value(AUTOLOAD_LAST_GAME_KEY, False, bool)


def set_autoload_last_game_check(new_value: bool):
    __program_settings.setValue(AUTOLOAD_LAST_GAME_KEY, new_value)


def get_autoload_last_game_path() -> str:
    return __program_settings.value(AUTOLOAD_LAST_GAME_PATH_KEY, "", str)


def set_autoload_last_game_path(new_game_path_str: str):
    __program_settings.setValue(AUTOLOAD_LAST_GAME_PATH_KEY, new_game_path_str)


def get_window_geometry() -> QByteArray:
    return __program_settings.value(WINDOW_GEOMETRY_KEY)


def set_window_geometry(new_geometry: QByteArray):
    __program_settings.setValue(WINDOW_GEOMETRY_KEY, new_geometry)


def get_window_state() -> QByteArray:
    return __program_settings.value(WINDOW_STATE_KEY)


def set_window_state(new_state: QByteArray):
    __program_settings.setValue(WINDOW_STATE_KEY, new_state)


def get_icon_theme() -> str:
    return __program_settings.value(ICON_THEME_KEY, "default")


def set_icon_theme(new_theme_name: str):
    __program_settings.setValue(ICON_THEME_KEY, new_theme_name)


def get_color_theme() -> str:
    return __program_settings.value(COLOR_THEME_KEY, "System Theme")


def set_color_theme(new_color_theme_name: str):
    if new_color_theme_name == "":
        raise ValueError("Empty Color Theme Name!")
    __program_settings.setValue(COLOR_THEME_KEY, new_color_theme_name)


def get_editor_color_theme() -> str:
    return __program_settings.value(EDITOR_THEME_KEY, "default")


def set_editor_color_theme(new_editor_theme_name: str):
    if new_editor_theme_name == "":
        raise ValueError("Empty Editor Color Theme Name!")
    __program_settings.setValue(EDITOR_THEME_KEY, new_editor_theme_name)


def get_recent_games() -> list[str]:
    result: list[str] = []

    size = __program_settings.beginReadArray(RECENT_GAMES_KEY)
    for idx in range(size):
        __program_settings.setArrayIndex(idx)
        result.append(__program_settings.value("folder_path"))
    __program_settings.endArray()

    return result


def set_recent_games(docs: list[str]):
    __program_settings.beginWriteArray(RECENT_GAMES_KEY)

    for idx in range(len(docs)):
        __program_settings.setArrayIndex(idx)
        __program_settings.setValue("folder_path", docs[idx])

    __program_settings.endArray()


def get_last_open_tabs() -> list[str]:
    result: list[str] = []

    size = __program_settings.beginReadArray(LAST_OPEN_TABS_KEY)
    for idx in range(size):
        __program_settings.setArrayIndex(idx)
        result.append(__program_settings.value("file_path"))
    __program_settings.endArray()

    return result


def set_recent_open_tabs(open_files_paths: list[str]):
    __program_settings.beginWriteArray(LAST_OPEN_TABS_KEY)

    for idx in range(len(open_files_paths)):
        __program_settings.setArrayIndex(idx)
        __program_settings.setValue("file_path", open_files_paths[idx])

    __program_settings.endArray()


def get_last_open_tab_index() -> int:
    return __program_settings.value(LAST_OPEN_TAB_INDEX_KEY, 0, type=int)


def set_last_open_tab_index(new_tab_index: int):
    if new_tab_index < 0:
        raise ValueError("New Tab Index cannot be negative!")
    __program_settings.setValue(LAST_OPEN_TAB_INDEX_KEY, new_tab_index)


def get_enable_autocompletion_check() -> bool:
    return __program_settings.value(ENABLE_AUTOCOMPLETION_KEY, True, bool)


def set_enable_autocompletion_check(new_value: bool):
    __program_settings.setValue(ENABLE_AUTOCOMPLETION_KEY, new_value)


def get_autocompletion_trigger_threshold() -> int:
    return __program_settings.value(AUTOCOMPLETION_THRESHOLD_KEY, 1, int)


def set_autocompletion_trigger_threshold(new_threshold: int):
    __program_settings.setValue(AUTOCOMPLETION_THRESHOLD_KEY, new_threshold)


def all_keys() -> list[str]:
    return __program_settings.allKeys()


def window_geometry_data_exists() -> bool:
    return __program_settings.value(WINDOW_GEOMETRY_KEY) is not None


def window_state_data_exists() -> bool:
    return __program_settings.value(WINDOW_STATE_KEY) is not None


def save_settings():
    __program_settings.sync()


def reset_settings():
    __program_settings.clear()
    __program_settings.setValue(FONT_NAME_KEY, "Consolas")
    __program_settings.setValue(FONT_SIZE_KEY, 10)
    __program_settings.setValue(FONT_BOLD_KEY, True)
    __program_settings.setValue(AUTOLOAD_LAST_GAME_KEY, False)
    __program_settings.setValue(AUTOLOAD_LAST_GAME_PATH_KEY, "")
    __program_settings.setValue(WINDOW_GEOMETRY_KEY, None)
    __program_settings.setValue(ICON_THEME_KEY, "default")
    __program_settings.setValue(COLOR_THEME_KEY, "System Theme")
    __program_settings.setValue(EDITOR_THEME_KEY, "default")
    __program_settings.setValue(ENABLE_AUTOCOMPLETION_KEY, True)
    __program_settings.setValue(AUTOCOMPLETION_THRESHOLD_KEY, 1)
