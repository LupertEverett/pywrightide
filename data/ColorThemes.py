import glob
from pathlib import Path

from . import IDESettings


def query_color_themes() -> list[str]:
    return glob.glob("*.css", root_dir="res/colorthemes/")

def _is_color_theme_exists(color_theme_name: str) -> bool:
    full_path = Path("res/colorthemes/{}".format(color_theme_name))

    return full_path.exists() and not full_path.is_dir()

def set_color_theme(color_theme_name: str):
    if not _is_color_theme_exists(color_theme_name):
        raise FileNotFoundError("Color theme {} not found!".format(color_theme_name))

    IDESettings.set_color_theme(color_theme_name)


def get_color_theme_path() -> str:
    color_theme_name = IDESettings.get_color_theme()

    if not _is_color_theme_exists(color_theme_name):
        raise FileNotFoundError("Color theme {} not found!".format(color_theme_name))

    return "res/colorthemes/{}".format(color_theme_name)


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
