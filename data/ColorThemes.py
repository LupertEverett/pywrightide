import glob
from pathlib import Path

from . import IDESettings


def query_color_themes() -> list[str]:
    return [x.stem for x in Path("res/colorthemes").iterdir() if x.is_dir() and _is_valid_theme_folder(x)]


def _is_valid_theme_folder(folder_path: Path):
    theme_file_name = folder_path/"theme.css"

    return theme_file_name.exists() and theme_file_name.is_file()


def set_color_theme(color_theme_name: str):
    folder_path = Path("res/colorthemes/{}".format(color_theme_name))

    if not _is_valid_theme_folder(folder_path):
        raise FileNotFoundError("Color theme {} not found!".format(color_theme_name))

    IDESettings.set_color_theme(color_theme_name)


def get_color_theme_path() -> str:
    color_theme_name = IDESettings.get_color_theme()

    folder_path = Path("res/colorthemes/{}".format(color_theme_name))

    if not _is_valid_theme_folder(folder_path):
        raise FileNotFoundError("Color theme {} not found!".format(color_theme_name))

    return "res/colorthemes/{}/theme.css".format(color_theme_name)


def load_current_color_theme() -> str:
    current_color_theme = IDESettings.get_color_theme()

    if current_color_theme == "System Theme":
        return ""

    result = ""
    with open(get_color_theme_path(), "r") as f:
        result_as_array = f.readlines()

        for line in result_as_array:
            result += line

    return result
