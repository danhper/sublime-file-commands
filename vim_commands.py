import sublime
import sublime_plugin

class WindowCommandExtension(sublime_plugin.WindowCommand):
  def close_if_no_file(self):
    if not self.window.views():
      self.window.run_command("close_window")

class SaveQuit(WindowCommandExtension):
  def run(self):
    v = self.window.active_view()
    if not v:
      return
    if v.is_dirty():
      v.run_command("save")
    self.window.run_command("close_file")
    self.close_if_no_file()

class ForceQuit(WindowCommandExtension):
  def run(self):
    v = self.window.active_view()
    if not v:
      return
    if v.is_dirty():
      if v.file_name():
        v.run_command("revert")
      else:
        v.set_scratch(True)
    self.window.run_command("close_file")
    self.close_if_no_file()

class Quit(WindowCommandExtension):
  def run(self):
    v = self.window.active_view()
    if not v:
      return
    self.window.run_command("close_file")
    self.close_if_no_file()
