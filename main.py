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
        #v.settings().set('todo_results', True)
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
        
        #f = open('/tmp/workfile', 'r')
    def choose_file(self, file):
        #print file
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
        print task
        #renderer = GruntConsole(self.window)
        #renderer.view.insert(edit, 0, "Hallooooo")
        #self.window.focus_view(renderer.view)
        #exec_args = settings['exec_args']
        #settings = [settings().get('exec_args')]
        exec_args = settings().get('exec_args')
        exec_args.update({'cmd': u"grunt --no-color " + self.tasks[task][0], 'shell': True, 'working_dir': self.folders[0]})
        print exec_args
        self.window.run_command("exec", exec_args)
        #(success, output) = run_cmd(".", "grunt " + self.tasks[task][0], True)
        #if success:
        #    print "success"
        #    edit = renderer.view.begin_edit()
        #    renderer.view.insert(edit, 0, output)
        #    renderer.view.end_edit(edit)
        #else:
        #    print "fail"

def settings():
    return sublime.load_settings('SublimeGrunt.sublime-settings')

class GruntCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.window = self.view.window()
        
        self.package_list = [
            ["Test", "Description", "aha"]
        ]
        #self.window.show_quick_panel(self.package_list, self.on_done)
        g = GruntfileParser(self.window)


def run_cmd(cwd, cmd, wait, input_str=None):
    shell = isinstance(cmd, basestring)
    if wait:
        proc = subprocess.Popen(cmd, cwd=cwd,
                                     shell=shell,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     stdin=(subprocess.PIPE if input_str else None))
        output, error = proc.communicate(input_str)
        return_code = proc.poll()
        if return_code:
            sublime.error_message("The following command exited with status "
                                  + "code " + str(return_code) + ":\n" + cmd
                                  + "\n\nOutput:\n" + output
                                  + "\n\nError:\n" + error)
            return (False, None)
        else:
            return (True, output)
    else:
        subprocess.Popen(cmd, cwd=cwd, shell=shell)
        return (False, None)