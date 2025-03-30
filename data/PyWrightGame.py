# Holds the information regarding one PyWright game
# Like its name, version, cases and such

from pathlib import Path

from .PyWrightCase import PyWrightCase

from . import PyWrightFolder


class PyWrightGameInfo:

    def __init__(self, game_title: str = "",
                 game_version: str = "",
                 game_author: str = "",
                 game_icon_path: Path = "",
                 game_cases: list[str] = [],
                 game_path: Path = ""):
        self.game_title: str = game_title
        self.game_version: str = game_version
        self.game_author: str = game_author
        self.game_icon_path: Path = game_icon_path
        self.game_cases: list[str] = game_cases
        self.game_path: Path = game_path
        self.builtin_macros: list[str] = []
        self.game_macros: list[str] = []
        self.pywright_folder_path: Path = Path("")

        if str(self.game_path) != "":
            self.pywright_folder_path = self.game_path.parent.parent

    @staticmethod
    def is_valid_game_folder(folder_path: Path):
        if folder_path.parent.stem.lower() != "games":
            return False

        if not PyWrightFolder.is_valid_pywright_folder(str(folder_path.parent.parent)):
            return False

        return True

    @staticmethod
    def load_from_folder(folder_path: Path):
        if folder_path.parent.stem.lower() != "games":
            raise FileNotFoundError("{} is not a valid PyWright game folder".format(folder_path))

        if not PyWrightFolder.is_valid_pywright_folder(str(folder_path.parent.parent)):
            raise FileNotFoundError("{} is not a valid PyWright folder".format(str(folder_path.parent.parent)))

        game_title, game_author, game_version, game_icon_path = PyWrightGameInfo._load_data_txt(folder_path)

        game_cases = PyWrightGameInfo._load_intro_txt(folder_path)

        game_info = PyWrightGameInfo(game_title, game_version, game_author, game_icon_path, game_cases, folder_path)
        game_info.parse_builtin_macros()
        game_info.parse_game_macros()

        return game_info

    @staticmethod
    def create_new_game(pywright_folder_path: Path,
                        game_folder_name: str,
                        game_version: str,
                        game_title: str,
                        game_author: str,
                        game_icon_path: Path):
        if pywright_folder_path == "":
            raise ValueError("PyWright folder path must not be empty!")

        if game_folder_name == "":
            raise ValueError("Game folder name must not be empty!")

        game_path = pywright_folder_path / "games" / game_folder_name

        if game_path.exists() and game_path.is_dir():
            # The folder mustn't already exist.
            raise FileExistsError("Folder already exists: {}".format(game_path))

        # Create the folder now.
        game_path.mkdir()

        # Also create additional subfolders (so that we don't crash after creating a new game + it is more convenient):
        (game_path / "art").mkdir()
        (game_path / "music").mkdir()
        (game_path / "sfx").mkdir()

        # Create the game info
        game_info = PyWrightGameInfo(game_title, game_version, game_author, game_icon_path, [], game_path)

        # Make it write the necessary files
        game_info.write_data_txt()
        game_info.write_intro_txt()

        # Return the created game info
        return game_info

    # Returns the info from data.txt in a manner the Welcome Dialog can use
    @staticmethod
    def get_game_data_info(game_folder_path: Path):
        game_title, game_author, game_version, game_icon_path = PyWrightGameInfo._load_data_txt(game_folder_path)

        game_icon_full_path = game_folder_path / game_icon_path
        if not game_icon_full_path.exists() or not game_icon_full_path.is_file():
            # Try the global folder
            pywright_path = game_folder_path.parent.parent
            game_icon_full_path = pywright_path / game_icon_path

            if not game_icon_full_path.exists() or not game_icon_full_path.is_file():
                # Not in the global folder either, bail out
                game_icon_full_path = ""

        return game_title, game_author, game_version, game_icon_full_path

    @staticmethod
    def _load_data_txt(game_folder_path: Path):
        file_path = game_folder_path / "data.txt"
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError("{} does not exist".format(file_path))

        game_title = ""
        game_version = ""
        game_author = ""
        game_icon_path = Path("")

        with open(file_path, "r") as f:
            for line in f.readlines():
                # Only splitting from the first whitespace should be more than enough
                line_splitted = line.strip().split(" ", maxsplit=1)

                # This allows us to make this assumption easily.
                if not len(line_splitted) == 2:
                    continue

                match line_splitted[0]:
                    case "version":
                        game_version = line_splitted[1]
                    case "icon":
                        game_icon_path = Path(line_splitted[1])
                    case "title":
                        game_title = line_splitted[1]
                    case "author":
                        game_author = line_splitted[1]

        return game_title, game_author, game_version, game_icon_path

    @staticmethod
    def _load_intro_txt(game_folder_path: Path):
        file_path = game_folder_path / "intro.txt"
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError("{} does not exist".format(file_path))

        game_cases: list[str] = []

        with open(file_path, "r") as f:
            for line in f.readlines():
                if not line.strip().startswith("set _case_"):
                    continue

                # now we should be only dealing with the lines that start with "set _case_"
                line = line.strip()
                # Only splitting from the first two whitespaces (because of "set" and "_case_")
                # should be more than enough
                line_splitted = line.split(" ", maxsplit=2)

                if not len(line_splitted) == 3:
                    continue

                game_cases.append(line_splitted[2])

        return game_cases

    def write_data_txt(self):
        with open(Path("{}/data.txt".format(self.game_path)), "w") as f:
            if self.game_title != "":
                f.write("title {}\n".format(self.game_title))
            if self.game_version != "":
                f.write("version {}\n".format(self.game_version))
            if self.game_author != "":
                f.write("author {}\n".format(self.game_author))
            if self.game_icon_path != "":
                f.write("icon {}".format(self.game_icon_path))

    def write_intro_txt(self):
        with open(Path("{}/intro.txt".format(self.game_path)), "w") as f:
            f.write("set _order_cases variable\n")
            for i in range(len(self.game_cases)):
                f.write("set _case_{} {}\n".format(i + 1, self.game_cases[i]))
            f.write("casemenu")

    def update_intro_txt_cases(self):
        with open(Path("{}/intro.txt".format(self.game_path)), "r") as f:
            entire_file = f.readlines()

        # Find the set _case_x lines and update them
        # Easiest way to do this is by finding, removing then inserting the new values
        for line_idx in range(len(entire_file)):
            if entire_file[line_idx] == "set _order_cases variable\n":
                # Remove the previously written case entries
                while entire_file[line_idx + 1].startswith("set _case_"):
                    entire_file.pop(line_idx + 1)

                for case_idx in range(len(self.game_cases)):
                    entire_file.insert(line_idx + (case_idx + 1),
                                       "set _case_{} {}\n".format(case_idx + 1, self.game_cases[case_idx]))

                break

        # Rewrite the intro.txt with the updated cases
        with open(Path("{}/intro.txt".format(self.game_path)), "w") as f:
            f.writelines(entire_file)

    def create_new_case(self, case_info: PyWrightCase):
        new_case_dir = Path("{}/{}".format(self.game_path, case_info.case_name))

        if new_case_dir.exists() and new_case_dir.is_dir():
            raise FileExistsError("Case {} already exists!".format(case_info.case_name))

        # Create the dir and add the necessary files
        new_case_dir.mkdir()

        # we can create an empty evidence.txt and initial script file.
        with open(new_case_dir / "{}.txt".format(case_info.initial_script_name), "w") as f:
            pass

        with open(new_case_dir / "evidence.txt", "w") as f:
            pass

        # intro.txt must have some initial data, that'll be dealt from new_case parameter
        with open(new_case_dir / "intro.txt", "w") as f:
            f.write(case_info.generate_case_intro_txt())

        # Finally, append the new case at the end of the cases list
        self.game_cases.append(case_info.case_name)
        self.update_intro_txt_cases()

    def remove_case(self, case_name: str, also_remove_folder: bool):
        try:
            self.game_cases.remove(case_name)
            self.update_intro_txt_cases()

            if also_remove_folder:
                import shutil
                case_dir = Path("{}/{}".format(self.game_path, case_name))
                shutil.rmtree(case_dir)
        except ValueError:
            pass

    @staticmethod
    def _parse_macros_in_folder(folder_path: Path) -> list[str]:
        """Parses all .mcro files in a given folder path"""
        if not (folder_path.exists() and folder_path.is_dir()):
            raise FileNotFoundError("Selected folder doesn't exist!")

        macro_files_list = folder_path.glob("*.mcro")

        macros_list = []

        for macro_file_name in macro_files_list:
            with open(macro_file_name, "r", encoding="UTF-8") as f:
                lines = f.readlines()

                for line in lines:
                    if line.startswith("macro "):
                        splitted_lines = line.split(maxsplit=1)
                        macros_list.append(splitted_lines[1].strip("\n"))

        return macros_list

    def parse_builtin_macros(self):
        self.builtin_macros = PyWrightGameInfo._parse_macros_in_folder(self.pywright_folder_path)

    def parse_game_macros(self):
        self.game_macros = PyWrightGameInfo._parse_macros_in_folder(self.game_path)

    def get_game_name(self):
        return self.game_path.name

    def clear_case_list(self):
        self.game_cases.clear()

    def clear_data_txt_fields(self):
        self.game_version = ""
        self.game_title = ""
        self.game_author = ""
        self.game_icon_path = ""

    def clear(self):
        self.clear_data_txt_fields()
        self.clear_case_list()
        self.builtin_macros.clear()
        self.game_macros.clear()
