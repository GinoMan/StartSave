# StartSave
A Python script that can be run from a shortcut key to save to start with notes.

**Authored by [Gino Vincenzini](mailto:OpenMySourceCode@gmail.com)**

## USAGE ##

`python save-start-menu.py [--reset]`

It is recommended that you create a shortcut that runs this program against the python interpreter or a virtual environment with all the packages installed. Then assign a shortcut key to the shortcut. When you wish to save your start menu as raw binary data, press the shortcut key and a window will appear asking what was changed since the last start menu save. Put in a detailed description and the saved start menu binary data will be tagged with that information in a text file that indexes all the changes made.

To delete all saved start menus and the manifest file, run the program with the `--reset` option.

## Description ##

This script loads the registry key in which the database for start menu entries are stored It then saves the binary data into incrementally counted files and adds an entry with a note on what changed into a text file. The note is obtained by showing a dialog box to the user asking for a description. The program is attached to a shortcut with a key combination (Ctrl+Shift+O) which allows the user to run it on the fly as changes are made to the start menu. Hopefully by doing this enough, the format of the data in the registry key can be reverse engineered so that by loading, changing, and then resaving the key, and then issuing a command to refresh the start menu. Such would bypass Microsoft's refusal to make start menu pinning available to legitimate programs that wish to do it.

## Command Line Options ##

One can append the --reset switch to reset the contents of both the file and the directory with saved start menu entries by deleting them.

## Further Notes ##

The code is quite quick and dirty, I intended for this to provide a useful tool for another project I'm working on that pins websites to the start menu from firefox. I don't see a likelihood for Microsoft to block this method in the future and up to date Windows 10 installs use this method for the start-menu storage. In fact, I'm betting they cannot since to do so would prevent windows itself from accessing or changing the start menu. Even if they changed the key name, or the file name, or worse, the format itself, they would only buy themselves a little time before it was determined how to work around it. The best course of action for Microsoft would be to provide an API to get permission from the user, save that permission in association with the program that requested it, and then allow the program access to change the start menu pins. IT managers want it, they want users to be able to see a set of default pins, and still be able to unpin or rearrange those pins as they wish. They want to be able to pin things to their users start menu. It seems a redesign is coming soon but the general premise is the same in the new design. We'll have to see if they change the way this works for that redesign.
