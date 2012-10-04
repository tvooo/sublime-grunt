sublime-grunt
=============

A Grunt plugin for Sublime Text

## Usage
Open the command palette using Ctrl+Shift+P (or Cmd+Shift+P on Mac, respectively)
and choose the "Grunt" command.

The plugin expects to find a Grunt file (`grunt.js`) in an open folder.
It displays a list of available Grunt tasks out of this grunt file.
If it finds more than one, it first provides a list for selection.


## Settings
The file `SublimeGrunt.sublime-settings` is used for configuration.
You may have to add the path to your Node.js installation to the `path`
variable.