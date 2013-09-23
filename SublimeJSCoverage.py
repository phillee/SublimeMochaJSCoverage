import os
import sys
import sublime
import sublime_plugin
import json

debug = lambda *args: sys.stdout.write("\n%s" % " ".join(args))

def find_project_root(file_path):
	"""Project Root is defined as the parent directory that contains a directory called 'coverage'"""
	if os.access(os.path.join(file_path, 'coverage'), os.R_OK):
		return file_path
	parent, current = os.path.split(file_path)
	if current:
		return find_project_root(parent)


def find_coverage_filename(project_root, file_path):
	"""
		Returns coverage json for specifed file or None if cannot find it
		file_path
	"""
	parts = file_path.split("/")
	dirname = parts[0]
	coverage_filepath = os.path.join(project_root, 'coverage', '%s.json' % dirname)
	debug("coverage_filepath to look up ", coverage_filepath)
	if os.access(coverage_filepath, os.R_OK):
		return coverage_filepath

class ShowJsCoverageCommand(sublime_plugin.TextCommand):
	"""
		Highlight uncovered lines in the current file 
		based on a previous coverage run.
	"""
	def run(self, edit):
		view = self.view
		filename = view.file_name()
		if not filename:
			return
		project_root = find_project_root(filename)

		if not project_root:
			if view.window():
				sublime.status_message("Could not find coverage directory")
			return

		relative_filename = filename.replace(project_root + "/", "")
		coverage_filepath = find_coverage_filename(project_root, relative_filename)

		debug("Display js coverage report for file", filename)
		debug("project_root", project_root)
		debug("relative_filename", relative_filename)
		debug("coverage_filepath", coverage_filepath)

		parts = relative_filename.split("/")
		dirname = parts[0]
		relative_filename = relative_filename.replace(dirname + "/", "")

		debug("relative_filename2", relative_filename)

		if not coverage_filepath:
			if view.window():
				sublime.status_message("Can't find the coverage file " + str(coverage_filepath))
			return

		# Clean up
		view.erase_status("SublimeJSCoverage")
		view.erase_regions("SublimeJSCoverage")

		outlines = []
		try:
			coverage_json = json.load(open(coverage_filepath, 'r'))
		except IOError:
			view.set_status("SublimeJSCoverage", "UNCOVERED!")
			if view.window():
				sublime.status_message("Can't find the coverage json file " + coverage_filepath)


		for f in coverage_json.get("files"):
			if f.get("filename") == relative_filename:
				sources = f.get("source")
				for line_num in sources:
					coverage = sources[line_num].get('coverage')
					line_num = int(line_num)
					if coverage != '' and int(coverage) != 1:
						region = view.full_line(view.text_point(line_num, 0))
						outlines.append(region)

		# update highlighted regions
		if outlines:
			view.add_regions('SublimeJSCoverage', outlines,
							 'markup.deleted.diff', 'bookmark', sublime.DRAW_OUTLINED)
