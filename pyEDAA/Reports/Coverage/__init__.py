from pyTooling.Decorators import export


@export
class Base:
	_coverage: float



@export
class Directory(Base):
	pass


@export
class File(Base):
	pass


@export
class Hierarchy(Base):
	pass


@export
class Entity(Base):
	pass


@export
class Line(Base):
	pass


@export
class Statement(Base):
	pass


@export
class Branch(Base):
	pass


@export
class Expression(Base):
	pass


@export
class Statemachine(Entity):
	pass


@export
class State(Base):
	pass


@export
class Transition(Base):
	pass


@export
class CoverageBin:
	pass


@export
class ItemBin(CoverageBin):
	pass


@export
class RangeBin(CoverageBin):
	pass


@export
class Dimension:
	pass


@export
class CoverageModel:
	pass
