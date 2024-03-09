# Mainly for storing the key names
from PyQt5.QtCore import QSettings, QByteArray

__program_settings = QSettings("PyWrightIDE", "PyWrightIDE")


# Key Names
FONT_NAME_KEY = "editor/font/name"
FONT_SIZE_KEY = "editor/font/size"
FONT_BOLD_KEY = "editor/font/bold"
AUTOLOAD_LAST_PROJECT_KEY = "general/autoload_last_project"
AUTOLOAD_LAST_PROJECT_PATH_KEY = "general/last_project_path"
AUTOLOAD_LAST_GAME_NAME_KEY = "general/last_game_name"
WINDOW_GEOMETRY_KEY = "general/window_geometry"
WINDOW_STATE_KEY = "general/window_state"
ICON_THEME_KEY = "general/icon_theme"
COLOR_THEME_KEY = "general/color_theme"
EDITOR_THEME_KEY = "editor/color_theme"

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


def get_autoload_last_project_check() -> bool:
    return __program_settings.value(AUTOLOAD_LAST_PROJECT_KEY, False, bool)


def set_autoload_last_project_check(new_value: bool):
    __program_settings.setValue(AUTOLOAD_LAST_PROJECT_KEY, new_value)


def get_autoload_last_project_path() -> str:
    return __program_settings.value(AUTOLOAD_LAST_PROJECT_PATH_KEY, "", str)


def set_autoload_last_project_path(new_path_str: str):
    __program_settings.setValue(AUTOLOAD_LAST_PROJECT_PATH_KEY, new_path_str)


def get_autoload_last_game_name() -> str:
    return __program_settings.value(AUTOLOAD_LAST_GAME_NAME_KEY, "", str)


def set_autoload_last_game_name(new_game_name_str: str):
    __program_settings.setValue(AUTOLOAD_LAST_GAME_NAME_KEY, new_game_name_str)


def get_window_geometry() -> bytes:
    return bytes(__program_settings.value(WINDOW_GEOMETRY_KEY, None, QByteArray))


def set_window_geometry(new_geometry: QByteArray):
    __program_settings.setValue(WINDOW_GEOMETRY_KEY, new_geometry)


def get_window_state() -> bytes:
    return bytes(__program_settings.value(WINDOW_STATE_KEY, None, QByteArray))


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


def all_keys() -> list[str]:
    return __program_settings.allKeys()


def window_geometry_data_exists() -> bool:
    return __program_settings.value(WINDOW_GEOMETRY_KEY) is not None


def window_state_data_exists() -> bool:
    return __program_settings.value(WINDOW_STATE_KEY) is not None


def save_settings():
    __program_settings.sync()


def reset_settings():
    __program_settings.setValue(FONT_NAME_KEY, "Consolas")
    __program_settings.setValue(FONT_SIZE_KEY, 10)
    __program_settings.setValue(FONT_BOLD_KEY, True)
    __program_settings.setValue(AUTOLOAD_LAST_PROJECT_KEY, False)
    __program_settings.setValue(AUTOLOAD_LAST_PROJECT_PATH_KEY, "")
    __program_settings.setValue(AUTOLOAD_LAST_GAME_NAME_KEY, "")
    __program_settings.setValue(WINDOW_GEOMETRY_KEY, None)
    __program_settings.setValue(ICON_THEME_KEY, "default")
    __program_settings.setValue(COLOR_THEME_KEY, "System Theme")
    __program_settings.setValue(EDITOR_THEME_KEY, "default")
