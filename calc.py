import sublime
import sublime_plugin
import xml.etree.ElementTree as ET
import xml.sax.saxutils as SAX

settings = sublime.load_settings("FileMaker.sublime-settings")


def get_selection(view, select_all=False):
    """ Returns regions of view to operate on
    """
    if select_all and not view.has_non_empty_selection_region():
        selection = [sublime.Region(0, view.size())]
    else:
        selection = view.sel()
    return selection


def syntax_to_filemaker(self):
    """Changes syntax to FileMaker if its in plain text
    """
    if "Plain text" in self.view.settings().get('syntax'):
        self.view.set_syntax_file("Packages/FileMaker/FileMaker.tmLanguage")

def syntax_to_clipboard(self):
    """Changes syntax to FileMaker Clipboard
    """
    self.view.set_syntax_file("Packages/FileMaker/FileMaker Clipboard.tmLanguage")

def quote(text):
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    text = text.replace('¶', '\\¶')
    return '"' + text + '"'


def quote_and_append(text):
    textNew = ""
    for line in text.splitlines():
        textNew += quote(line) + ' & ¶ &' + "\n"
    return textNew + "\n" + '""'

def extract_table_field_names(text):
    root = ET.fromstring(text)
    textNew = ""
    for elem in root.iterfind('Field'):
      textNew += elem.get('name') + "\n"
    return textNew

def convert_to_script_comments(text):
    template = '<Step enable="True" id="" name="Comment"><Text>{0}</Text></Step>'
    textNew = '<fmxmlsnippet type="FMObjectList">' + "\n"
    for line in text.splitlines():
        lineNew = SAX.escape(line)
        textNew += template.format(' ' + lineNew + "\n")
    textNew += '</fmxmlsnippet>'
    return textNew


class FilemakerQuoteCommand(sublime_plugin.TextCommand):
    """ Quotes calculation as FileMaker string, escaping as necessary
    """
    def run(self, edit):
        view = self.view
        select_all = settings.get("use_entire_file_if_no_selection", True)
        selection = get_selection(view, select_all)
        for sel in selection:
            view.replace(edit, sel, quote(view.substr(sel)))

        if select_all:
            self.syntax_to_filemaker()


class FilemakerQuoteAndAppendCommand(sublime_plugin.TextCommand):
    """ Quotes each line in calculation as FileMaker string, appending each line of text with carriage return
    """
    def run(self, edit):
        view = self.view
        select_all = settings.get("use_entire_file_if_no_selection", True)
        selection = get_selection(view, select_all)
        for sel in selection:
            view.replace(edit, sel, quote_and_append(view.substr(sel)))

        if select_all:
            self.syntax_to_filemaker()

class FilemakerExtractTableFieldNamesCommand(sublime_plugin.TextCommand):
    """ Extracts list of field names from FileMaker clipboard object
    """
    def run(self, edit):
        view = self.view
        select_all = settings.get("use_entire_file_if_no_selection", True)
        selection = get_selection(view, select_all)
        for sel in selection:
            view.replace(edit, sel, extract_table_field_names(view.substr(sel)))

        if select_all:
            extract_table_field_names(view.substr(selection))

class FilemakerConvertToScriptComments(sublime_plugin.TextCommand):
    """ Converts each line of text to a script comment to be pasted into FileMaker
    """
    def run(self, edit):
        view = self.view
        select_all = settings.get("use_entire_file_if_no_selection", True)
        selection = get_selection(view, select_all)
        for sel in selection:
            view.replace(edit, sel, convert_to_script_comments(view.substr(sel)))

        if select_all:
            self.syntax_to_clipboard()
