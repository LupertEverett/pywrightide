# Holds the basic information regarding one PyWright case

from pathlib import Path


class PyWrightCase:

    def __init__(self, case_name: str = "", initial_script: str = ""):
        self.case_name: str = case_name.strip()
        self.initial_script_name: str = initial_script.strip()
        self.textbox_lines: int = 3
        self.textbox_wrap: bool = True
        self.initial_evidence_list: list[str] = []

    def generate_case_intro_txt(self) -> str:
        result = "set _textbox_wrap {}\n".format(self.textbox_wrap) + \
               "set _textbox_lines {}\n".format(self.textbox_lines) + \
               "include evidence\n"

        for ev in self.initial_evidence_list:
            result += "addev {}\n".format(ev)

        result += "script {}".format(self.initial_script_name)

        return result

    def update_case_intro_txt(self, case_folder_path: Path):
        """Non-destructively updates an intro.txt file
        :param case_folder_path: Path to the Case that's going to be updated"""
        if not case_folder_path.exists() or not case_folder_path.is_dir():
            raise FileNotFoundError("Invalid case folder!")

        intro_txt = case_folder_path/"intro.txt"

        if not intro_txt.exists():
            raise FileNotFoundError("Missing intro.txt file for the case!")

        # Load the current intro.txt into memory...
        with open(intro_txt, "r") as f:
            whole_file = f.readlines()

        # ...change the appropriate fields...
        for idx in range(len(whole_file)):
            line = whole_file[idx]
            line_splitted = line.split(maxsplit=3)

            if len(line_splitted) <= 1:
                continue

            ends_with_newline = line.endswith("\n")
            if line_splitted[0] == "set":
                if line_splitted[1] == "_textbox_wrap":
                    whole_file[idx] = "set _textbox_wrap {}".format(str(self.textbox_wrap).lower())
                elif line_splitted[1] == "_textbox_lines":
                    whole_file[idx] = "set _textbox_lines {}".format(self.textbox_lines)

                if ends_with_newline:
                    whole_file[idx] += "\n"

            elif line_splitted[0] == "script":
                whole_file[idx] = "script {}".format(self.initial_script_name)
                if ends_with_newline:
                    whole_file[idx] += "\n"

        # ...and finally write everything back to intro.txt
        with open(intro_txt, "w") as f:
            f.writelines(whole_file)

    def read_from_intro_txt(self, case_folder_path: str):
        if not Path(case_folder_path).exists() or not Path(case_folder_path).is_dir():
            print("Invalid case folder!")
            return

        intro_txt = Path("{}/intro.txt".format(case_folder_path))

        if not intro_txt.exists():
            print("Missing intro.txt file for the case!")
            return

        with open(intro_txt, "r") as f:
            self.initial_evidence_list.clear()
            for line in f.readlines():
                line_splitted = line.split(maxsplit=3)

                if len(line_splitted) <= 1:
                    continue

                match line_splitted[0]:
                    case "set":
                        match line_splitted[1]:
                            case "_textbox_wrap":
                                self.textbox_wrap = line_splitted[2].lower() == "true"
                            case "_textbox_lines":
                                self.textbox_lines = int(line_splitted[2])

                    case "addev":
                        self.initial_evidence_list.append(line_splitted[1])

                    case "script":
                        self.initial_script_name = line_splitted[1]

    @staticmethod
    def from_existing_case_folder(case_folder_path: Path):
        if not case_folder_path.exists() or not case_folder_path.is_dir():
            raise FileNotFoundError("Case folder does not exist!")

        read_case = PyWrightCase(case_name=case_folder_path.stem)
        read_case.read_from_intro_txt(str(case_folder_path))

        return read_case

