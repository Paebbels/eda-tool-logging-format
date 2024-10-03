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
from pathlib              import Path
from time                 import perf_counter_ns
from typing               import Optional as Nullable, Generator, Tuple, Union, TypeVar, Type, ClassVar

from lxml.etree           import ElementTree, Element, SubElement, tostring, _Element
from pyTooling.Decorators import export

from pyEDAA.Reports.Unittesting       import UnittestException, TestsuiteKind
from pyEDAA.Reports.Unittesting       import TestcaseStatus, TestsuiteStatus, IterationScheme
from pyEDAA.Reports.Unittesting       import TestsuiteSummary as ut_TestsuiteSummary, Testsuite as ut_Testsuite
from pyEDAA.Reports.Unittesting.JUnit import Testcase as ju_Testcase, Testclass as ju_Testclass, Testsuite as ju_Testsuite
from pyEDAA.Reports.Unittesting.JUnit import TestsuiteSummary as ju_TestsuiteSummary, Document as ju_Document


TestsuiteType = TypeVar("TestsuiteType", bound="Testsuite")
TestcaseAggregateReturnType = Tuple[int, int, int]
TestsuiteAggregateReturnType = Tuple[int, int, int, int, int]


@export
class Testcase(ju_Testcase):
	pass


@export
class Testclass(ju_Testclass):
	pass


@export
class Testsuite(ju_Testsuite):
	def Aggregate(self, strict: bool = True) -> TestsuiteAggregateReturnType:
		tests, skipped, errored, failed, passed = super().Aggregate()

		for testclass in self._testclasses.values():
			_ = testclass.Aggregate(strict)

			tests += 1

			status = testclass._status
			if status is TestcaseStatus.Unknown:
				raise UnittestException(f"Found testclass '{testclass._name}' with state 'Unknown'.")
			elif status is TestcaseStatus.Skipped:
				skipped += 1
			elif status is TestcaseStatus.Errored:
				errored += 1
			elif status is TestcaseStatus.Passed:
				passed += 1
			elif status is TestcaseStatus.Failed:
				failed += 1
			elif status & TestcaseStatus.Mask is not TestcaseStatus.Unknown:
				raise UnittestException(f"Found testclass '{testclass._name}' with unsupported state '{status}'.")
			else:
				raise UnittestException(f"Internal error for testclass '{testclass._name}', field '_status' is '{status}'.")

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

	@classmethod
	def FromTestsuite(cls, testsuite: ut_Testsuite) -> "Testsuite":
		juTestsuite = cls(
			testsuite._name,
			startTime=testsuite._startTime,
			duration=testsuite._totalDuration,
			status= testsuite._status,
		)

		juTestsuite._tests = testsuite._tests
		juTestsuite._skipped = testsuite._skipped
		juTestsuite._errored = testsuite._errored
		juTestsuite._failed = testsuite._failed
		juTestsuite._passed = testsuite._passed

		for tc in testsuite.IterateTestcases():
			ts = tc._parent
			if ts is None:
				raise UnittestException(f"Testcase '{tc._name}' is not part of a hierarchy.")

			classname = ts._name
			ts = ts._parent
			while ts is not None and ts._kind > TestsuiteKind.Logical:
				classname = f"{ts._name}.{classname}"
				ts = ts._parent

			if classname in juTestsuite._testclasses:
				juClass = juTestsuite._testclasses[classname]
			else:
				juClass = Testclass(classname, parent=juTestsuite)

			juClass.AddTestcase(Testcase.FromTestcase(tc))

		return juTestsuite

	def ToTestsuite(self) -> ut_Testsuite:
		testsuite = ut_Testsuite(
			self._name,
			TestsuiteKind.Logical,
			startTime=self._startTime,
			totalDuration=self._duration,
			status=self._status,
		)

		for testclass in self._testclasses.values():
			suite = testsuite
			classpath = testclass._name.split(".")
			for element in classpath:
				if element in suite._testsuites:
					suite = suite._testsuites[element]
				else:
					suite = ut_Testsuite(element, kind=TestsuiteKind.Package, parent=suite)

			suite._kind = TestsuiteKind.Class
			if suite._parent is not testsuite:
				suite._parent._kind = TestsuiteKind.Module

			suite.AddTestcases(tc.ToTestcase() for tc in testclass._testcases.values())

		return testsuite


@export
class TestsuiteSummary(ju_TestsuiteSummary):
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

	@classmethod
	def FromTestsuiteSummary(cls, testsuiteSummary: ut_TestsuiteSummary) -> "TestsuiteSummary":
		return cls(
			testsuiteSummary._name,
			startTime=testsuiteSummary._startTime,
			duration=testsuiteSummary._totalDuration,
			status=testsuiteSummary._status,
			testsuites=(ut_Testsuite.FromTestsuite(testsuite) for testsuite in testsuiteSummary._testsuites.values())
		)

	def ToTestsuiteSummary(self) -> ut_TestsuiteSummary:
		return ut_TestsuiteSummary(
			self._name,
			startTime=self._startTime,
			totalDuration=self._duration,
			status=self._status,
			testsuites=(testsuite.ToTestsuite() for testsuite in self._testsuites.values())
		)


@export
class Document(ju_Document):
	"""
	A document reader and writer for the GoogelTest JUnit XML file format.

	This class reads, validates and transforms an XML file in the GoogelTest JUnit format into a JUnit data model. It can
	then be converted into a unified test entity data model.

	In reverse, a JUnit data model instance with the specific GoogelTest JUnit file format can be created from a unified
	test entity data model. This data model can be written as XML into a file.
	"""

	_TESTCASE:  ClassVar[Type[Testcase]] =  Testcase
	_TESTCLASS: ClassVar[Type[Testclass]] = Testclass
	_TESTSUITE: ClassVar[Type[Testsuite]] = Testsuite

	@classmethod
	def FromTestsuiteSummary(cls, xmlReportFile: Path, testsuiteSummary: ut_TestsuiteSummary):
		doc = cls(xmlReportFile)
		doc._name = testsuiteSummary._name
		doc._startTime = testsuiteSummary._startTime
		doc._duration = testsuiteSummary._totalDuration
		doc._status = testsuiteSummary._status
		doc._tests = testsuiteSummary._tests
		doc._skipped = testsuiteSummary._skipped
		doc._errored = testsuiteSummary._errored
		doc._failed = testsuiteSummary._failed
		doc._passed = testsuiteSummary._passed

		doc.AddTestsuites(Testsuite.FromTestsuite(testsuite) for testsuite in testsuiteSummary._testsuites.values())

		return doc

	def Analyze(self) -> None:
		"""
		Analyze the XML file, parse the content into an XML data structure and validate the data structure using an XML
		schema.

		.. hint::

		   The time spend for analysis will be made available via property :data:`AnalysisDuration`.

		The used XML schema definition is specific to the GoogleTest JUnit dialect.
		"""
		xmlSchemaFile = "GoogleTest-JUnit.xsd"
		self._Analyze(xmlSchemaFile)

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

	def Convert(self) -> None:
		"""
		Convert the parsed and validated XML data structure into a JUnit test entity hierarchy.

		.. hint::

		   The time spend for model conversion will be made available via property :data:`ModelConversionDuration`.

		:raises UnittestException: If XML was not read and parsed before.
		"""
		if self._xmlDocument is None:
			ex = UnittestException(f"JUnit XML file '{self._path}' needs to be read and analyzed by an XML parser.")
			ex.add_note(f"Call 'JUnitDocument.Analyze()' or create the document using 'JUnitDocument(path, parse=True)'.")
			raise ex

		startConversion = perf_counter_ns()
		rootElement: _Element = self._xmlDocument.getroot()

		self._name = self._ParseName(rootElement, optional=True)
		self._startTime =self._ParseTimestamp(rootElement, optional=True)
		self._duration = self._ParseTime(rootElement, optional=True)

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
		newTestsuite = Testsuite(
			self._ParseName(testsuitesNode, optional=False),
			self._ParseHostname(testsuitesNode, optional=True),
			self._ParseTimestamp(testsuitesNode, optional=False),
			self._ParseTime(testsuitesNode, optional=False),
			parent=parent
		)

		self._ParseTestsuiteChildren(testsuitesNode, newTestsuite)

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

		for testclass in testsuite._testclasses.values():
			for tc in testclass._testcases.values():
				self._GenerateTestcase(tc, testsuiteElement)

	def _GenerateTestcase(self, testcase: Testcase, parentElement: _Element):
		testcaseElement = SubElement(parentElement, "testcase")
		if testcase.Classname is not None:
			testcaseElement.attrib["classname"] = testcase.Classname
		testcaseElement.attrib["name"] = testcase._name
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
