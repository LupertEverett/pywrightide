# Text Editor Color Themes handling

# Colors are put into the .editortheme file as "key=value(s)" pairs. Available keys:
#
# default: Default color
# commands: Commands ("set", "include", "script", ...)
# specialvars: Special Variables ("_ev", "_order_cases", ...)
# parameters: Parameters ("stack", "nowait", "hide", ...)
# comments: Line comments
# strings: String literals
# numbers: Self-explanatory
# builtinmacros: Built-in Macros (that come with PyWright)
# gamemacros: Game-specific Macros
# stringtokens: String tokens ("{n}", "{c{number}}", ...)
# editormargin: Scintilla's Margin section, all margins
# editormarginborder: Special margin reserved for acting like a border between line number area and text area
# caret: The vertical line on the text editing area that indicates the position, and also blinks.
# matchingtext: Highlight color on matching text occurrences.
#
# Lines follow the format: "[Text Color],[Paper (Background) Color]", where each color is formatted as "#aarrggbb"

from pathlib import Path


def query_available_editor_themes() -> list[str]:
    return [x.stem for x in Path("res/editorcolorthemes").iterdir() if x.is_file() and x.suffix == ".editortheme"]


class EditorColor:

    def __init__(self, color_name: str, text_color: str, paper_color: str, style_index: int):
        self.color_name = color_name     # Color's name, written to the .editortheme file
        self.text_color = text_color     # Text color
        self.paper_color = paper_color   # Background color
        self.style_index = style_index   # Supplied to Lexer

    def __str__(self):
        if self.text_color == "":
            return "{}={}".format(self.color_name, self.paper_color)
        else:
            return "{}={},{}".format(self.color_name, self.text_color, self.paper_color)


class EditorColorTheme:

    def __init__(self):
        self.default_style_color = EditorColor("default",  "#ff000000", "#ffffffff", 0)
        self.commands_color = EditorColor("commands",  "#ff00007f", "#ffffffff", 1)
        self.special_variables_color = EditorColor("specialvars", "#ff007f00", "#ffffffff", 2)
        self.parameters_color = EditorColor("parameters", "#ff7f0000", "#ffffffff", 3)
        self.line_comments_color = EditorColor("comments", "#ffa0a0a0", "#ffffffff", 4)
        self.string_literals_color = EditorColor("strings", "#ff707000", "#ffffffff", 5)
        self.numbers_color = EditorColor("numbers", "#ff00a0a0", "#ffffffff", 6)
        self.builtin_macros_color = EditorColor("builtinmacros", "#ff0000dd", "#ffffffff", 7)
        self.game_macros_color = EditorColor("gamemacros", "#ff4f00ff", "#ffffffff", 8)
        self.string_tokens_color = EditorColor("stringtokens", "#ff00af00", "#ffffffff", 9)
        self.editor_margin_color = EditorColor("editormargin", "#ff000000", "#ffffffff", 0)
        self.editor_margin_border_color = EditorColor("editormarginborder", "", "#ff303030", 0)
        self.caret_color = EditorColor("caret", "", "#ffffffff", 0)
        self.match_highlight_color = EditorColor("matchingtext", "", "#ff3ee2e8",0)

        self.colors = [self.default_style_color, self.commands_color, self.special_variables_color,
                       self.parameters_color, self.line_comments_color, self.string_literals_color,
                       self.numbers_color, self.builtin_macros_color, self.game_macros_color,
                       self.string_tokens_color, self.editor_margin_color, self.editor_margin_border_color,
                       self.caret_color, self.match_highlight_color]

    def __load_from_file(self, file_path: Path):
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError("Editor theme {} does not exist!".format(str(file_path)))

        with open(file_path, "r") as f:
            all_lines = f.readlines()

            for line in all_lines:
                key_value_pair = line.split("=")
                key = key_value_pair[0]
                values = key_value_pair[1].split(",")

                for i in range(len(values)):
                    values[i] = values[i].strip("\n")

                match key:
                    case "default":
                        self.default_style_color.text_color = values[0]
                        self.default_style_color.paper_color = values[1]
                    case "commands":
                        self.commands_color.text_color = values[0]
                        self.commands_color.paper_color = values[1]
                    case "specialvars":
                        self.special_variables_color.text_color = values[0]
                        self.special_variables_color.paper_color = values[1]
                    case "parameters":
                        self.parameters_color.text_color = values[0]
                        self.parameters_color.paper_color = values[1]
                    case "comments":
                        self.line_comments_color.text_color = values[0]
                        self.line_comments_color.paper_color = values[1]
                    case "strings":
                        self.string_literals_color.text_color = values[0]
                        self.string_literals_color.paper_color = values[1]
                    case "numbers":
                        self.numbers_color.text_color = values[0]
                        self.numbers_color.paper_color = values[1]
                    case "builtinmacros":
                        self.builtin_macros_color.text_color = values[0]
                        self.builtin_macros_color.paper_color = values[1]
                    case "gamemacros":
                        self.game_macros_color.text_color = values[0]
                        self.game_macros_color.paper_color = values[1]
                    case "stringtokens":
                        self.string_tokens_color.text_color = values[0]
                        self.string_tokens_color.paper_color = values[1]
                    case "editormargin":
                        self.editor_margin_color.text_color = values[0]
                        self.editor_margin_color.paper_color = values[1]
                    case "editormarginborder":
                        self.editor_margin_border_color.paper_color = values[0]
                    case "caret":
                        self.caret_color.paper_color = values[0]
                    case "matchingtext":
                        self.match_highlight_color.paper_color = values[0]

    def load_theme(self, theme_name: str):
        self.__load_from_file(Path("res/editorcolorthemes/{}.editortheme".format(theme_name)))

    def load_defaults(self):
        self.load_theme("default")

    def save_to_file(self, theme_file_name: str):
        with open("res/editorcolorthemes/{}.editortheme".format(theme_file_name), "w") as f:
            for color in self.colors:
                f.write(str(color) + "\n")


    @staticmethod
    def load_from_theme_name(theme_name: str):
        result = EditorColorTheme()
        result.load_theme(theme_name)

        return result


# Global editor theme variable
current_editor_theme = EditorColorTheme()
