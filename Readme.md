# PyWright IDE: A simple IDE for working on PyWright games.

This project is a curious experiment made with Python and PyQt, that aims at making developing PyWright games easier.

Includes a tabbed text editor with syntax highlighting, dialogs to create new games/cases, and an icon picker.

## Dependencies

* A recent Python version
* PyQt5 and QScintilla for Python

## Usage

For the source code version: Have all the dependencies installed, and then run PyWrightIDE.py

A compiled build for Windows is also available. Just download, extract and run PyWrightIDE.exe

## Building for Windows

Alongside the dependencies above, have pyinstaller installed via pip. Then run this command in the source code's root folder:

* pyinstaller PyWrightIDE.spec

Once the command finishes its job, the compiled program can be found in /dist/pywrightide/

## Notes

Consider this a beta quality software. Some of the features are not yet planned or missing, 
but you should be able to work with what's available just fine.

## Licenses / Credits

The code is licensed under GPLv3, and the custom made icons in /res/icons, barring the ones that utilize official artworks in any way
(the icons that has the Blue Badger), "pwicon.png", which comes from PyWright, and its edited versions "ideicon.ico" and "ideicon.png",
are licensed with Creative Commons BY/NC/SA.