import sublime
import sublime_plugin
import os
import re
import sys
import subprocess
import json

package_name = "Grunt"

tasksJSON = re.compile(r'EXPOSE_BEGIN(.*)EXPOSE_END', re.M | re.I | re.DOTALL)

class GruntRunner(object):
    def __init__(self, window):
        self.window = window
        self.listGruntfiles()

    def listTasks(self):
        tasks = []
        sorted_tasks = []
        path = settings().get('exec_args').get('path')
        package_path = os.path.join(sublime.packages_path(), package_name)
        args = 'grunt --no-color --tasks "' + package_path + '" expose'

        p = subprocess.Popen( args, stdout=subprocess.PIPE, env={"PATH": path}, cwd=self.wd, shell=True)
        s = p.communicate()[0]
        t = tasksJSON.search(s.decode('utf8'))

        js = json.loads(t.groups()[0])
        for k in js.keys():
            task = js[k]
            tasks.append([k, task['info'], task['meta']['info']])

        sorted_tasks = sorted(tasks, key=lambda task: task)

        return tasks

    def listGruntfiles(self):
        self.grunt_files = []
        self.folders = []
        for f in self.window.folders():
            self.folders.append(f)
            if os.path.exists(os.path.join(f, "Gruntfile.js")):
                self.grunt_files.append(os.path.join(f, "Gruntfile.js"))
            elif os.path.exists(os.path.join(f, "Gruntfile.coffee")):
                self.grunt_files.append(os.path.join(f, "Gruntfile.coffee"))
        if len(self.grunt_files) > 0:
            if len(self.grunt_files) == 1:
                self.choose_file(0)
            else:
                self.window.show_quick_panel(self.grunt_files, self.choose_file)
        else:
            sublime.error_message("Gruntfile.js or Gruntfile.coffee not found!")

    def choose_file(self, file):
        self.wd = os.path.dirname(self.grunt_files[file])
        self.tasks = self.listTasks()
        self.window.show_quick_panel(self.tasks, self.on_done)

    def on_done(self, task):
        if task > -1:
            exec_args = settings().get('exec_args')
            exec_args.update({'cmd': u"grunt --no-color " + self.tasks[task][0], 'shell': True, 'working_dir': self.wd})
            self.window.run_command("exec", exec_args)

def settings():
    return sublime.load_settings('SublimeGrunt.sublime-settings')

class GruntCommand(sublime_plugin.WindowCommand):
    def run(self):
        GruntRunner(self.window)

class GruntKillCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.run_command("exec", {"kill": True})
