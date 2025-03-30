# PyWright IDE: A simple IDE for working on PyWright games.

This project is a simple IDE written in Python and PyQt, that aims to make developing PyWright games easier. It features a tabbed text editor with syntax highlighting, dialogs to create new or interact with games/cases, and asset browsers.

## Dependencies

* A recent Python version (3.10+)
* PyQt6 and PyQt6-QScintilla
* pygame (only for playing sounds)

> [!NOTE]
> To easily install the dependencies, run this command below on the folder PyWright IDE is in:
> 
> `pip install -r requirements.txt`

## Usage

For the source code version: Have all the dependencies installed, and then run PyWrightIDE.py

A compiled build for Windows is also available. Just download, extract and run PyWrightIDE.exe

## Building for Windows

Alongside the dependencies above, have `pyinstaller` installed via pip. Then run this command in the source code's root folder:

* pyinstaller PyWrightIDE.spec

Once the command finishes its job, the compiled program can be found in `/dist/pywrightide/`

## Screenshots

![](https://i.imgur.com/pngNrF6.png)

![](https://i.imgur.com/uAPfJ8i.png)

![](https://i.imgur.com/VeXVzVs.png)

![](https://i.imgur.com/m2czWac.png)

![](https://i.imgur.com/7eTWSBz.png)

![](https://i.imgur.com/l80yQaK.png)

![](https://i.imgur.com/7rAP2ku.png)

![](https://i.imgur.com/McqYDQa.png)

## License

Code is licensed under **GPLv3**

Custom-made icons in `/res/icons` and `/res/iconthemes` that are supplied with this program are licensed with **Creative Commons BY/NC/SA**, with the exception of the ones that utilize official artworks in any way
(the icons that has the Blue Badger), "pwicon.png", which comes from PyWright, and its edited versions "ideicon.ico" and "ideicon.png".

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for details!

## Credits

See [CREDITS.md](CREDITS.md) for details!