# Holds the information regarding one PyWright game
# Like its name, version, cases and such

from pathlib import Path

from .PyWrightCase import PyWrightCase

import PyWrightFolder


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
        self.game_macros: list[str] = []
        self.pywright_folder_path: Path = Path("")

        if str(self.game_path) != "":
            self.pywright_folder_path = self.game_path.parent.parent

    @staticmethod
    def from_folder(folder_path: Path):
        if folder_path.parent.stem.lower() != "games":
            raise FileNotFoundError("Not a valid PyWright game folder")

        if not PyWrightFolder.is_valid_pywright_folder(str(folder_path.parent.parent)):
            raise FileNotFoundError("Not a valid PyWright game folder")

        game_title, game_author, game_version, game_icon_path = PyWrightGameInfo._load_data_txt(folder_path)

        game_cases = PyWrightGameInfo._load_intro_txt(folder_path)

        return PyWrightGameInfo(game_title, game_version, game_author, game_icon_path, game_cases, folder_path)


    @staticmethod
    def create_new_game(pywright_folder_path: Path,
                        game_version: str,
                        game_title: str,
                        game_author: str,
                        game_icon_path: str):
        pass

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


class PyWrightGame:
    def __init__(self):
        self.game_version: str = ""
        self.game_title: str = ""
        self.game_icon_path: str = ""
        self.game_author: str = ""
        self.game_cases: list[str] = []
        self.game_path: Path = Path("")
        self.game_macros: list[str] = []

    def is_a_game_selected(self) -> bool:
        return self.game_path.name != ""

    def set_game_path(self, new_game_path: str):
        self.game_path = Path(new_game_path)

    def get_game_name(self):
        return self.game_path.name

    def clear(self):
        self.clear_case_list()
        self.clear_data_txt_fields()
        self.game_macros.clear()

    def clear_data_txt_fields(self):
        self.game_version = ""
        self.game_title = ""
        self.game_author = ""
        self.game_icon_path = ""

    def set_data_txt_fields(self, version: str, title: str, icon_path: str, author: str):
        self.game_version = version
        self.game_title = title
        self.game_icon_path = icon_path
        self.game_author = author

    def set_case_list(self, case_list: list[str]):
        self.game_cases = case_list

    def clear_case_list(self):
        self.game_cases.clear()

    def load_data_txt(self):
        if not self.is_a_game_selected():
            print("No game path is set!")
            return

        with open(Path("{}/data.txt".format(self.game_path)), "r") as f:
            for line in f.readlines():
                # Only splitting from the first whitespace should be more than enough
                line_splitted = line.strip().split(" ", maxsplit=1)

                # This allows us to make this assumption easily.
                if not len(line_splitted) == 2:
                    continue

                # match line_splitted[0]:
                #     case "version":
                #         self.game_version = line_splitted[1]
                #     case "icon":
                #         self.game_icon_path = line_splitted[1]
                #     case "title":
                #         self.game_title = line_splitted[1]
                #     case "author":
                #         self.game_author = line_splitted[1]

                # Python < 3.10 compatibility moment

                if line_splitted[0] == "version":
                    self.game_version = line_splitted[1]
                elif line_splitted[0] == "icon":
                    self.game_icon_path = line_splitted[1]
                elif line_splitted[0] == "title":
                    self.game_title = line_splitted[1]
                elif line_splitted[0] == "author":
                    self.game_author = line_splitted[1]

    def load_intro_txt(self):
        if not self.is_a_game_selected():
            print("No game path is set!")
            return

        with open(Path("{}/intro.txt".format(self.game_path)), "r") as f:
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

                self.game_cases.append(line_splitted[2])

    def write_data_txt(self):
        if not self.is_a_game_selected():
            print("No game path is set!")
            return

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
        if not self.is_a_game_selected():
            print("No game path is set!")
            return

        with open(Path("{}/intro.txt".format(self.game_path)), "w") as f:
            f.write("set _order_cases variable\n")
            for i in range(len(self.game_cases)):
                f.write("set _case_{} {}\n".format(i + 1, self.game_cases[i]))
            f.write("casemenu")

    def update_intro_txt_cases(self):
        if not self.is_a_game_selected():
            print("No game path is set!")
            return

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

    def create_new_case(self, new_case: PyWrightCase):
        new_case_dir = Path("{}/{}".format(self.game_path, new_case.case_name))

        if new_case_dir.exists() and new_case_dir.is_dir():
            print("Case {} already exists!".format(new_case.case_name))
            return

        # Create the dir and add the necessary files
        new_case_dir.mkdir()

        # we can create an empty evidence.txt and initial script file.
        with open(new_case_dir/"{}.txt".format(new_case.initial_script_name), "w") as f:
            pass

        with open(new_case_dir/"evidence.txt", "w") as f:
            pass

        # intro.txt must have some initial data, that'll be dealt from new_case parameter
        with open(new_case_dir/"intro.txt", "w") as f:
            f.write(new_case.generate_case_intro_txt())

        # Finally, append the new case at the end of the cases list
        self.game_cases.append(new_case.case_name)
        self.update_intro_txt_cases()

    def create_new_game(self, game_path: str,
                        version: str,
                        title: str,
                        icon_path: str,
                        author: str):
        if game_path == "":
            # Rest of the strings can be empty, but game path must absolutely not be.
            raise ValueError("Game Folder must not be empty!")

        path = Path(game_path)

        if path.exists() and path.is_dir():
            # The folder shouldn't exist
            raise FileExistsError("Folder already exists!")

        # Create the folder now.
        path.mkdir()

        # Also create additional subfolders (so that we don't crash after creating a new game + it is more convenient):
        Path("{}/art".format(game_path)).mkdir()
        Path("{}/music".format(game_path)).mkdir()
        Path("{}/sfx".format(game_path)).mkdir()

        self.game_path = path
        self.set_data_txt_fields(version, title, icon_path, author)

        self.write_data_txt()
        self.write_intro_txt()

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

    def load_game(self, game_path: Path):
        self.game_path = game_path
        self.clear_data_txt_fields()
        self.clear_case_list()
        self.load_data_txt()
        self.load_intro_txt()
        self.parse_game_macros()

    def parse_game_macros(self):
        if not (self.game_path.exists() and self.game_path.is_dir()):
            raise FileNotFoundError("Selected game doesn't exist!")

        macro_files_list = self.game_path.glob("*.mcro")

        self.game_macros.clear()

        for macro_file_name in macro_files_list:
            with open(macro_file_name, "r", encoding="UTF-8") as f:
                lines = f.readlines()

                for line in lines:
                    if line.startswith("macro "):
                        splitted_lines = line.split(maxsplit=1)
                        self.game_macros.append(splitted_lines[1])
