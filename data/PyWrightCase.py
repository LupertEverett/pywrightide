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

                # match line_splitted[0]:
                #     case "set":
                #         match line_splitted[1]:
                #             case "_textbox_wrap":
                #                 self.textbox_wrap = line_splitted[2].lower() == "true"
                #             case "_textbox_lines":
                #                 self.textbox_lines = int(line_splitted[2])
                #
                #     case "addev":
                #         self.initial_evidence_list.append(line_splitted[1])
                #
                #     case "script":
                #         self.initial_script_name = line_splitted[1]

                # Python < 3.10 compatibility moment

                if line_splitted[0] == "set":
                    if line_splitted[1] == "_textbox_wrap":
                        self.textbox_wrap = line_splitted[2].lower() == "true"
                    elif line_splitted[1] == "_textbox_lines":
                        self.textbox_lines = int(line_splitted[2])

                elif line_splitted[0] == "addev":
                    self.initial_evidence_list.append(line_splitted[1])

                elif line_splitted[0] == "script":
                    self.initial_script_name = line_splitted[1]

    @staticmethod
    def from_existing_case_folder(case_folder_path: Path):
        if not case_folder_path.exists() or not case_folder_path.is_dir():
            raise FileNotFoundError("Case folder does not exist!")

        read_case = PyWrightCase(case_name=case_folder_path.stem)
        read_case.read_from_intro_txt(str(case_folder_path))

        return read_case

