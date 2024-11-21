from pyTooling.Decorators import export

from pyEDAA.Reports import Severity


@export
class Entry:
	_severity: Severity
	_message: str
