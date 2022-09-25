# A custom lexer for PyWright scripts, mainly for syntax highlighting
import re

from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import QSettings

from PyQt5.Qsci import QsciLexerCustom, QsciScintilla

from data import IDESettings

#font_name = "Consolas"
#font_size = 10

commands = [
    # In the written order in doc.txt (with some additions):
    # "To add various objects"
    "emo",
    "gui", "Back", "Button", "Wait", "Input",
    "menu",
    "list", "li", "showlist", "forgetlist", "forgetlistitem",
    "present",
    "examine", "region",
    # "Various control commands"
    "print", "include", "nt", "goto", "label", "penalty", "pause", "waitenter",
    "mus", "sfx", "movie",
    "exit", "endscript", "casemenu", "script", "top",
    "cross", "endcross", "statement", "resume", "cross_restart", "clearcross",
    "next_statement", "prev_statement",
    # "Variables and flags to keep track of what happens"
    "setflag", "delflag", "flag", "noflag", "set",
    "setvar", "joinvar", "addvar", "subvar", "divvar", "mulvar", "absvar",
    "random",
    "is", "AND", "isnot", "isempty", "isnotempty", "isnumber",
    "exportvars", "importvars", "savegame", "loadgame", "deletegame",
    # "Working with evidence"
    "addev", "delev",
    # "Special effects"
    "draw_off", "draw_on", "scroll", "rotate",
    # macros
    "macro", "endmacro",
    # data.txt fields
    "icon", "title", "author", "version",
    # "Animation file commands" (these can be added here too)
    "horizontal", "vertical", "length", "loops", "framedelay",
    "blinkmode", "blipsound", "framecompress",
    # "Art Types"
    "fg", "bg", "ev",
    # Not mentioned in doc.txt, but somewhere else
    "zoom", "char", "delete", "shake", "is_ex", "setvar_ex",
    # Misc. stuff (some might be custom macros, or stuff that wasn't in 0.9880)
    "in", "out", "obj"
]

special_variables = [
    # In the written order in doc.txt
    # "Used in actual game logic"
    "_speaking",
    # "Dev controls"
    "_debug", "_return", "_preload",
    # "Things engine sets which might be useful to use in logic"
    "_layer_invisible", "_layer_bg", "_layer_char", "_layer_fg", "_layer_textbox", "_layer_gui"
    "_speaking_name", "_lastline", "_currentline", "_lastlabel", "_currentlabel",
    "_statement", "_selected", "_examine_offset_x", "_examine_offset_y",
    "_examine_click_x", "_examine_click_y",
    # "Interface toggles so you can customize look or behavior of things"
    "_default_port_fg_delay", "_default_fg_frame_delay", "_list_checked_img", "_bigbutton_img",
    "_textbox_show_button", "_textbox_show_recordbutton", "_textbox_lines", "_textbox_wrap",
    "_textbox_allow_skip", "_textbox_skipupdate", "_nt_image", "_examine_skipupdate", "_examine_showbars",
    "_examine_showcursor", "_examine_use", "_examine_mousedown", "_testimony_blinker", "_cr_button",
    "_allow_present_evidence", "_allow_present_profiles", "_allow_click_save", "_allow_saveload",
    "_allow_click_load",
    # "Present customization"
    "_profiles_enable", "_profiles_present", "_evidence_enable", "_evidence_present",
    "_cr_back_button", "_list_back_button", "_menu_fade_level", "_double_screen_list_fade",
    "_flash_sound", "_shake_sound", "_music_loop",
    # "Used in intro.txt in the game folder to control menu"
    "_order_cases",
    # _case_0, _case_1, case_2... etc. are handled in a separate list
    # Misc. stuff that wasn't in the doc.txt (some might be custom macros, or stuff that wasn't in 0.9880)
    "_list_bg_image", "_music_fade", "ev_mode_bg_logic", "_bigbutton_bg",
    "_production", "_ev_pages", "_ev", "_version"
]

# Support up to 100 case definitions for a single game, this should be much more than enough.
cases = ["_case_{}".format(num) for num in range(100)]

# Just for that sweet, sweet startswith()
named_parameters = ("start=", "end=", "e=", "x=", "y=", "z=", "name=", "speed=", "width=",
                    "graphic=", "graphichigh=", "fail=", "nametag=", "result=", "mag=", "frames=")

parameters = ["stack", "nowait", "noclear", "hide", "fade", "true", "false", "noback", "sx", "sy",
              "blink", "loop", "stop", "noauto", "password"]

# Following might need some sort of regex for each
# "{sound {str}}"
# "{c{number}}
# "{p{number}}
# "{delay {number}}
# "{sfx {str}}
# "{s {str}}"
string_tokens = ["{n}", "{next}", "{f}", "{center}"]


def is_string_number(string: str) -> bool:
    if string.startswith("-"):
        return is_string_number(string[1:])

    return string.isnumeric() or is_string_float(string)


def is_string_float(string: str) -> bool:
    try:
        float(string)
        return True
    except ValueError:
        return False


class PyWrightScriptLexer(QsciLexerCustom):

    def __init__(self, parent: QsciScintilla):
        super().__init__(parent)

        settings = QSettings("PyWrightIDE", "PyWrightIDE")

        if IDESettings.FONT_NAME_KEY not in settings.allKeys():
            font_name = "Consolas"
        else:
            font_name = settings.value(IDESettings.FONT_NAME_KEY)
        if IDESettings.FONT_SIZE_KEY not in settings.allKeys():
            font_size = 10
        else:
            font_size = int(settings.value(IDESettings.FONT_SIZE_KEY))

        # Default Text Settings
        self.setDefaultColor(QColor("#ff000000"))
        self.setDefaultPaper(QColor("#ffffffff"))
        self.setDefaultFont(QFont(font_name, font_size))

        # Colors per style
        # Style 0: Default
        self.setColor(QColor("#ff000000"), 0)  # black
        self.setPaper(QColor("#ffffffff"), 0)
        self.setFont(QFont(font_name, font_size, weight=QFont.Bold), 0)

        # Style 1: Commands
        self.setColor(QColor("#ff00007f"), 1)  # blue
        self.setPaper(QColor("#ffffffff"), 1)
        self.setFont(QFont(font_name, font_size, weight=QFont.Bold), 1)

        # Style 2: Special Variables (includes case names)
        self.setColor(QColor("#ff007f00"), 2)  # green
        self.setPaper(QColor("#ffffffff"), 2)
        self.setFont(QFont(font_name, font_size, weight=QFont.Bold), 2)

        # Style 3: parameters
        self.setColor(QColor("#ff7f0000"), 3)  # red
        self.setPaper(QColor("#ffffffff"), 3)
        self.setFont(QFont(font_name, font_size, weight=QFont.Bold), 3)

        # Style 4: line comments
        self.setColor(QColor("#ffa0a0a0"), 4)  # gray
        self.setPaper(QColor("#ffffffff"), 4)
        self.setFont(QFont(font_name, font_size, weight=QFont.Bold), 4)

        # Style 5: Double-quoted strings
        self.setColor(QColor("#ff707000"), 5)  # ??? (I'm bad with colors)
        self.setPaper(QColor("#ffffffff"), 5)
        self.setFont(QFont(font_name, font_size, weight=QFont.Bold), 5)

        # Style 6: Numbers
        self.setColor(QColor("#ff00a0a0"), 6)  # ??? (I'm bad with colors)
        self.setPaper(QColor("#ffffffff"), 6)
        self.setFont(QFont(font_name, font_size, weight=QFont.Bold), 6)

        # Style 7: Builtin Macros
        self.setColor(QColor("#ff0000dd"), 7)  # (Cyan?)
        self.setPaper(QColor("#ffffffff"), 7)
        self.setFont(QFont(font_name, font_size, weight=QFont.Bold), 7)

        # Style 8: Game Macros
        self.setColor(QColor("#ff4f00ff"), 8)  # (Idk anymore...)
        self.setPaper(QColor("#ffffffff"), 8)
        self.setFont(QFont(font_name, font_size, weight=QFont.Bold), 8)

        self.builtin_macros: list[str] = []
        self.game_macros: list[str] = []

    def set_font_properties(self, font_name: str, font_size: int):
        self.setDefaultFont(QFont(font_name, font_size))
        for i in range(0, 9):
            self.setFont(QFont(font_name, font_size, weight=QFont.Bold), i)

    def set_builtin_macros(self, new_list: list[str]):
        self.builtin_macros = new_list

    def set_game_macros(self, new_list: list[str]):
        self.game_macros = new_list

    def language(self):
        return "PyWright Script"

    def description(self, style):
        if style == 0:
            return "default_style"
        elif style == 1:
            return "commands_style"
        elif style == 2:
            return "special_variables_style"
        elif style == 3:
            return "parameters_style"
        elif style == 4:
            return "line_comments_style"
        elif style == 5:
            return "double_quoted_strings_style"
        elif style == 6:
            return "numbers_style"
        elif style == 7:
            return "builtin_macros_style"
        elif style == 8:
            return "game_macros_style"
        else:
            return ""

    def styleText(self, start, end):
        self.startStyling(start)

        text = self.parent().text()[start:end]

        p = re.compile(r"//+[^\r\n]*|#+[^\r\n]*|\"[^\r\n]*\"|\S+|\s+")

        token_list = [(token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]

        for i, token in enumerate(token_list):
            self._set_styling_for_token(token)

    def _set_styling_for_token(self, token: tuple[str, int]):
        if token[0] in commands:
            self.setStyling(token[1], 1)
        elif token[0] in special_variables or token[0] in cases:
            self.setStyling(token[1], 2)
        elif token[0].startswith("$") and (token[0][1:] in special_variables
                                           or token[0][1:] in parameters):
            self.setStyling(token[1], 2)
        elif token[0].startswith(named_parameters):
            # Divide the = section and then colorize that instead
            param_name = token[0].split("=", maxsplit=1)
            param_0_len = len(param_name[0]) + 1  # + 1 for the "="
            self.setStyling(param_0_len, 3)
            param_1_token = (param_name[1], len(param_name[1]))
            self._set_styling_for_token(param_1_token)
        elif token[0] in parameters:
            self.setStyling(token[1], 3)
        elif token[0].startswith("{") and token[0].endswith("}"):
            self.setStyling(token[1], 3)
        elif token[0].startswith("//") or token[0].startswith("#"):
            self.setStyling(token[1], 4)
        elif token[0].startswith("\"") and token[0].endswith("\""):
            self.setStyling(token[1], 5)
        elif is_string_number(token[0]):
            self.setStyling(token[1], 6)
        elif token[0] in self.builtin_macros:
            self.setStyling(token[1], 7)
        elif token[0] in self.game_macros:
            self.setStyling(token[1], 8)
        else:
            self.setStyling(token[1], 0)
