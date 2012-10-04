import sublime, sublime_plugin
from xml.etree import ElementTree as ET
import os
import re
import subprocess

class GruntConsole(object):
    def __init__(self, window):
        self.window = window

    @property
    def view(self):
        v = self.window.new_file()
        v.set_name("Grunt")
        v.set_scratch(True)
        return v

class GruntfileParser(object):
    def __init__(self, window):
        self.window = window
        self.grunt_files = []
        self.folders = []
        for f in self.window.folders():
            self.folders.append(f)
            if os.path.exists(os.path.join(f, "grunt.js")):
                self.grunt_files.append(os.path.join(f, "grunt.js"))
        if len(self.grunt_files) > 0:
            if len(self.grunt_files) == 1:
                self.choose_file(0)
            else:
                self.window.show_quick_panel(self.grunt_files, self.choose_file)
        else:
            sublime.error_message("Gruntfile not found!")
        
    def choose_file(self, file):
        self.tasks = []
        try:
            f = open(self.grunt_files[0], "r")
            #s = f.read()
            regex = re.compile( r'registerTask\(\'(.*)\', \'(.*)\'\)', re.M|re.I)
            for line in f:
                match = regex.search(line)
                if match:
                    self.tasks.append(list(match.groups()))
                #else:
                #    print "No match!!"
        except IOError:
            sys.stderr.write( "[myScript] - Error: Could not open %s\n" % (inputFn) )
            sys.exit(-1)

        self.window.show_quick_panel(self.tasks, self.on_done)

    def on_done(self, task):
        exec_args = settings().get('exec_args')
        exec_args.update({'cmd': u"grunt --no-color " + self.tasks[task][0], 'shell': True, 'working_dir': self.folders[0]})
        self.window.run_command("exec", exec_args)

def settings():
    return sublime.load_settings('SublimeGrunt.sublime-settings')

class GruntCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.window = self.view.window()
        g = GruntfileParser(self.window)