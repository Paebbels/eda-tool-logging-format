# ==================================================================================================================== #
#              _____ ____    _        _      ____                       _                                              #
#  _ __  _   _| ____|  _ \  / \      / \    |  _ \ ___ _ __   ___  _ __| |_ ___                                        #
# | '_ \| | | |  _| | | | |/ _ \    / _ \   | |_) / _ \ '_ \ / _ \| '__| __/ __|                                       #
# | |_) | |_| | |___| |_| / ___ \  / ___ \ _|  _ <  __/ |_) | (_) | |  | |_\__ \                                       #
# | .__/ \__, |_____|____/_/   \_\/_/   \_(_)_| \_\___| .__/ \___/|_|   \__|___/                                       #
# |_|    |___/                                        |_|                                                              #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2024-2024 Electronic Design Automation Abstraction (EDA²)                                                  #
# Copyright 2023-2023 Patrick Lehmann - Bötzingen, Germany                                                             #
#                                                                                                                      #
# Licensed under the Apache License, Version 2.0 (the "License");                                                      #
# you may not use this file except in compliance with the License.                                                     #
# You may obtain a copy of the License at                                                                              #
#                                                                                                                      #
#   http://www.apache.org/licenses/LICENSE-2.0                                                                         #
#                                                                                                                      #
# Unless required by applicable law or agreed to in writing, software                                                  #
# distributed under the License is distributed on an "AS IS" BASIS,                                                    #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                             #
# See the License for the specific language governing permissions and                                                  #
# limitations under the License.                                                                                       #
#                                                                                                                      #
# SPDX-License-Identifier: Apache-2.0                                                                                  #
# ==================================================================================================================== #
#
"""
Reader for JUnit unit testing summary files in XML format.
"""
from datetime        import datetime, timedelta
from enum            import Flag
from pathlib         import Path
from time            import perf_counter_ns
from typing          import Optional as Nullable, Iterable, Dict, Any, Generator, Tuple, Generic, Union, TypeVar

from lxml.etree                 import XMLParser, parse, XMLSchema, XMLSyntaxError, _ElementTree, _Element, _Comment
from lxml.etree                 import ElementTree, Element, SubElement, tostring
from pyTooling.Decorators       import export, readonly
from pyTooling.MetaClasses      import ExtendedType, mustoverride
from pyTooling.Tree             import Node

from pyEDAA.Reports             import resources, getResourceFile
from pyEDAA.Reports.Unittesting import UnittestException, DuplicateTestsuiteException, DuplicateTestcaseException
from pyEDAA.Reports.Unittesting import TestcaseStatus, TestsuiteStatus, IterationScheme
from pyEDAA.Reports.Unittesting import Document as ut_Document


@export
class JUnitException:
	pass


@export
class UnittestException(UnittestException, JUnitException):
	pass


@export
class DuplicateTestsuiteException(DuplicateTestsuiteException, JUnitException):
	pass


@export
class DuplicateTestcaseException(DuplicateTestcaseException, JUnitException):
	pass


@export
class JUnitReaderMode(Flag):
	Default = 0
	DecoupleTestsuiteHierarchyAndTestcaseClassName = 1


TestsuiteType = TypeVar("TestsuiteType", bound="Testsuite")
TestcaseAggregateReturnType = Tuple[int, int, int]
TestsuiteAggregateReturnType = Tuple[int, int, int, int, int]


@export
class Base(metaclass=ExtendedType, slots=True):
	_parent:         Nullable["Testsuite"]
	_name:           str
	_duration:       Nullable[timedelta]
	_assertionCount: Nullable[int]
	_dict:           Dict[str, Any]

	def __init__(self, name: str, duration: Nullable[timedelta] = None, assertionCount: Nullable[int] = None, parent: Nullable["Testsuite"] = None):
		if name is None:
			raise ValueError(f"Parameter 'name' is None.")
		elif not isinstance(name, str):
			raise TypeError(f"Parameter 'name' is not of type 'str'.")

		# TODO: check parameter duration
		# TODO: check parameter parent

		self._parent = parent
		self._name = name
		self._duration = duration
		self._assertionCount = assertionCount

		self._dict = {}

	@readonly
	def Parent(self) -> Nullable["Testsuite"]:
		return self._parent

	# QUESTION: allow Parent as setter?

	@readonly
	def Name(self) -> str:
		return self._name

	@readonly
	def Duration(self) -> timedelta:
		return self._duration

	@readonly
	def AssertionCount(self) -> int:
		return self._assertionCount

	def __len__(self) -> int:
		return len(self._dict)

	def __getitem__(self, key: str) -> Any:
		return self._dict[key]

	def __setitem__(self, key: str, value: Any) -> None:
		self._dict[key] = value

	def __delitem__(self, key: str) -> None:
		del self._dict[key]

	def __contains__(self, key: str) -> bool:
		return key in self._dict

	def __iter__(self) -> Generator[Tuple[str, Any], None, None]:
		yield from self._dict.items()


@export
class Testcase(Base):
	_classname:      str
	_status:         TestcaseStatus

	def __init__(
		self,
		name: str,
		classname: str,
		# startTime: Nullable[datetime] = None,
		duration:  Nullable[timedelta] = None,
		status: TestcaseStatus = TestcaseStatus.Unknown,
		assertionCount: Nullable[int] = None,
		parent: Nullable["Testsuite"] = None
	):
		if parent is not None:
			if not isinstance(parent, Testsuite):
				raise TypeError(f"Parameter 'parent' is not of type 'Testsuite'.")

			parent._testcases[name] = self

		super().__init__(name, duration, assertionCount, parent)

		self._classname = classname
		self._status = status

	@readonly
	def Classname(self) -> str:
		return self._classname

	@readonly
	def Status(self) -> TestcaseStatus:
		return self._status

	def Copy(self) -> "Testcase":
		return self.__class__(
			self._name,
			None,
			self._duration,
			self._status,
			self._assertionCount
		)

	def Aggregate(self, strict: bool = True) -> None:  # TestcaseAggregateReturnType:
		if self._status is TestcaseStatus.Unknown:
			if self._assertionCount is None:
				self._status = TestcaseStatus.Passed
			elif self._assertionCount == 0:
				self._status = TestcaseStatus.Weak
			elif self._failedAssertionCount == 0:
				self._status = TestcaseStatus.Passed
			else:
				self._status = TestcaseStatus.Failed

				if strict:
					self._status = self._status & ~TestcaseStatus.Passed | TestcaseStatus.Failed

			# TODO: check for setup errors
			# TODO: check for teardown errors

		# return 0, 0, 0

	def __str__(self) -> str:
		return (
			f"<JUnit.Testcase {self._name}: {self._status.name} - {self._assertionCount}>"
			# f" assert/pass/fail:{self._assertionCount}/{self._passedAssertionCount}/{self._failedAssertionCount}>"
		)


@export
class TestsuiteBase(Base):
	_startTime: Nullable[datetime]
	_status:    TestsuiteStatus

	_tests:     int
	_skipped:   int
	_errored:   int
	_failed:    int
	_passed:    int

	def __init__(
		self,
		name: str,
		startTime: Nullable[datetime] = None,
		duration:  Nullable[timedelta] = None,
		status: TestsuiteStatus = TestsuiteStatus.Unknown,
		parent: Nullable["Testsuite"] = None
	):
		super().__init__(name, duration, None, parent)

		self._startTime = startTime
		self._status = status
		self._tests =        0
		self._skipped =      0
		self._errored =      0
		self._failed =       0
		self._passed =       0

	@readonly
	def StartTime(self) -> Nullable[datetime]:
		return self._startTime

	@readonly
	def Status(self) -> TestsuiteStatus:
		return self._status

	@readonly
	@mustoverride
	def TestcaseCount(self) -> int:
		pass

	@readonly
	def Tests(self) -> int:
		return self.TestcaseCount

	# @readonly
	# def AssertionCount(self) -> int:
	# 	raise NotImplementedError()
	# 	# return self._assertionCount

	@readonly
	def FailedAssertionCount(self) -> int:
		raise NotImplementedError()
		# return self._assertionCount - (self._warningCount + self._errorCount + self._fatalCount)

	@readonly
	def PassedAssertionCount(self) -> int:
		raise NotImplementedError()
		# return self._assertionCount - (self._warningCount + self._errorCount + self._fatalCount)

	@readonly
	def Skipped(self) -> int:
		return self._skipped

	@readonly
	def Errored(self) -> int:
		return self._errored

	@readonly
	def Failed(self) -> int:
		return self._failed

	@readonly
	def Passed(self) -> int:
		return self._passed

	def Aggregate(self) -> TestsuiteAggregateReturnType:
		tests = 0
		skipped = 0
		errored = 0
		failed = 0
		passed = 0

		# for testsuite in self._testsuites.values():
		# 	t, s, e, w, f, p = testsuite.Aggregate()
		# 	tests += t
		# 	skipped += s
		# 	errored += e
		# 	weak += w
		# 	failed += f
		# 	passed += p

		return tests, skipped, errored, failed, passed

	@mustoverride
	def Iterate(self, scheme: IterationScheme = IterationScheme.Default) -> Generator[Union[TestsuiteType, Testcase], None, None]:
		pass


@export
class Testsuite(TestsuiteBase):
	_hostname:  str
	_testcases: Dict[str, "Testcase"]

	def __init__(
		self,
		name: str,
		hostname: str,
		startTime: Nullable[datetime] = None,
		duration:  Nullable[timedelta] = None,
		status: TestsuiteStatus = TestsuiteStatus.Unknown,
		testcases: Nullable[Iterable["Testcase"]] = None,
		parent: Nullable["TestsuiteSummary"] = None
	):
		if parent is not None:
			if not isinstance(parent, TestsuiteSummary):
				raise TypeError(f"Parameter 'parent' is not of type 'TestsuiteSummary'.")

			parent._testsuites[name] = self

		super().__init__(name, startTime, duration, status, parent)

		self._hostname = hostname

		self._testcases = {}
		if testcases is not None:
			for testcase in testcases:
				if testcase._parent is not None:
					raise ValueError(f"Testcase '{testcase._name}' is already part of a testsuite hierarchy.")

				if testcase._name in self._testcases:
					raise DuplicateTestcaseException(f"Testsuite already contains a testcase with same name '{testcase._name}'.")

				testcase._parent = self
				self._testcases[testcase._name] = testcase

	@readonly
	def Hostname(self) -> str:
		return self._hostname

	@readonly
	def Testcases(self) -> Dict[str, "Testcase"]:
		return self._testcases

	@readonly
	def TestcaseCount(self) -> int:
		return len(self._testcases)

	def AddTestcase(self, testcase: "Testcase") -> None:
		if testcase._parent is not None:
			raise ValueError(f"Testcase '{testcase._name}' is already part of a testsuite hierarchy.")

		if testcase._name in self._testcases:
			raise DuplicateTestcaseException(f"Testsuite already contains a testcase with same name '{testcase._name}'.")

		testcase._parent = self
		self._testcases[testcase._name] = testcase

	def AddTestcases(self, testcases: Iterable["Testcase"]) -> None:
		for testcase in testcases:
			self.AddTestcase(testcase)

	# def IterateTestsuites(self, scheme: IterationScheme = IterationScheme.TestsuiteDefault) -> Generator[TestsuiteType, None, None]:
	# 	return self.Iterate(scheme)

	def IterateTestcases(self, scheme: IterationScheme = IterationScheme.TestcaseDefault) -> Generator[Testcase, None, None]:
		return self.Iterate(scheme)

	def ToTree(self) -> Node:
		rootNode = Node(value=self._name)

		def convertTestcase(testcase: Testcase, parentNode: Node) -> None:
			_ = Node(value=testcase._name, parent=parentNode)

		def convertTestsuite(testsuite: Testsuite, parentNode: Node) -> None:
			testsuiteNode = Node(value=testsuite._name, parent=parentNode)

			for ts in testsuite._testsuites.values():
				convertTestsuite(ts, testsuiteNode)

			for tc in testsuite._testcases.values():
				convertTestcase(tc, testsuiteNode)

		for testsuite in self._testsuites.values():
			convertTestsuite(testsuite, rootNode)

		return rootNode

	def Copy(self) -> "Testsuite":
		return self.__class__(
			self._name,
			self._hostname,
			self._startTime,
			self._duration,
			self._status
		)

	def Aggregate(self, strict: bool = True) -> TestsuiteAggregateReturnType:
		tests, skipped, errored, failed, passed = super().Aggregate()

		for testcase in self._testcases.values():
			_ = testcase.Aggregate(strict)

			tests += 1

			status = testcase._status
			if status is TestcaseStatus.Unknown:
				raise UnittestException(f"Found testcase '{testcase._name}' with state 'Unknown'.")
			elif status is TestcaseStatus.Skipped:
				skipped += 1
			elif status is TestcaseStatus.Errored:
				errored += 1
			elif status is TestcaseStatus.Passed:
				passed += 1
			elif status is TestcaseStatus.Failed:
				failed += 1
			elif status & TestcaseStatus.Mask is not TestcaseStatus.Unknown:
				raise UnittestException(f"Found testcase '{testcase._name}' with unsupported state '{status}'.")
			else:
				raise UnittestException(f"Internal error for testcase '{testcase._name}', field '_status' is '{status}'.")

		self._tests = tests
		self._skipped = skipped
		self._errored = errored
		self._failed = failed
		self._passed = passed

		if errored > 0:
			self._status = TestsuiteStatus.Errored
		elif failed > 0:
			self._status = TestsuiteStatus.Failed
		elif tests == 0:
			self._status = TestsuiteStatus.Empty
		elif tests - skipped == passed:
			self._status = TestsuiteStatus.Passed
		elif tests == skipped:
			self._status = TestsuiteStatus.Skipped
		else:
			self._status = TestsuiteStatus.Unknown

		return tests, skipped, errored, failed, passed

	def Iterate(self, scheme: IterationScheme = IterationScheme.Default) -> Generator[Union[TestsuiteType, Testcase], None, None]:
		assert IterationScheme.PreOrder | IterationScheme.PostOrder not in scheme

		if IterationScheme.PreOrder in scheme:
			if IterationScheme.IncludeSelf | IterationScheme.IncludeTestsuites in scheme:
				yield self

			if IterationScheme.IncludeTestcases in scheme:
				for testcase in self._testcases.values():
					yield testcase

		for testsuite in self._testsuites.values():
			yield from testsuite.Iterate(scheme | IterationScheme.IncludeSelf)

		if IterationScheme.PostOrder in scheme:
			if IterationScheme.IncludeTestcases in scheme:
				for testcase in self._testcases.values():
					yield testcase

			if IterationScheme.IncludeSelf | IterationScheme.IncludeTestsuites in scheme:
				yield self

	def __str__(self) -> str:
		return (
			f"<JUnit.Testsuite {self._name}: {self._status.name} - {self._tests}>"
			# f" assert/pass/fail:{self._assertionCount}/{self._passedAssertionCount}/{self._failedAssertionCount} -"
			# f" warn/error/fatal:{self._warningCount}/{self._errorCount}/{self._fatalCount}>"
		)


@export
class TestsuiteSummary(TestsuiteBase):
	_testsuites: Dict[str, Testsuite]

	def __init__(
		self,
		name: str,
		startTime: Nullable[datetime] = None,
		duration:  Nullable[timedelta] = None,
		status: TestsuiteStatus = TestsuiteStatus.Unknown,
		testsuites: Nullable[Iterable[Testsuite]] = None
	):
		super().__init__(name, startTime, duration, status, None)

		self._testsuites = {}
		if testsuites is not None:
			for testsuite in testsuites:
				if testsuite._parent is not None:
					raise ValueError(f"Testsuite '{testsuite._name}' is already part of a testsuite hierarchy.")

				if testsuite._name in self._testsuites:
					raise DuplicateTestsuiteException(f"Testsuite already contains a testsuite with same name '{testsuite._name}'.")

				testsuite._parent = self
				self._testsuites[testsuite._name] = testsuite

	@readonly
	def Testsuites(self) -> Dict[str, Testsuite]:
		return self._testsuites

	@readonly
	def TestcaseCount(self) -> int:
		return sum(testsuite.TestcaseCount for testsuite in self._testsuites.values())

	@readonly
	def TestsuiteCount(self) -> int:
		return len(self._testsuites)

	def AddTestsuite(self, testsuite: Testsuite) -> None:
		if testsuite._parent is not None:
			raise ValueError(f"Testsuite '{testsuite._name}' is already part of a testsuite hierarchy.")

		if testsuite._name in self._testsuites:
			raise DuplicateTestsuiteException(f"Testsuite already contains a testsuite with same name '{testsuite._name}'.")

		testsuite._parent = self
		self._testsuites[testsuite._name] = testsuite

	def AddTestsuites(self, testsuites: Iterable[Testsuite]) -> None:
		for testsuite in testsuites:
			self.AddTestsuite(testsuite)

	def Aggregate(self) -> TestsuiteAggregateReturnType:
		tests, skipped, errored, failed, passed = super().Aggregate()

		self._tests = tests
		self._skipped = skipped
		self._errored = errored
		self._failed = failed
		self._passed = passed

		if errored > 0:
			self._status = TestsuiteStatus.Errored
		elif failed > 0:
			self._status = TestsuiteStatus.Failed
		elif tests == 0:
			self._status = TestsuiteStatus.Empty
		elif tests - skipped == passed:
			self._status = TestsuiteStatus.Passed
		elif tests == skipped:
			self._status = TestsuiteStatus.Skipped
		else:
			self._status = TestsuiteStatus.Unknown

		return tests, skipped, errored, failed, passed

	def Iterate(self, scheme: IterationScheme = IterationScheme.Default) -> Generator[Union[Testsuite, Testcase], None, None]:
		if IterationScheme.IncludeSelf | IterationScheme.IncludeTestsuites | IterationScheme.PreOrder in scheme:
			yield self

		for testsuite in self._testsuites.values():
			yield from testsuite.IterateTestsuites(scheme | IterationScheme.IncludeSelf)

		if IterationScheme.IncludeSelf | IterationScheme.IncludeTestsuites | IterationScheme.PostOrder in scheme:
			yield self

	def __str__(self) -> str:
		return (
			f"<JUnit.TestsuiteSummary {self._name}: {self._status.name} - {self._tests}>"
			# f" assert/pass/fail:{self._assertionCount}/{self._passedAssertionCount}/{self._failedAssertionCount} -"
			# f" warn/error/fatal:{self._warningCount}/{self._errorCount}/{self._fatalCount}>"
		)


@export
class JUnitDocument(TestsuiteSummary, ut_Document):
	_readerMode:       JUnitReaderMode
	_xmlDocument:      Nullable[_ElementTree]

	def __init__(self, xmlReportFile: Path, parse: bool = False, readerMode: JUnitReaderMode = JUnitReaderMode.Default):
		super().__init__("Unprocessed JUnit XML file")
		ut_Document.__init__(self, xmlReportFile)

		self._readerMode = readerMode
		self._xmlDocument = None

		if parse:
			self.Read()
			self.Parse()

	@classmethod
	def FromTestsuiteSummary(cls, xmlReportFile: Path, testsuiteSummary: TestsuiteSummary):
		doc = cls(xmlReportFile)
		doc._name = testsuiteSummary._name
		doc._startTime = testsuiteSummary._startTime
		doc._totalDuration = testsuiteSummary._duration
		doc._status = testsuiteSummary._status
		doc._tests = testsuiteSummary._tests
		doc._skipped = testsuiteSummary._skipped
		doc._errored = testsuiteSummary._errored
		doc._failed = testsuiteSummary._failed
		doc._passed = testsuiteSummary._passed

		for name, testsuite in testsuiteSummary._testsuites.items():
			doc._testsuites[name] = testsuite
			testsuite._parent = doc

		return doc

	def Read(self) -> None:
		if not self._path.exists():
			raise UnittestException(f"JUnit XML file '{self._path}' does not exist.") \
				from FileNotFoundError(f"File '{self._path}' not found.")

		startAnalysis = perf_counter_ns()
		try:
			# xmlSchemaFile = getResourceFile(resources, "JUnit.xsd")
			xmlSchemaFile = getResourceFile(resources, "Unittesting.xsd")
			schemaParser = XMLParser(ns_clean=True)
			schemaRoot = parse(xmlSchemaFile, schemaParser)

			junitSchema = XMLSchema(schemaRoot)
			junitParser = XMLParser(schema=junitSchema, ns_clean=True)
			junitDocument = parse(self._path, parser=junitParser)

			self._xmlDocument = junitDocument
		except XMLSyntaxError as ex:
			print(ex)

			print(junitParser.error_log)
		except Exception as ex:
			raise UnittestException(f"Couldn't open '{self._path}'.") from ex

		endAnalysis = perf_counter_ns()
		self._analysisDuration = (endAnalysis - startAnalysis) / 1e9

	def Write(self, path: Nullable[Path] = None, overwrite: bool = False, regenerate: bool = False) -> None:
		if path is None:
			path = self._path

		if not overwrite and path.exists():
			raise UnittestException(f"JUnit XML file '{path}' can not be written.") \
				from FileExistsError(f"File '{path}' already exists.")

		if regenerate:
			self.Generate(overwrite=True)

		if self._xmlDocument is None:
			ex = UnittestException(f"Internal XML document tree is empty and needs to be generated before write is possible.")
			ex.add_note(f"Call 'JUnitDocument.Generate()' or 'JUnitDocument.Write(..., regenerate=True)'.")
			raise ex

		with path.open("wb") as file:
			file.write(tostring(self._xmlDocument, encoding="utf-8", xml_declaration=True, pretty_print=True))

	def Parse(self) -> None:
		if self._xmlDocument is None:
			ex = UnittestException(f"JUnit XML file '{self._path}' needs to be read and analyzed by an XML parser.")
			ex.add_note(f"Call 'JUnitDocument.Read()' or create document using 'JUnitDocument(path, parse=True)'.")
			raise ex

		startConversion = perf_counter_ns()
		rootElement: _Element = self._xmlDocument.getroot()

		self._name =      rootElement.attrib["name"]                              if "name"      in rootElement.attrib else "root"
		self._startTime = datetime.fromisoformat(rootElement.attrib["timestamp"]) if "timestamp" in rootElement.attrib else None
		self._duration =  timedelta(seconds=float(rootElement.attrib["time"]))    if "time"      in rootElement.attrib else None

		# tests = rootElement.getAttribute("tests")
		# skipped = rootElement.getAttribute("skipped")
		# errors = rootElement.getAttribute("errors")
		# failures = rootElement.getAttribute("failures")
		# assertions = rootElement.getAttribute("assertions")

		for rootNode in rootElement.iterchildren(tag="testsuite"):  # type: _Element
			self._ParseTestsuite(self, rootNode)

		self.Aggregate()
		endConversation = perf_counter_ns()
		self._modelConversion = (endConversation - startConversion) / 1e9

	def _ParseTestsuite(self, parent: TestsuiteSummary, testsuitesNode: _Element) -> None:
		name = testsuitesNode.attrib["name"]

		kwargs = {}
		if "timestamp" in testsuitesNode.attrib:
			kwargs["startTime"] = datetime.fromisoformat(testsuitesNode.attrib["timestamp"])
		if "time" in testsuitesNode.attrib:
			kwargs["duration"] = timedelta(seconds=float(testsuitesNode.attrib["time"]))
		if "hostname" in testsuitesNode.attrib:
			kwargs["hostname"] = testsuitesNode.attrib["hostname"]

		newTestsuite = Testsuite(
			name,
			**kwargs,
			parent=parent
		)

		# if self._readerMode is JUnitReaderMode.Default:
		# 	currentTestsuite = parent
		# elif self._readerMode is JUnitReaderMode.DecoupleTestsuiteHierarchyAndTestcaseClassName:
		# 	currentTestsuite = newTestsuite
		# else:
		# 	raise UnittestException(f"Unknown reader mode '{self._readerMode}'.")

		for node in testsuitesNode.iterchildren():   # type: _Element
			if node.tag == "testsuite":
				self._ParseTestsuite(newTestsuite, node)
			elif node.tag == "testcase":
				self._ParseTestcase(newTestsuite, node)

	def _ParseTestcase(self, parent: Testsuite, testsuiteNode: _Element) -> None:
		name = testsuiteNode.attrib["name"]
		className = testsuiteNode.attrib["classname"]
		time = float(testsuiteNode.attrib["time"])

		# if self._readerMode is JUnitReaderMode.Default:
		# 	currentTestsuite = self
		# elif self._readerMode is JUnitReaderMode.DecoupleTestsuiteHierarchyAndTestcaseClassName:
		# 	currentTestsuite = parentTestsuite
		# else:
		# 	raise UnittestException(f"Unknown reader mode '{self._readerMode}'.")

		# testsuitePath = className.split(".")
		# for testsuiteName in testsuitePath:
		# 	try:
		# 		currentTestsuite = currentTestsuite._testsuites[testsuiteName]
		# 	except KeyError:
		# 		currentTestsuite._testsuites[testsuiteName] = new = Testsuite(testsuiteName)
		# 		currentTestsuite = new

		testcase = Testcase(name, className, duration=timedelta(seconds=time), parent=parent)

		for node in testsuiteNode.iterchildren():   # type: _Element
			if isinstance(node, _Comment):
				pass
			elif isinstance(node, _Element):
				if node.tag == "skipped":
					testcase._status = TestcaseStatus.Skipped
				elif node.tag == "failure":
					testcase._status = TestcaseStatus.Failed
				elif node.tag == "error":
					testcase._status = TestcaseStatus.Errored
				elif node.tag == "system-out":
					pass
				elif node.tag == "system-err":
					pass
				elif node.tag == "properties":
					pass
				else:
					raise UnittestException(f"Unknown element '{node.tag}' in junit file.")
			else:
				pass

		if testcase._status is TestcaseStatus.Unknown:
			testcase._status = TestcaseStatus.Passed

	def Generate(self, overwrite: bool = False) -> None:
		if self._xmlDocument is not None:
			raise UnittestException(f"Internal XML document is populated with data.")

		rootElement = Element("testsuites")
		rootElement.attrib["name"] = self._name
		if self._startTime is not None:
			rootElement.attrib["timestamp"] = f"{self._startTime.isoformat()}"
		if self._duration is not None:
			rootElement.attrib["time"] = f"{self._duration.total_seconds():.6f}"
		rootElement.attrib["tests"] = str(self._tests)
		rootElement.attrib["failures"] = str(self._failed)
		rootElement.attrib["errors"] = str(self._errored)
		rootElement.attrib["skipped"] = str(self._skipped)
		# if self._assertionCount is not None:
		# 	rootElement.attrib["assertions"] = f"{self._assertionCount}"

		self._xmlDocument = ElementTree(rootElement)

		for testsuite in self._testsuites.values():
			self._GenerateTestsuite(testsuite, rootElement)

	def _GenerateTestsuite(self, testsuite: Testsuite, parentElement: _Element):
		testsuiteElement = SubElement(parentElement, "testsuite")
		testsuiteElement.attrib["name"] = testsuite._name
		if testsuite._startTime is not None:
			testsuiteElement.attrib["timestamp"] = f"{testsuite._startTime.isoformat()}"
		if testsuite._duration is not None:
			testsuiteElement.attrib["time"] = f"{testsuite._duration.total_seconds():.6f}"
		testsuiteElement.attrib["tests"] = str(testsuite._tests)
		testsuiteElement.attrib["failures"] = str(testsuite._failed)
		testsuiteElement.attrib["errors"] = str(testsuite._errored)
		testsuiteElement.attrib["skipped"] = str(testsuite._skipped)
		# if testsuite._assertionCount is not None:
		# 	testsuiteElement.attrib["assertions"] = f"{testsuite._assertionCount}"
		if testsuite._hostname is not None:
			testsuiteElement.attrib["hostname"] = testsuite._hostname

		for tc in testsuite._testcases.values():
			self._GenerateTestcase(tc, testsuiteElement)

	def _GenerateTestcase(self, testcase: Testcase, parentElement: _Element):
		testcaseElement = SubElement(parentElement, "testcase")
		testcaseElement.attrib["name"] = testcase._name
		if testcase._classname is not None:
			testcaseElement.attrib["classname"] = testcase._classname
		if testcase._duration is not None:
			testcaseElement.attrib["time"] = f"{testcase._duration.total_seconds():.6f}"
		if testcase._assertionCount is not None:
			testcaseElement.attrib["assertions"] = f"{testcase._assertionCount}"

		if testcase._status is TestcaseStatus.Passed:
			pass
		elif testcase._status is TestcaseStatus.Failed:
			failureElement = SubElement(testcaseElement, "failure")
		elif testcase._status is TestcaseStatus.Skipped:
			skippedElement = SubElement(testcaseElement, "skipped")
		else:
			errorElement = SubElement(testcaseElement, "error")
