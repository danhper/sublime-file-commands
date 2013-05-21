import sublime
import sublime_plugin
import os


def get_home_dir():
    if sublime.platform() == 'windows':
        return os.environ['USERPROFILE']
    else:
        return os.environ['HOME']


class WindowCommandExtension(sublime_plugin.WindowCommand):
    def close_if_no_file(self):
        if not self.window.views():
            self.window.run_command("close_window")

    def close_file_and_window(self):
        self.window.run_command("close_file")
        self.close_if_no_file()


class SaveQuit(WindowCommandExtension):
    def run(self):
        v = self.window.active_view()
        if v is None:
            return
        if v.is_dirty():
            v.run_command("save")
        self.close_file_and_window()


class ForceQuit(WindowCommandExtension):
    def run(self):
        v = self.window.active_view()
        if v is None:
            return
        if v.is_dirty():
            if v.file_name():
                v.run_command("revert")
            else:
                v.set_scratch(True)
        self.close_file_and_window()


class TryQuit(WindowCommandExtension):
    def run(self):
        v = self.window.active_view()
        if v is None:
            return
        if v.is_dirty():
            self.window.run_command("get_confirmation", {
                'caption': "Save changes?",
                'on_yes': "save_quit",
                'on_no': "force_quit",
                'on_cancel': None
            })
        else:
            self.close_file_and_window()


class Quit(WindowCommandExtension):
    def run(self):
        v = self.window.active_view()
        if not v:
            return
        self.window.run_command("close_file")
        self.close_if_no_file()


class VimOpenFile(sublime_plugin.WindowCommand):
    # cant override __init__ ><
    def init(self):
        self.settings = sublime.load_settings("VimCommands.sublime-settings")

    def run(self):
        self.init()
        try:
            self.current_view = self.window.active_view()
            file_dir = os.path.dirname(self.current_view.file_name())
            self.current_path = file_dir
        except:
            self.current_path = os.getcwd()
        if not self.current_path.endswith('/'):
            self.current_path += '/'

        self.input_panel = self.window.show_input_panel("Open file", self.current_path, self.on_done, self.on_change, None)
        self.input_panel.settings().set('tab_completion', False)

    def on_done(self, text):
        try:
            if os.path.isfile(text):
                if text.endswith('.sublime-project') and not \
                        self.settings.get('open_project_as_file'):
                    self.window.run_command("load_project", {'file': text})
                else:
                    view = self.window.open_file(text)
                    self.window.focus_view(view)
            elif os.path.isdir(text):
                self.window.run_command("add_folder", {'folder': text})
            else:
                dirname = os.path.dirname(text)
                if os.path.isdir(dirname):
                    self.window.open_file(text)
                else:
                    if not self.settings.get('auto_create_dir', False):
                        self.set_error("directory {0} \
                            does not exist".format(dirname))
                    else:
                        os.makedirs(dirname, 0o755, True)
                        self.window.open_file(text)
        except:
            self.set_error(text)

    def set_error(self, filename, msg=''):
        if not self.current_view:
            return
        status = "Could not open '{0}'".format(filename)
        if msg:
            status += ': {0}'.format(msg)
        self.current_view.set_status("open_file_error", status)
        sublime.set_timeout(lambda: self.current_view.erase_status("open_file_error"), 3000)

    def on_change(self, text):
        if not text:
            return
        if text.endswith('\t'):
            self.input_panel.run_command('move_to', {
                'extend': False,
                'to': 'hardeol'
            })
            self.input_panel.run_command('delete_left')
            self.make_quick_panel(text.strip())

    def make_quick_panel(self, path):
        self.path = path
        self.files = self.get_files(path)
        # not working without timeout
        sublime.set_timeout(lambda: self.window.show_quick_panel(self.files, self.update_path, sublime.MONOSPACE_FONT, 0, self.show_file_preview), 1)

    def show_file_preview(self, index):
        path = os.path.join(self.path, self.files[index])
        if os.path.isfile(path):
            self.previewed = self.window.open_file(path, sublime.TRANSIENT)

    def get_files(self, directory):
        dirname = os.path.dirname(directory)
        basename = os.path.basename(directory).strip()
        files = [f + '/' if os.path.isdir(dirname + '/' + f)
                         else f
                         for f in os.listdir(dirname)
                         if f.startswith(basename) and f != basename]
        if not self.settings.get('auto_complete_hidden_files', True):
            files = [f for f in files if not f.startswith(".")]
        return files

    def update_path(self, index):
        input_region = self.input_panel.full_line(0)
        current_path = self.input_panel.substr(input_region).rstrip('\t')
        current_dir = os.path.dirname(current_path)
        if not current_dir.endswith('/'):
            current_dir += '/'
        if index == -1:
            selected = ''
            if self.previewed is not None and self.previewed != self.current_view:
                self.previewed.close()
                self.previewed = None
        else:
            selected = self.files[index]
        if selected:
            current_path = current_dir + selected
        if os.path.isfile(current_path) and \
                self.settings.get('open_file_on_complete', False):
            self.on_done(current_path)
            self.window.run_command("hide_panel")
        else:
            self.input_panel.run_command('cut')
            self.input_panel.run_command('append', {
                'characters': current_path
            })
            self.window.focus_view(self.input_panel)
            if index != -1 and self.settings.get('show_next_autocomplete', True):
                self.make_quick_panel(current_path)

        self.input_panel.run_command('move_to', {
            'extend': False,
            'to': 'hardeol'
        })


class GetConfirmationCommand(sublime_plugin.WindowCommand):
    def run(self, caption="Confirm", on_yes=None, on_no=None, on_cancel=None):
        self.caption = caption + " (Y/N): "
        self.on_yes = on_yes
        self.on_no = on_no
        self.on_cancel = on_cancel
        self.input_panel = self.window.show_input_panel(self.caption,
                                        "", None, self.on_change, None)

    def reset_input(self):
        input_region = self.input_panel.full_line(0)
        edit = self.input_panel.begin_edit()
        self.input_panel.replace(edit, input_region, "")
        self.input_panel.end_edit(edit)

    def on_change(self, text):
        if not text:
            return
        elif len(text) != 1 or text not in "yYnN":
            self.reset_input()
        else:
            self.window.run_command("hide_panel")
            if text in "yY" and self.on_yes:
                self.window.run_command(self.on_yes)
            elif text in "nN" and self.on_no:
                self.window.run_command(self.on_no)

    def on_cancel(self):
        if self.on_cancel:
            self.window.run_command(self.on_cancel)
