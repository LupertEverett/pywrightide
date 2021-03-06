# Holds the information regarding one PyWright game
# Like its name, version, cases and such

from pathlib import Path

from .PyWrightCase import PyWrightCase


class PyWrightGame:
    def __init__(self):
        self.game_version: str = ""
        self.game_title: str = ""
        self.game_icon_path: str = ""
        self.game_author: str = ""
        self.game_cases: list[str] = []
        self.game_path: str = ""

    def is_a_game_selected(self) -> bool:
        return self.game_path != ""

    def set_game_path(self, new_game_path: str):
        self.game_path = new_game_path

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
        self.write_intro_txt()

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

        self.game_path = game_path
        self.set_data_txt_fields(version, title, icon_path, author)

        self.write_data_txt()
        self.write_intro_txt()
