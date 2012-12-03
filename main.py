import sublime
import sublime_plugin
import os
import re
import sys
#import subprocess

basicTasks = [
    ["lint", "Validate files with JSHint.", "Grunt default tasks"],
    ["qunit", "Run QUnit unit tests in a headless PhantomJS instance.", "Grunt default tasks"],
    ["min", "Minify files with UglifyJS.", "Grunt default tasks"],
    ["watch", "Run predefined tasks whenever watched files change.", "Grunt default tasks"],
    ["server", "Start a static web server.", "Grunt default tasks"],
    ["concat", "Concatenate files.", "Grunt default tasks"],
    ["test", "Run unit tests with nodeunit.", "Grunt default tasks"],
    ["init", "Generate project scaffolding from a predefined template.", "Grunt default tasks"]
]

rFiles = re.compile(r'loadNpmTasks\(\'(.*)\'\)', re.M | re.I)
rSingle = re.compile(r'registerTask.*\(.*\'(.*)\'.*,.*\'(.*)\'.*\)', re.M | re.I)
rMulti = re.compile(r'registerMultiTask.*\(.*\'(.*)\'.*,.*\'(.*)\'.*,', re.M | re.I)
rFunc = re.compile(r'registerMultiTask.*\(.*\'(.*)\'.*,.*\'(.*)\'.*,.*function\((.*)\).*{', re.M | re.I)


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
            elif os.path.exists(os.path.join(f, "Gruntfile.js")):
                self.grunt_files.append(os.path.join(f, "Gruntfile.js"))
        if len(self.grunt_files) > 0:
            if len(self.grunt_files) == 1:
                self.choose_file(0)
            else:
                self.window.show_quick_panel(self.grunt_files, self.choose_file)
        else:
            sublime.error_message("Gruntfile not found!")

    def extractTasks(self, file, source):
        tasks = []
        try:
            f = open(file, "r")
            for line in f:
                # Single Tasks
                matchSingle = rSingle.search(line)
                matchFunc = rFunc.search(line)
                matchMulti = rMulti.search(line)
                if matchSingle:
                    l = list(matchSingle.groups())
                    l.append(source)
                    tasks.append(l)
                    print l
                # Function Tasks
                elif matchFunc:
                    l = list(matchFunc.groups())
                    l.append(source)
                    l[0] = l[0] + ' *'
                    tasks.append(l)
                    print l
                # Multi Tasks
                elif matchMulti:
                    l = list(matchMulti.groups())
                    l.append(source)
                    l[0] = l[0] + ' **'
                    tasks.append(l)
                    print l
                #match = rMulti.search(line)
                #if match:
                #    self.tasks.append(list(match.groups()))
                #    print list(match.groups())
            f.close()
        except IOError:
            sys.stderr.write("[sublime-grunt] - Error: Could not open %s\n" % (file))
            sys.exit(-1)
        except:
            sys.stderr.write("[sublime-grunt] - Error =( \n")
            sys.exit(-1)
        return tasks

    def extractNpmFiles(self, file):
        files = []
        try:
            f = open(file, "r")
            for line in f:
                match = rFiles.search(line)
                if match:
                    files.append(match.groups()[0])
        except IOError:
            sys.stderr.write("[sublime-grunt] - Error: Could not open %s\n" % (file))
            sys.exit(-1)
        finally:
            f.close()
        return files

    def choose_file(self, file):
        self.wd = os.path.dirname(self.grunt_files[file])
        npmTasks = []

        files = self.extractNpmFiles(self.grunt_files[file])
        for f in files:
            taskFiles = [tf for tf in os.listdir(os.path.join(self.wd, "node_modules", f, "tasks")) if tf.lower().endswith('.js')]
            for tf in taskFiles:
                npmTasks = npmTasks + self.extractTasks(os.path.join(self.wd, "node_modules", f, "tasks", tf), "Module: %s" % f)
        self.tasks = self.extractTasks(self.grunt_files[file], self.grunt_files[file]) + npmTasks + basicTasks
        self.window.show_quick_panel(self.tasks, self.on_done)
        #self.window.show_quick_panel(files, self.on_done)

    def on_done(self, task):
        if task > -1:
            exec_args = settings().get('exec_args')
            exec_args.update({'cmd': u"grunt --no-color " + self.tasks[task][0], 'shell': True, 'working_dir': self.folders[0]})
            self.window.run_command("exec", exec_args)


def settings():
    return sublime.load_settings('SublimeGrunt.sublime-settings')


class GruntCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.window = self.view.window()
        GruntfileParser(self.window)
