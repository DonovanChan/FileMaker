import sublime
import sublime_plugin

settings = sublime.load_settings("FileMaker.sublime-settings")


def get_selection(view, select_all=False):
    """ Returns regions of view to operate on
    """
    if select_all and not view.has_non_empty_selection_region():
        selection = [sublime.Region(0, view.size())]
    else:
        selection = view.sel()
    return selection


def change_syntax(self):
    """Changes syntax to JSON if its in plain text
    """
    if "Plain text" in self.view.settings().get('syntax'):
        self.view.set_syntax_file("Packages/FileMaker/FileMaker.tmLanguage")


def quote(text):
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    text = text.replace('¶', '\\¶')
    return '"' + text + '"'


class QuoteCommand(sublime_plugin.TextCommand):
    """ Quotes calculation as FileMaker string, escaping as necessary
    """
    def run(self, edit):
        view = self.view
        select_all = settings.get("use_entire_file_if_no_selection", True)
        selection = get_selection(view, select_all)
        for sel in selection:
            view.replace(edit, sel, quote(view.substr(sel)))

        if select_all:
            self.change_syntax()
