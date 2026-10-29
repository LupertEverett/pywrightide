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
# parameterboxes: Outline of the parameter boxes
# foldmargin(1/2): Background color for fold margin. There are two different colors used in a checkerboard pattern
#
# Lines follow the format: "[Text Color],[Paper (Background) Color]", where each color is formatted as "#aarrggbb"

from pathlib import Path
from enum import IntEnum


def query_available_editor_themes() -> list[str]:
    return [x.stem for x in Path("res/editorcolorthemes").iterdir() if x.is_file() and x.suffix == ".editortheme"]


class ColorName(IntEnum):
    DEFAULT = 0
    COMMANDS = 1
    SPECIAL_VARS = 2
    PARAMETERS = 3
    LINE_COMMENTS = 4
    STRING_LITERALS = 5
    NUMBERS = 6
    BUILTIN_MACROS = 7
    GAME_MACROS = 8
    STRING_TOKENS = 9
    EDITOR_MARGIN = 10
    EDITOR_MARGIN_BORDER = 11
    CARET = 12
    MATCH_HIGHLIGHT = 13
    PARAMETER_BOXES = 14
    FOLD_MARGIN_1 = 15
    FOLD_MARGIN_2 = 16


class ColorTarget(IntEnum):
    TEXT = 0
    PAPER = 1


class EditorColor:

    def __init__(self, color_name: str, text_color: str, paper_color: str, style_index: int):
        self.color_name = color_name  # Color's name, written to the .editortheme file
        self.text_color = text_color  # Text color
        self.paper_color = paper_color  # Background color
        self.style_index = style_index  # Supplied to Lexer

    def __str__(self):
        if self.text_color == "":
            return "{}={}".format(self.color_name, self.paper_color)
        else:
            return "{}={},{}".format(self.color_name, self.text_color, self.paper_color)


# Default color theme
# For falling back in the case of a theme missing
_DEFAULT_STYLE_TEXT_COLOR = "#ff000000"
_DEFAULT_STYLE_PAPER_COLOR = "#ffffffff"

_DEFAULT_COMMANDS_TEXT_COLOR = "#ff00007f"
_DEFAULT_COMMANDS_PAPER_COLOR = "#ffffffff"

_DEFAULT_SPECIAL_VARIABLES_TEXT_COLOR = "#ff007f00"
_DEFAULT_SPECIAL_VARIABLES_PAPER_COLOR = "#ffffffff"

_DEFAULT_PARAMETERS_TEXT_COLOR = "#ff7f0000"
_DEFAULT_PARAMETERS_PAPER_COLOR = "#ffffffff"

_DEFAULT_COMMENTS_TEXT_COLOR = "#ffa0a0a0"
_DEFAULT_COMMENTS_PAPER_COLOR = "#ffffffff"

_DEFAULT_STRINGS_TEXT_COLOR = "#ff707000"
_DEFAULT_STRINGS_PAPER_COLOR = "#ffffffff"

_DEFAULT_NUMBERS_TEXT_COLOR = "#ff00a0a0"
_DEFAULT_NUMBERS_PAPER_COLOR = "#ffffffff"

_DEFAULT_BUILTIN_MACROS_TEXT_COLOR = "#ff0000dd"
_DEFAULT_BUILTIN_MACROS_PAPER_COLOR = "#ffffffff"

_DEFAULT_GAME_MACROS_TEXT_COLOR = "#ff4f00ff"
_DEFAULT_GAME_MACROS_PAPER_COLOR = "#ffffffff"

_DEFAULT_STRING_TOKENS_TEXT_COLOR = "#ff00af00"
_DEFAULT_STRING_TOKENS_PAPER_COLOR = "#ffffffff"

_DEFAULT_EDITOR_MARGIN_TEXT_COLOR = "#ff000000"
_DEFAULT_EDITOR_MARGIN_PAPER_COLOR = "#ffffffff"

_DEFAULT_EDITOR_MARGIN_BORDER_PAPER_COLOR = "#ff303030"

# Folding margins use two colors for its background
_DEFAULT_FOLD_MARGIN_PAPER_COLOR_1 = "#ffffffff"
_DEFAULT_FOLD_MARGIN_PAPER_COLOR_2 = "#ffffffff"

_DEFAULT_CARET_PAPER_COLOR = "#ffffffff"

_DEFAULT_MATCHINGTEXT_PAPER_COLOR = "#ff3ee2e8"

_DEFAULT_PARAMETER_BOX_PAPER_COLOR = "#2f0000ff"


class EditorColorTheme:

    def __init__(self):
        self.default_style_color = EditorColor("default", _DEFAULT_STYLE_TEXT_COLOR, _DEFAULT_STYLE_PAPER_COLOR, 0)
        self.commands_color = EditorColor("commands", _DEFAULT_COMMANDS_TEXT_COLOR, _DEFAULT_COMMANDS_PAPER_COLOR, 1)
        self.special_variables_color = EditorColor("specialvars", _DEFAULT_SPECIAL_VARIABLES_TEXT_COLOR,
                                                   _DEFAULT_SPECIAL_VARIABLES_PAPER_COLOR, 2)
        self.parameters_color = EditorColor("parameters", _DEFAULT_PARAMETERS_TEXT_COLOR,
                                            _DEFAULT_PARAMETERS_PAPER_COLOR, 3)
        self.line_comments_color = EditorColor("comments", _DEFAULT_COMMENTS_TEXT_COLOR, _DEFAULT_COMMENTS_PAPER_COLOR,
                                               4)
        self.string_literals_color = EditorColor("strings", _DEFAULT_STRINGS_TEXT_COLOR, _DEFAULT_STRINGS_PAPER_COLOR,
                                                 5)
        self.numbers_color = EditorColor("numbers", _DEFAULT_NUMBERS_TEXT_COLOR, _DEFAULT_NUMBERS_PAPER_COLOR, 6)
        self.builtin_macros_color = EditorColor("builtinmacros", _DEFAULT_BUILTIN_MACROS_TEXT_COLOR,
                                                _DEFAULT_BUILTIN_MACROS_PAPER_COLOR, 7)
        self.game_macros_color = EditorColor("gamemacros", _DEFAULT_GAME_MACROS_TEXT_COLOR,
                                             _DEFAULT_GAME_MACROS_PAPER_COLOR, 8)
        self.string_tokens_color = EditorColor("stringtokens", _DEFAULT_STRING_TOKENS_TEXT_COLOR,
                                               _DEFAULT_STRING_TOKENS_PAPER_COLOR, 9)
        self.editor_margin_color = EditorColor("editormargin", _DEFAULT_EDITOR_MARGIN_TEXT_COLOR,
                                               _DEFAULT_EDITOR_MARGIN_PAPER_COLOR, 0)
        self.editor_margin_border_color = EditorColor("editormarginborder", "",
                                                      _DEFAULT_EDITOR_MARGIN_BORDER_PAPER_COLOR, 0)
        self.caret_color = EditorColor("caret", "", _DEFAULT_CARET_PAPER_COLOR, 0)
        self.match_highlight_color = EditorColor("matchingtext", "", _DEFAULT_MATCHINGTEXT_PAPER_COLOR, 0)
        self.parameter_boxes_color = EditorColor("parameterboxes", "", _DEFAULT_PARAMETER_BOX_PAPER_COLOR, 0)

        self.fold_margin_color_1 = EditorColor("foldmargin1", "", _DEFAULT_FOLD_MARGIN_PAPER_COLOR_1, 0)
        self.fold_margin_color_2 = EditorColor("foldmargin2", "", _DEFAULT_FOLD_MARGIN_PAPER_COLOR_2, 0)

        self.colors_dict = {
            ColorName.DEFAULT : self.default_style_color,
            ColorName.COMMANDS : self.commands_color,
            ColorName.SPECIAL_VARS : self.special_variables_color,
            ColorName.PARAMETERS : self.parameters_color,
            ColorName.LINE_COMMENTS : self.line_comments_color,
            ColorName.STRING_LITERALS : self.string_literals_color,
            ColorName.NUMBERS : self.numbers_color,
            ColorName.BUILTIN_MACROS : self.builtin_macros_color,
            ColorName.GAME_MACROS : self.game_macros_color,
            ColorName.STRING_TOKENS : self.string_tokens_color,
            ColorName.EDITOR_MARGIN : self.editor_margin_color,
            ColorName.EDITOR_MARGIN_BORDER : self.editor_margin_border_color,
            ColorName.CARET : self.caret_color,
            ColorName.MATCH_HIGHLIGHT : self.match_highlight_color,
            ColorName.PARAMETER_BOXES : self.parameter_boxes_color,
            ColorName.FOLD_MARGIN_1 : self.fold_margin_color_1,
            ColorName.FOLD_MARGIN_2 : self.fold_margin_color_2
        }

    def get_color_string(self, color_name: ColorName, color_target: ColorTarget) -> str:
        match color_target:
            case ColorTarget.TEXT:
                return self.colors_dict[color_name].text_color
            case ColorTarget.PAPER:
                return self.colors_dict[color_name].paper_color

    def set_color_string(self, color_name: ColorName, color_target: ColorTarget, new_color_str: str):
        match color_target:
            case ColorTarget.TEXT:
                self.colors_dict[color_name].text_color = new_color_str
            case ColorTarget.PAPER:
                self.colors_dict[color_name].paper_color = new_color_str

    def __load_from_file(self, file_path: Path):
        if not file_path.exists() or not file_path.is_file():
            raise ThemeNotFoundException("Editor theme {} does not exist!".format(str(file_path)))

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
                    case "parameterboxes":
                        self.parameter_boxes_color.paper_color = values[0]
                    case "foldmargin1":
                        self.fold_margin_color_1.paper_color = values[0]
                    case "foldmargin2":
                        self.fold_margin_color_2.paper_color = values[0]

    def load_theme(self, theme_name: str):
        self.__load_from_file(Path("res/editorcolorthemes/{}.editortheme".format(theme_name)))

    def load_defaults(self):
        self.load_theme("default")

    def save_to_file(self, theme_file_name: str):
        with open("res/editorcolorthemes/{}.editortheme".format(theme_file_name), "w") as f:
            for color in self.colors:
                f.write(str(color) + "\n")

    def reset_colors_to_defaults(self):
        self.default_style_color.text_color = _DEFAULT_STYLE_TEXT_COLOR
        self.default_style_color.paper_color = _DEFAULT_STYLE_PAPER_COLOR

        self.commands_color.text_color = _DEFAULT_COMMANDS_TEXT_COLOR
        self.commands_color.paper_color = _DEFAULT_COMMANDS_PAPER_COLOR

        self.special_variables_color.text_color = _DEFAULT_SPECIAL_VARIABLES_TEXT_COLOR
        self.special_variables_color.paper_color = _DEFAULT_SPECIAL_VARIABLES_PAPER_COLOR

        self.parameters_color.text_color = _DEFAULT_PARAMETERS_TEXT_COLOR
        self.parameters_color.paper_color = _DEFAULT_PARAMETERS_PAPER_COLOR

        self.line_comments_color.text_color = _DEFAULT_COMMENTS_TEXT_COLOR
        self.line_comments_color.paper_color = _DEFAULT_COMMENTS_PAPER_COLOR

        self.string_literals_color.text_color = _DEFAULT_STRINGS_TEXT_COLOR
        self.string_literals_color.paper_color = _DEFAULT_STRINGS_PAPER_COLOR

        self.numbers_color.text_color = _DEFAULT_NUMBERS_TEXT_COLOR
        self.numbers_color.paper_color = _DEFAULT_NUMBERS_PAPER_COLOR

        self.builtin_macros_color.text_color = _DEFAULT_BUILTIN_MACROS_TEXT_COLOR
        self.builtin_macros_color.paper_color = _DEFAULT_BUILTIN_MACROS_PAPER_COLOR

        self.game_macros_color.text_color = _DEFAULT_GAME_MACROS_TEXT_COLOR
        self.game_macros_color.paper_color = _DEFAULT_GAME_MACROS_PAPER_COLOR

        self.string_tokens_color.text_color = _DEFAULT_STRING_TOKENS_TEXT_COLOR
        self.string_tokens_color.paper_color = _DEFAULT_STRING_TOKENS_PAPER_COLOR

        self.editor_margin_color.text_color = _DEFAULT_EDITOR_MARGIN_TEXT_COLOR
        self.editor_margin_color.paper_color = _DEFAULT_EDITOR_MARGIN_PAPER_COLOR

        self.editor_margin_border_color.paper_color = _DEFAULT_EDITOR_MARGIN_BORDER_PAPER_COLOR

        self.fold_margin_color_1.paper_color = _DEFAULT_FOLD_MARGIN_PAPER_COLOR_1
        self.fold_margin_color_2.paper_color = _DEFAULT_FOLD_MARGIN_PAPER_COLOR_2

        self.caret_color.paper_color = _DEFAULT_CARET_PAPER_COLOR

        self.match_highlight_color.paper_color = _DEFAULT_MATCHINGTEXT_PAPER_COLOR
        
        self.parameter_boxes_color = _DEFAULT_PARAMETER_BOX_PAPER_COLOR

    @staticmethod
    def load_from_theme_name(theme_name: str):
        result = EditorColorTheme()
        result.load_theme(theme_name)

        return result


# Global editor theme variable
current_editor_theme = EditorColorTheme()


class ThemeNotFoundException(Exception):
    pass
