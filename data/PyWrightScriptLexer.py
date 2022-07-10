# A custom lexer for PyWright scripts, mainly for syntax highlighting
import re

from PyQt5.QtGui import QColor, QFont

from PyQt5.Qsci import QsciLexerCustom, QsciScintilla

font_name = "Consolas"
font_size = 10

# TODO: Check doc.txt for the entire list of commands and such

commands = ["set", "sfx", "mus", "muslogic", "music_fade_out",
            "fg", "bg", "ev", "in", "out", "zoom", "obj",
            "gui", "Back", "Button", "Input", "Wait", "isempty", "is_ex",
            "addev", "delev", "addvar",
            "casemenu", "include",
            "setflag", "noflag", "delflag", "flag", "hideevr", "nt",
            "icon", "title", "author", "version",
            "label", "examine", "region", "menu", "char", "goto",
            "forgetlist", "showlist", "list", "li",
            "pause", "savegame", "delete", "scroll", "shake",
            "script", "macro", "endmacro", "guilty_words", "exit"]

properties = ["_allow_saveload", "_order_cases", "_cr_button", "_list_bg_image", "_music_loop", "_music_fade",
              "_testimony_blinker", "ev_mode_bg_logic", "_bigbutton_bg", "_bigbutton_img",
              "_textbox_allow_skip", "_allow_click_save", "_examine_showcursor",
              "_production", "_examine_showbars", "_ev_pages", "_ev"]

# Support up to 100 case definitions for a single game, this should be much more than enough.
cases = ["_case_{}".format(num) for num in range(100)]

parameters = ["start=", "end=", "e=", "x=", "y=", "z=", "name=", "speed=", "width=",
              "graphic=", "graphichigh=", "fail=",
              "stack", "nowait", "noclear", "hide", "fade", "true", "false", "penalty", "noback", "sx", "sy",
              "$_examine_clickx", "$_examine_clicky"]

# Following might need some sort of regex for each
# "{sound {str}}"
# "{c{number}}
# "{p{number}}
# "{delay {number}}
# "{sfx {str}}
# "{s {str}}"
string_tokens = ["{n}", "{next}", "{f}", "{center}"]


class PyWrightScriptLexer(QsciLexerCustom):

    def __init__(self, parent: QsciScintilla):
        super().__init__(parent)

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

        # Style 2: Properties (includes case names)
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

    def language(self):
        return "PyWright Script"

    def description(self, style):
        # match style:
        #     case 0:
        #         return "default_style"
        #     case 1:
        #         return "commands_style"
        #     case 2:
        #         return "properties_style"
        #     case 3:
        #         return "parameters_style"
        #     case 4:
        #         return "line_comments_style"
        #     case 5:
        #         return "double_quoted_strings_style"
        #     case 6:
        #         return "numbers_style"
        # return ""

        # Python < 3.10 compatibility moment

        if style == 0:
            return "default_style"
        elif style == 1:
            return "commands_style"
        elif style == 2:
            return "properties_style"
        elif style == 3:
            return "parameters_style"
        elif style == 4:
            return "line_comments_style"
        elif style == 5:
            return "double_quoted_strings_style"
        elif style == 6:
            return "numbers_style"
        else:
            return ""

    def styleText(self, start, end):
        self.startStyling(start)

        text = self.parent().text()[start:end]

        p = re.compile(r"//+[^\r\n]*|#+[^\r\n]*|\"+[^\r\n]*\"|\s+|\w+=?|\W")

        token_list = [(token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]

        for i, token in enumerate(token_list):
            if token[0] in commands:
                self.setStyling(token[1], 1)
            elif token[0] in properties or token[0] in cases:
                self.setStyling(token[1], 2)
            elif token[0] in parameters:
                self.setStyling(token[1], 3)
            elif token[0].startswith("{") and token[0].endswith("}"):
                self.setStyling(token[1], 3)
            elif token[0].startswith("//") or token[0].startswith("#"):
                self.setStyling(token[1], 4)
            elif token[0].startswith("\"") and token[0].endswith("\""):
                self.setStyling(token[1], 5)
            elif token[0].isnumeric():
                self.setStyling(token[1], 6)
            else:
                self.setStyling(token[1], 0)
