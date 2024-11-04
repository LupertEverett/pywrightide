# PyWright IDE: A simple IDE for working on PyWright games.

This project is a simple IDE written in Python and PyQt, that aims to make developing PyWright games easier. It features a tabbed text editor with syntax highlighting, dialogs to create new or interact with games/cases, and asset browsers.

## Dependencies

* A recent Python version (3.10+)
* PyQt6 and PyQt6-QScintilla
* pygame (only for playing sounds)

## Usage

For the source code version: Have all the dependencies installed, and then run PyWrightIDE.py

A compiled build for Windows is also available. Just download, extract and run PyWrightIDE.exe

## Building for Windows

Alongside the dependencies above, have `pyinstaller` installed via pip. Then run this command in the source code's root folder:

* pyinstaller PyWrightIDE.spec

Once the command finishes its job, the compiled program can be found in `/dist/pywrightide/`

## Screenshots

![](https://i.imgur.com/ZOMY6HP.png)

![](https://i.imgur.com/BniCVT0.png)

![](https://i.imgur.com/A9Wx2Ie.png)

![](https://i.imgur.com/Lv8cGeH.png)

![](https://i.imgur.com/nMzfyJI.png)

![](https://i.imgur.com/JGZRt1F.png)

![](https://i.imgur.com/iwvxCtj.png)

![](https://i.imgur.com/9go62w2.png)

## License

Code is licensed under **GPLv3**

Custom-made icons in `/res/icons` and `/res/iconthemes` that are supplied with this program are licensed with **Creative Commons BY/NC/SA**, with the exception of the ones that utilize official artworks in any way
(the icons that has the Blue Badger), "pwicon.png", which comes from PyWright, and its edited versions "ideicon.ico" and "ideicon.png".

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for details!

## Credits

See [CREDITS.md](CREDITS.md) for details!