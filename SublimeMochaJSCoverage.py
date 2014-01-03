import os
import sys
import json
import fnmatch

import sublime
import sublime_plugin

debug = lambda *args: sys.stdout.write("\n%s" % " ".join(map(str, args)))

COVERAGE_FILENAME = 'coverage.json'
REGION_KEY = 'SublimeMochaJSCoverage'

class DetectSublimeFileChange(sublime_plugin.EventListener):
  def on_load_async(self, view):
    renderCoverage(self, view)

def read_coverage_report(file_path):
  with open(file_path, 'r') as coverage_file:
    try:
      coverage_json = json.load(coverage_file)
      return coverage_json
    except IOError:
      return None

def renderCoverage(self, view):
  # get name of currently opened file
  filename = view.file_name()

  if not filename:
    return

  project_root = view.window().project_data().get("folders")[0].get("path");

  relative_filename = filename.replace(project_root + "/", "")
  coverage_path = os.path.join(project_root, COVERAGE_FILENAME)

  debug("Display js coverage report for file", filename)
  debug("project_root", project_root)
  debug("relative_filename", relative_filename)
  debug("coverage_filename", coverage_path)

  # Clean up
  view.erase_status("SublimeMochaJSCoverage")
  view.erase_regions("SublimeMochaJSCoverage")

  outlines = []

  report = read_coverage_report(coverage_path)

  if report is None:
    if view.window():
      sublime.status_message(
        "Can't read coverage report from file: " + str(coverage_path))

    return

  if not report:
    view.set_status("SublimeMochaJSCoverage", "UNCOVERED!")
    if view.window():
      sublime.status_message(
        "Can't find the coverage json file in project root: " + project_root)

  coverage_files = {}

  for f in report.get("files"):
    coverage_files[f.get("filename")] = f

  coverage_file = coverage_files.get(relative_filename)
  
  if coverage_file:
    if view.window():
      sublime.status_message("Found coverage data in " + COVERAGE_FILENAME)

    debug("Found test report for file " + str(relative_filename))
    lines = coverage_file.get("source")
    for num in lines:
      coverage = lines.get(num).get("coverage")
      if coverage == 0:
        region = view.full_line(view.text_point(int(num), 0))
        outlines.append(region)
  else:
    if view.window():
      sublime.status_message("Cannot find coverage data in " + COVERAGE_FILENAME)

  # update highlighted regions
  if outlines:
    view.add_regions(REGION_KEY, outlines, 'invalid.illegal', 'circle')

class ShowMochaJsCoverageCommand(sublime_plugin.TextCommand):

  """
    Highlight uncovered lines in the current file
    based on a previous coverage run.
  """

  def run(self, edit):
    view = self.view
    renderCoverage(self, view)

class ClearMochaJsCoverageCommand(sublime_plugin.TextCommand):

  """
    Remove highlights created by plugin.
  """

  def run(self, edit):
    view = self.view
    view.erase_regions(REGION_KEY)
