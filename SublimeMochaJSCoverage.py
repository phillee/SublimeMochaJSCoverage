import os
import sys
import json
import fnmatch

import sublime
import sublime_plugin

debug = lambda *args: sys.stdout.write("\n%s" % " ".join(map(str, args)))

COVERAGE_PATH = 'coverage/coverage.json'
REGION_KEY = 'SublimeMochaJSCoverage'

class DetectSublimeFileChange(sublime_plugin.EventListener):
  def on_load_async(self, view):
    renderCoverage(self, view)

def readCoverageReport(file_path):
  with open(file_path, 'r') as coverageFile:
    try:
      coverage_json = json.load(coverageFile)
      return coverage_json
    except IOError:
      return None

def renderCoverage(self, view):
  # get name of currently opened file
  filename = view.file_name()

  if not filename:
    return

  project_root = view.window().project_data().get("folders")[0].get("path");

  coveragePath = os.path.join(project_root, COVERAGE_PATH)

  debug("Display js coverage report for file", filename)
  debug("coverage_filename", coveragePath)

  # Clean up
  view.erase_status(REGION_KEY)
  view.erase_regions(REGION_KEY)

  outlines = []

  reports = readCoverageReport(coveragePath)

  if reports is None:
    if view.window():
      sublime.status_message(
        "Can't read coverage report from file: " + str(coveragePath))

    return

  if not reports:
    view.set_status("SublimeMochaJSCoverage", "UNCOVERED!")
    if view.window():
      sublime.status_message("Can't find " + COVERAGE_FILENAME + " at " + coveragePath)

  report = reports.get(filename)
  
  if report:
    if view.window():
      sublime.status_message("Found coverage data")

    debug("Found report for " + str(filename))
    for statement, coverage in report["s"].items():
      if coverage == 0:
        statementCoverage = report["statementMap"][statement]
        start = statementCoverage["start"]
        end = statementCoverage["end"]

        # debug("statement" + statement + ", start: " + str(start) + ", end: " + str(end))
        startOffset = view.text_point(start["line"] - 1, start["column"])
        endOffset = view.text_point(end["line"] - 1, end["column"])

        region = sublime.Region(startOffset, endOffset)
        outlines.append(region)
  else:
    if view.window():
      sublime.status_message("No coverage data")

  # update highlighted regions
  if outlines:
    view.add_regions(REGION_KEY, outlines, 'invalid.illegal', 'bookmark')

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
