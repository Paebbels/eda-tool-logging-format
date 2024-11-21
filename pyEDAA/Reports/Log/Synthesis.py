from typing import List

from pyTooling.Decorators import export
from pyEDAA.ProjectModel  import File

from pyEDAA.Reports.Log import Entry as Log_Entry


@export
class SourceCodePosition:
	"""
	Represents a position in a source code file as a ragged 2 dimensional ``Row``:``Column`` position.
	"""

	Row       : int    #: Row or line in the document
	Column    : int    #: Column in the document

	def __init__(self, row : int, column : int):
		self.Row =       row
		self.Column =    column

	def __str__(self):
		"""Returns a string representation."""
		return "(line: {0}, col: {1})".format(self.Row, self.Column)

	def __repr__(self):
		"""Returns a string representation in ``row:col`` format."""
		return "{0}:{1})".format(self.Row, self.Column)


@export
class Entry(Log_Entry):
	_file: File
	_position: SourceCodePosition
	_codeObject: str
	_linkedEntries: List["Entry"]
