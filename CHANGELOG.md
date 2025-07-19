# PyWright IDE Changelog

## Unreleased

* Lexer improvements:
  * Add more parameters from docs/index.html (by Zetrypio)
  * Add distinction for "fade" and "script" depending on where they are used, which can be both a command or a parameter (by Zetrypio)

## Version 1.4.2 - 31.05.2025

* Fixed syntax highlighting for consecutive inline macros (by in1tiate)
* Fixed Find/Replace dialog needing the user to position the cursor before it can search text.
* Added the ability to highlight the other occurrences of the selected text.
  * This can be toggled off in the settings.
  * There are two highlight styles to choose from: "Hollow" and "Filled"
  * Note that if you're using a custom editor color theme, you might need to update it to account for the highlight color.
* Slightly tidied up the Settings dialog.
* Cursor position (line and column) and the amount of selected characters are now shown in the status bar.

## Version 1.4.1 - 17.05.2025

* Fixed the crash caused by tab(s) being unable to be restored due to file(s) no longer existing (by in1tiate)
* PyWright IDE now informs the user in the case of some tabs being unable to be restored due to missing files.
* Fixed the crash that happens when the user tries to close the IDE with no tabs open.

## Version 1.4 - 06.05.2025

* Welcome dialog now shows the game's icon and the author info, if the relevant fields are provided in data.txt
* Lots of Lexer improvements:
  * Added separate coloring for {} tokens in strings (by Zetrypio)
  * Added handling for logical operators (==, >=, AND, OR, etc) (by in1tiate)
  * Added handling for engine-level macro argument access variables (by in1tiate)
  * Fixed question mark operators at the end of conditionals breaking highlighting for the last operand (by in1tiate)
  * Fixed inline macro calls with arguments not being highlighted (by in1tiate)
    * Arguments to inline macro calls will now be highlighted as normal. (by in1tiate)
  * Added missing keywords "suppress" (by in1tiate) and "OR"
  * Fixed built-in and game macros' names not being highlighted.
* Added a Color Editor dialog for editing text editor component themes.
* Added requirements.txt for a more convenient way to download the required dependencies (by in1tiate)
* Moved built-in macro handling to PyWrightGameInfo class (less code duplication)
* Find/Replace Dialog:
  * "Find" field will be filled with highlighted text on the active tab (if there is any) on startup. (by in1tiate)
  * "Find Next" button is now highlighted by default. (by in1tiate)
* PyWright IDE can now be buildable on Linux.
* Compiled versions of PyWright IDE are now bundled with PyQt 6.9.0
  * Mainly so that the IDE can show its own icon when it is run under Linux/Wayland

## Version 1.3.4 - 09.03.2025

* Fix the wrong ordering of parameters being given to create_new_game(), resulting in author and icon path info changing places.

## Version 1.3.3 - 01.02.2025

* IDE now opens the Welcome dialog if the last open game folder is missing for whatever reason, instead of refusing to open itself until the folder is back.
* Similarly, the Welcome dialog now notifies the user about such an issue occuring.

## Version 1.3.2 - 22.12.2024

* Added more missing keywords to the Script Lexer (by in1tiate)
* Autocompletion suggestions can now be toggled off in the settings.
* Autocompletion suggestions can now have a varying trigger threshold in between 1-10 characters
  (i.e. if you set it to 5 then you'll have to type at least 5 characters to make it appear).

## Version 1.3.1 - 21.11.2024

* Added the missing "hotkey=" keyword to Script Lexer (by in1tiate)
* Make AboutDialog load the credits from CREDITS.md file instead.

## Version 1.3 - 09.11.2024

* Added basic autocompletion support (by Zetrypio)
* Overhauled and streamlined game loading logic:
  * Now the user only has to select a PyWright Game folder! There is no need to select a PyWright root folder anymore, as it will be figured out from the selected game folder.
  * Thus, the corresponding button has been removed from the toolbar, and its functionality has been given to the "Open PyWright Game" button.
  * New Game Dialog now also has a PyWright Folder Path text field, due to the changes above.
  * **Note: This will "reset" some of the settings, namely the autoloading the last folder and the recent docs functionality, in order to avoid any oddities with the older, now incompatible data.**
* Renamed the "Autoreload the last open project" setting to "Restore the last open game and tabs on startup" to better reflect its purpose.
* Added the ability to restore the last open tabs, when the "Restore the last open game and tabs on startup" setting is enabled.
* Main window's title now shows the currently open game.
* Fixed the Settings and New PyWright Game windows looking squished on Linux
* Drop down menu of the Open PyWright Game button now indicates that there are no other games to switch to when it is the case, instead of showing nothing.
* Improved About Dialog.
* Added a "Reset All Settings" button to Settings Dialog.

## Version 1.2.4 - 01.11.2024

* Fix crashes with Directory View, now it is possible to remove files from there once again.

## Version 1.2.3 - 03.10.2024

* Added the ability to browse the music/sfx files of individual cases.
* Fixed an issue where adding multibyte unicode characters (€, ½, etc.) into a script would corrupt the syntax highlighter.

## Version 1.2.2 - 25.07.2024

* Add an "Insert as looping music" option to the music browser's right click menu.

## Version 1.2.1 - 06.07.2024

* Use Python's own isinstance() function instead of checking the tab's name for detecting whether we're in a Game Properties tab or not. This fixes a crash on Linux because in certain cases (like running PyWright IDE outside PyCharm), the tab title gets a hidden "&" added in front of it for some reason (I blame (Py?)Qt6).
* Change the keys used a bit so that the settings file won't randomly get corrupted in Linux, as apparently using "general" as a key name is a BAD idea with (Py?)Qt6.
  * Note that this effectively "resets" the settings on ALL platforms. I apologize for the inconvenience.
* Welcome dialog now saves the added folders once you load one of them as well, instead of only when the user closes the dialog and not loads the IDE.
* Settings dialog is now cannot be resizeable.
* Introduce theme overriding on Linux. Just add a `theme_linux.css` file inside the theme folder to override certain aspects of the theme only on Linux.
* Some dark theme fixes for Linux.

## Version 1.2 - 30.06.2024

* Added a Welcome screen that allows the user to add and select PyWright folders, which can be skipped if the user has the "Always load the selected folder" option enabled (or the "Autoreload the last open project" option in the settings)
* "Locate PyWright Installation" button is renamed to "Open PyWright Folder" and it allows you to quickly switch to the previous folders you've opened!
* Open PyWright Game dialog:
  * Now uses QListView + QStandardItemModel instead of QListWidget, allowing it to show icons for the game folders.
  * OK button is disabled until a game is selected, preventing a crash.
* Audio and SFX Browsers:
  * Switched to QListView + QStandardItemModel from QListWidget, making the sound file entries have icons which change dynamically when they start/stop playing.
  * Added icons for Play and Stop buttons, which was long overdue.
* Asset Browsers in general:
  * They now REALLY, TRULY clear themselves on PyWright folder changes, unlike in v1.1
  * Added a Refresh button (as well as a corresponding icon for it) on each tab to manually refresh the currently selected folder (per request of BirbIsTheWord).

## Version 1.1.1 - 28.05.2024

* Reduce minimum sizes on some places, so that the IDE can be snapped to half of the screen without taking extra space once again.
* A better border color for the Windows System Theme override.
* Make the group boxes have a transparent background color on dark theme (should fix an issue with how the theme looks on Linux).

## Version 1.1 - 26.05.2024

* Everything is ported to PyQt6.
  * Functionality-wise this shouldn't change anything.
  * Added some workarounds for it looking a bit glitchy on Windows.
* Asset browsers now keep track of the changed files, and update themselves accordingly.
* Asset browsers clear themselves when the user changes the PyWright installation.
* Fixed a crash when there is no global music folder present in the selected PyWright installation.

## Version 1.0.1 - 24.03.2024

* Fix the crash happening when one right clicks on Directory View and chooses the "Add Case" option.

## Version 1.0 - 17.03.2024

* Initial stable release.
* Changelog from the previous snapshot build:
  * Introduce text editor component theming, and add a "dark mode" editor theme.
  * Find/Replace button is now disabled when there are no PyWright installations selected.
  * Various cleanups and moving code around.