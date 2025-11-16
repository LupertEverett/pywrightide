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

## Building a Compiled Version

Alongside the dependencies above, have `pyinstaller` installed via pip. Then run this command in the source code's root folder:

* pyinstaller PyWrightIDE-[Platform].spec

Where [Platform] can be either Windows or Linux

Once the command finishes its job, the compiled program can be found in `/dist/pywrightide/`

## Screenshots

![](https://imgur.com/pJiss5P.png)

![](https://imgur.com/uAPfJ8i.png)

![](https://imgur.com/RJtba9F.png)

![](https://imgur.com/RANxjs4.png)

![](https://imgur.com/kLO6D9Y.png)

![](https://imgur.com/spP62RJ.png)

![](https://imgur.com/bzLkC8X.png)

![](https://imgur.com/Gra9grD.png)

## License

Code is licensed under **GPLv3**

Custom-made icons in `/res/icons` and `/res/iconthemes` that are supplied with this program are licensed with **Creative Commons BY/NC/SA**, with the exception of the ones that utilize official artworks in any way
(the icons that has the Blue Badger), "pwicon.png", which comes from PyWright, and its edited versions "ideicon.ico" and "ideicon.png".

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for details!

## Credits

See [CREDITS.md](CREDITS.md) for details!