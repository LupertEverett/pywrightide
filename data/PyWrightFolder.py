from pathlib import Path


def is_valid_pywright_folder(selected_directory: str) -> bool:
    """Returns true if the selected folder is a valid PyWright directory."""

    return (Path(selected_directory).exists()
            and Path("{}/games".format(selected_directory)).exists()
            and Path("{}/art".format(selected_directory)).exists()
            and Path("{}/core".format(selected_directory)).exists()
            and __check_legit_pywright_executables(selected_directory))


def __check_legit_pywright_executables(selected_directory: str) -> bool:
    # Let's not handle macOS PyWright yet...
    return Path("{}/PyWright.exe".format(selected_directory)).exists() \
        or Path("{}/PyWright.py".format(selected_directory)).exists()


def pick_pywright_executable(selected_directory: str) -> str:
    """Picks a PyWright executable from the selected_directory.

    :param selected_directory: Selected Directory, must be the root folder of the PyWright installation."""
    # Default to Windows, fallback to the generic py version.
    win_pywright = Path("{}/PyWright.exe".format(selected_directory))
    py_pywright = Path("{}/PyWright.py".format(selected_directory))

    if win_pywright.exists():
        return win_pywright.name
    elif py_pywright.exists():
        return py_pywright.name
