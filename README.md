# sublime-file-commands

## Installation

Install the package as `FileCommands` through Package Control.

## Usage

This package has the following commands to work with file
more easily.

* `open_or_create_file`
    Opens or creates a file.
    Will also create all directories in between when needed when creating file.

* `save_quit`
    Saves and closes the file.
    Closes Sublime Text if it is the last file open and no directory or project is opened.

* `try_quit`
    Closes the file (or prompt if not saved).
    Closes Sublime Text if it is the last file open and no directory or project is opened.

* `force_quit`
    Closes the file even if not saved.
    Closes Sublime Text if it is the last file open and no directory or project is opened.

The package commands are available in the Command Palette
so that they can be accessed through vim bindings,
but any keybings works perfectly, for example:

```json
[
  { "keys": ["super+w"], "command": "try_quit" },
  { "keys": ["super+o"], "command": "open_or_create_file" }
]
```


Open file screenshot:

![screenshot-1423632337](https://cloud.githubusercontent.com/assets/1436271/6142441/e980dfe2-b1f9-11e4-828d-0fbe6f277199.png)


