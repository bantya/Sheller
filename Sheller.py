import sublime_plugin
import subprocess
import sublime
import shlex
import os

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

        self.show_menu_label = kwargs.get('show_menu_lable', 'Command: ')
        self.args = []
        self.on_command()

        if not os.path.isfile(file_name):
            self.PROJECT_PATH = self.view.window().folders()[0]

    def folder_paras (self, path):
        path = path.split("\\")
        self.current_drive = path[0]

        path.pop()

        self.current_directory = "\\".join(path)

    def on_folder (self):
        self.check_dir_exist()

        self.PROJECT_PATH = self.view.window().folders()[0]

        self.show_status(self.PROJECT_PATH)

    def on_file (self, file_name):
        self.folder_paras(file_name)

        self.PROJECT_PATH = self.current_directory

        self.show_status(self.PROJECT_PATH)

    def open_shell_file (self, file_name):
        self.folder_paras(file_name)

        directory = self.current_directory
        command = "cd " + directory + " & " + self.current_drive + " & start cmd"

        os.system(command)
        self.show_status(directory)

    def open_shell_folder (self):
        self.check_dir_exist()

        path = self.view.window().folders()[0]

        self.folder_paras(path)

        self.current_directory = path
        command = "cd " + self.current_directory + " & " + self.current_drive + " & start cmd"

        os.system(command)
        self.show_status(path)

    def reveal_file (self, file_name):
        self.folder_paras(file_name)

        directory = self.current_directory
        self.args = []

        self.view.window().run_command(
            "open_dir", {
                "dir": directory
            }
        )
        self.show_status(directory)

    def reveal_folder (self):
        self.check_dir_exist()

        directory = self.view.window().folders()[0]
        self.args = []

        self.view.window().run_command(
            "open_dir",
            {"dir": directory}
        )
        self.show_status(directory)

    def on_command (self):
        self.view.window().show_input_panel(
            self.show_menu_label, '', self.on_show_menu, None, None
        )

    def on_show_menu (self, show_menu):
        self.args.extend(
            shlex.split(str(show_menu))
        )
        self.on_done()

    def show_status(self, message):
        sublime.status_message('Directory: ' + message + os.sep)

    def check_dir_exist(self):
        if self.view.window().folders() == []:
            sublime.error_message("Project root directory not found!")

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
