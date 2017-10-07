import os
import shlex
import subprocess
import sublime
import sublime_plugin

class ShellerCommand(sublime_plugin.TextCommand):
    def __init__ (self, *args, **kwargs):
        super(ShellerCommand, self).__init__(*args, **kwargs)

    def run (self, *args, **kwargs):
        command = kwargs.get('command', None)
        file_name = self.view.file_name()

        if file_name is None:
            file_name = ''

        if command == 'sheller_folder':
            self.on_folder()
        elif command == 'sheller_file':
            self.on_file(file_name)
        elif command == 'sheller_reveal_file':
            self.reveal_file(file_name)
            return
        elif command == 'sheller_reveal_folder':
            self.reveal_folder()
            return
        elif command == 'sheller_open_shell_file':
            self.open_shell_file(file_name)
            return
        elif command == 'sheller_open_shell_folder':
            self.open_shell_folder()
            return

        file_path = os.path.join(self.PROJECT_PATH, file_name)

        print(file_path)

        self.show_menu_label = kwargs.get('show_menu_lable', 'Command: ')
        self.args = []
        self.on_command()

        if not os.path.isfile("%s" % file_name):
            self.PROJECT_PATH = self.view.window().folders()[0]

    def folder_paras (self, path):
        path = path.split("\\")
        self.current_drive = path[0]
        path.pop()
        self.current_directory = "\\".join(path)

    def on_folder (self):
        self.check_dis_exist()

        self.PROJECT_PATH = self.view.window().folders()[0]

    def on_file (self, file_name):
        self.folder_paras(file_name)
        self.PROJECT_PATH = self.current_directory

    def open_shell_file (self, file_name):
        self.folder_paras(file_name)
        command = "cd " + self.current_directory + " & " + self.current_drive + " & start cmd"
        os.system(command)

    def open_shell_folder (self):
        self.check_dis_exist()

        path = self.view.window().folders()[0]
        self.folder_paras(path)
        self.current_directory = path
        command = "cd " + self.current_directory + " & " + self.current_drive + " & start cmd"
        os.system(command)

    def reveal_file (self, file_name):
        self.folder_paras(file_name)

        self.args = []
        self.view.window().run_command(
            "open_dir",
            {
                "dir": self.current_directory
            }
        )

    def reveal_folder (self):
        self.check_dis_exist()

        self.args = []
        self.view.window().run_command(
            "open_dir",
            {"dir": self.view.window().folders()[0]}
        )

    def on_command (self):
        self.view.window().show_input_panel(self.show_menu_label, '', self.on_show_menu, None, None)

    def on_show_menu (self, show_menu):
        self.args.extend(shlex.split(str(show_menu)))
        self.on_done()

    def check_dis_exist(self):
        if self.view.window().folders() == []:
            sublime.error_message("Project Root Direcoty not found!")

    def on_done (self):
        if os.name != 'posix':
            self.args = subprocess.list2cmdline(self.args)

        try:
            self.view.window().run_command("exec", {
                "cmd": self.args,
                "shell": os.name == 'nt',
                "working_dir": self.PROJECT_PATH
                }
            )
            sublime.status_message('Command executed succesfully!')
        except IOError:
            sublime.status_message('IOError - Error occured')
