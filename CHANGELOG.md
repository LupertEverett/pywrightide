# PyWright IDE Changelog

## Upcoming

* Added basic autocompletion support (by Zetrypio)
* Overhauled and streamlined game loading logic:
  * Now the user only has to select a PyWright Game folder! There is no need to select a PyWright root folder anymore, as it will be figured out from the selected game folder.
  * Thus, the corresponding button has been removed from the toolbar, and its functionality has been given to the "Open PyWright Game" button.
  * New Game Dialog now also has a PyWright Folder Path text field, due to the above changes.
  * **Note: This will "reset" some of the settings, namely the autoloading the last folder and the recent docs functionality, in order to avoid any oddities with the older, now incompatible data.**

---

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