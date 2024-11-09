.. _UNITTEST/DataModel:

Unified data model
******************

The unified data model for test entities (test summary, test suite, test case) implements a super-set of all (so far
known) unit test result summary file formats. pyEDAA.Report's data model is a structural and functional cleanup of the
Ant JUnit data model. Naming has been cleaned up and missing features have been added.

As some of the JUnit XML dialects are too divergent from the original Ant + JUnit4 format, these dialects have an
independent test entity inheritance hierarchy. Nonetheless, instances of each data format can be converted to and from
the unified data model.

.. grid:: 2

   .. grid-item::
      :columns: 6

      .. grid:: 2

         .. grid-item-card::
            :columns: 6

            :ref:`UNITTEST/DataModel/Testcase`
            ^^^
            A :dfn:`test case` is the leaf-element in the test entity hierarchy and describes an individual test run.
            Test cases are grouped by test suites.

         .. grid-item-card::
            :columns: 6

            :ref:`UNITTEST/DataModel/Testsuite`
            ^^^
            A :dfn:`test suite` is a group of test cases and/or test suites. Test suites itself can be grouped by test
            suites. The test suite hierarchy's root element is a test suite summary.

         .. grid-item-card::
            :columns: 6

            :ref:`UNITTEST/DataModel/TestsuiteSummary`
            ^^^
            The :dfn:`test suite summary` is derived from test suite and defines the root of the test suite hierarchy.

         .. grid-item-card::
            :columns: 6

            :ref:`UNITTEST/DataModel/Document`
            ^^^
            The :dfn:`document` is derived from a test suite summary and represents a file containing a test suite
            summary.

   .. grid-item::
      :columns: 6

      .. mermaid::

         graph TD;
           doc[Document]
           sum[Summary]
           ts1[Testsuite]
           ts2[Testsuite]
           ts21[Testsuite]
           tc11[Testcase]
           tc12[Testcase]
           tc13[Testcase]
           tc21[Testcase]
           tc22[Testcase]
           tc211[Testcase]
           tc212[Testcase]
           tc213[Testcase]

           doc:::root -.-> sum:::summary
           sum --> ts1:::suite
           sum --> ts2:::suite
           ts2 --> ts21:::suite
           ts1 --> tc11:::case
           ts1 --> tc12:::case
           ts1 --> tc13:::case
           ts2 --> tc21:::case
           ts2 --> tc22:::case
           ts21 --> tc211:::case
           ts21 --> tc212:::case
           ts21 --> tc213:::case

           classDef root fill:#4dc3ff
           classDef summary fill:#80d4ff
           classDef suite fill:#b3e6ff
           classDef case fill:#eeccff


.. _UNITTEST/DataModel/TestcaseStatus:

Testcase Status
===============

.. grid:: 2

   .. grid-item::
      :columns: 6

      :class:`~pyEDAA.Reports.Unittesting.TestcaseStatus` and :class:`~pyEDAA.Reports.Unittesting.TestsuiteStatus` are
      flag enumerations to describe the overall status of a test case or test suite.

      Unknown
        tbd

      Excluded
        tbd

      Skipped
        tbd

      Weak
        tbd

      Passed
        tbd

      Failed
        tbd

      Inverted
        tbd

      Warned
        tbd

      Errored
        tbd

      Failed
        tbd

      SetupError
        tbd

      TearDownError
        tbd

      Inconsistent
        tbd


   .. grid-item::
      :columns: 6

      .. code-block:: Python

         @export
         class TestcaseStatus(Flag):
           """A flag enumeration describing the status of a test case."""
           Unknown =    0                         #: Testcase status is uninitialized and therefore unknown.
           Excluded =   1                         #: Testcase was permanently excluded / disabled
           Skipped =    2                         #: Testcase was temporarily skipped (e.g. based on a condition)
           Weak =       4                         #: No assertions were recorded.
           Passed =     8                         #: A passed testcase, because all assertions were successful.
           Failed =    16                         #: A failed testcase due to at least one failed assertion.

           Mask = Excluded | Skipped | Weak | Passed | Failed

           Inverted = 128                         #: To mark inverted results
           UnexpectedPassed = Failed | Inverted
           ExpectedFailed =   Passed | Inverted

           Warned =  1024                         #: Runtime warning
           Errored = 2048                         #: Runtime error (mostly caught exceptions)
           Aborted = 4096                         #: Uncaught runtime exception

           SetupError =     8192                  #: Preparation / compilation error
           TearDownError = 16384                  #: Cleanup error / resource release error
           Inconsistent = 32768                   #: Dataset is inconsistent

           Flags = Warned | Errored | Aborted | SetupError | TearDownError | Inconsistent

      .. code-block:: Python

         @export
         class TestsuiteStatus(Flag):
           """A flag enumeration describing the status of a test suite."""
           Unknown =    0
           Excluded =   1                         #: Testcase was permanently excluded / disabled
           Skipped =    2                         #: Testcase was temporarily skipped (e.g. based on a condition)
           Empty =      4                         #: No tests in suite
           Passed =     8                         #: Passed testcase, because all assertions succeeded
           Failed =    16                         #: Failed testcase due to failing assertions

           Mask = Excluded | Skipped | Empty | Passed | Failed

           Inverted = 128                         #: To mark inverted results
           UnexpectedPassed = Failed | Inverted
           ExpectedFailed =   Passed | Inverted

           Warned =  1024                         #: Runtime warning
           Errored = 2048                         #: Runtime error (mostly caught exceptions)
           Aborted = 4096                         #: Uncaught runtime exception

           SetupError =     8192                  #: Preparation / compilation error
           TearDownError = 16384                  #: Cleanup error / resource release error

           Flags = Warned | Errored | Aborted | SetupError | TearDownError


.. _UNITTEST/DataModel/Testcase:

Testcase
========

.. grid:: 2

   .. grid-item::
      :columns: 6

      A :class:`~pyEDAA.Reports.Unittesting.Testcase` is the leaf-element in the test entity hierarchy and describes an
      individual test run. Besides a test case status, it also contains statistics like the start time or the test
      duration. Test cases are grouped by test suites and need to be unique per parent test suite.

      A test case (or its base classes) implements the following properties and methods:

      :data:`~pyEDAA.Reports.Unittesting.Base.Parent`
         The test case has a reference to it's parent test suite in the hierarchy. By iterating parent references, the
         root element (test suite summary) be be found, which has no parent reference (``None``).

      :data:`~pyEDAA.Reports.Unittesting.Base.Name`
         The test case has a name. This name must be unique per hierarchy parent, but can exist multiple times in the
         overall test hierarchy.

         In case the data format uses hierarchical names like ``pyEDAA.Reports.CLI.Application``, the name is split at
         the separator and multiple hierarchy levels (test suites) are created in the unified data model. To be able to
         recreate such an hierarchical name, :class:`~pyEDAA.Reports.Unittesting.TestsuiteKind` is applied accordingly
         to test suite's :data:`~pyEDAA.Reports.Unittesting.TestsuiteBase.Kind` field.

      :data:`~pyEDAA.Reports.Unittesting.Base.StartTime`
         The test case stores a time when the individual test run was started. In combination with
         :data:`~pyEDAA.Reports.Unittesting.Base.TotalDuration`, the end time can be calculated. If the start time is
         unknown, set this value to ``None``.

      :data:`~pyEDAA.Reports.Unittesting.Base.SetupDuration`, :data:`~pyEDAA.Reports.Unittesting.Base.TestDuration`, :data:`~pyEDAA.Reports.Unittesting.Base.TeardownDuration`, :data:`~pyEDAA.Reports.Unittesting.Base.TotalDuration`
         The test case has fields to capture the setup duration, test run duration and teardown duration. The sum of all
         durations is provided by total duration.

         :pycode:`TotalDuration := SetupDuration + TestDuration + TeardownDuration`

         The :dfn:`setup duration` is the time spend on setting up a test run. If the setup duration can't be
         distinguished from the test's runtime, set this value to ``None``.

         The test's runtime without setup and teardown portions is captured by :dfn:`test duration`. If the duration is
         unknown, set this value to ``None``.

         The :dfn:`teardown duration` of a test run is the time spend on tearing down a test run. If the teardown
         duration can't be distinguished from the test's runtime, set this value to ``None``.

         The test case has a field :dfn:`total duration` to sum up setup duration, test duration and teardown duration.
         If the duration is unknown, this value will be ``None``.

      :data:`~pyEDAA.Reports.Unittesting.Base.WarningCount`, :data:`~pyEDAA.Reports.Unittesting.Base.ErrorCount`, :data:`~pyEDAA.Reports.Unittesting.Base.FatalCount`
         The test case counts for warnings, errors and fatal errors observed in a test run while the test was executed.

      :meth:`~pyEDAA.Reports.Unittesting.Base.__len__`, :meth:`~pyEDAA.Reports.Unittesting.Base.__getitem__`, :meth:`~pyEDAA.Reports.Unittesting.Base.__setitem__`, :meth:`~pyEDAA.Reports.Unittesting.Base.__delitem__`, :meth:`~pyEDAA.Reports.Unittesting.Base.__contains__`, :meth:`~pyEDAA.Reports.Unittesting.Base.__iter__`
         The test case implements a dictionary interface, so arbitrary key-value pairs can be annotated per test entity.

      :data:`~pyEDAA.Reports.Unittesting.Testcase.Status`
         The overall status of a test case.

         See also: :ref:`UNITTEST/DataModel/TestcaseStatus`.

      :data:`~pyEDAA.Reports.Unittesting.Testcase.AssertionCount`, :data:`~pyEDAA.Reports.Unittesting.Testcase.PassedAssertionCount`, :data:`~pyEDAA.Reports.Unittesting.Testcase.FailedAssertionCount`
         The :dfn:`assertion count` represents the overall number of assertions (checks) in a test case. It can be
         distinguished into :dfn:`passed assertions` and :dfn:`failed assertions`. If it can't be distinguished, set
         passed and failed assertions to ``None``.

         :pycode:`AssertionCount := PassedAssertionCount + FailedAssertionCount`

      :meth:`~pyEDAA.Reports.Unittesting.Testcase.Copy`
        tbd

      :meth:`~pyEDAA.Reports.Unittesting.Testcase.Aggregate`
        Aggregate (recalculate) all durations, warnings, errors, assertions, etc.

      :meth:`~pyEDAA.Reports.Unittesting.Testcase.__str__`
        tbd

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         @export
         class Testcase(Base):
            def __init__(
               self,
               name: str,
               startTime: Nullable[datetime] = None,
               setupDuration: Nullable[timedelta] = None,
               testDuration: Nullable[timedelta] = None,
               teardownDuration: Nullable[timedelta] = None,
               totalDuration:  Nullable[timedelta] = None,
               status: TestcaseStatus = TestcaseStatus.Unknown,
               assertionCount: Nullable[int] = None,
               failedAssertionCount: Nullable[int] = None,
               passedAssertionCount: Nullable[int] = None,
               warningCount: int = 0,
               errorCount: int = 0,
               fatalCount: int = 0,
               parent: Nullable["Testsuite"] = None
            ):
              ...

            @readonly
            def Parent(self) -> Nullable["Testsuite"]:
              ...

            @readonly
            def Name(self) -> str:
              ...

            @readonly
            def StartTime(self) -> Nullable[datetime]:
              ...

            @readonly
            def SetupDuration(self) -> Nullable[timedelta]:
              ...

            @readonly
            def TestDuration(self) -> Nullable[timedelta]:
              ...

            @readonly
            def TeardownDuration(self) -> Nullable[timedelta]:
              ...

            @readonly
            def TotalDuration(self) -> Nullable[timedelta]:
              ...

            @readonly
            def WarningCount(self) -> int:
              ...

            @readonly
            def ErrorCount(self) -> int:
              ...

            @readonly
            def FatalCount(self) -> int:
              ...

            def __len__(self) -> int:
              ...

            def __getitem__(self, key: str) -> Any:
              ...

            def __setitem__(self, key: str, value: Any) -> None:
              ...

            def __delitem__(self, key: str) -> None:
              ...

            def __contains__(self, key: str) -> bool:
              ...

            def __iter__(self) -> Generator[Tuple[str, Any], None, None]:
              ...

            @readonly
            def Status(self) -> TestcaseStatus:
              ...

            @readonly
            def AssertionCount(self) -> int:
              ...

            @readonly
            def FailedAssertionCount(self) -> int:
              ...

            @readonly
            def PassedAssertionCount(self) -> int:
              ...

            def Copy(self) -> "Testcase":
              ...

            def Aggregate(self, strict: bool = True) -> TestcaseAggregateReturnType:
              ...

            def __str__(self) -> str:
              ...


.. _UNITTEST/DataModel/Testsuite:

Testsuite
=========

.. grid:: 2

   .. grid-item::
      :columns: 6

      A :class:`~pyEDAA.Reports.Unittesting.Testsuite` is a grouping element in the test entity hierarchy and describes
      a group of test runs. Besides a list of test cases and a test suite status, it also contains statistics like the
      start time or the test duration for the group of tests. Test suites are grouped by other test suites or a test
      suite summary and need to be unique per parent test suite.

      A test suite (or its base classes) implements the following properties and methods:

      :data:`~pyEDAA.Reports.Unittesting.Base.Parent`
         The test suite has a reference to it's parent test entity in the hierarchy. By iterating parent references, the
         root element (test suite summary) be be found, which has no parent reference (``None``).

      :data:`~pyEDAA.Reports.Unittesting.Base.Name`
         The test suite has a name. This name must be unique per hierarchy parent, but can exist multiple times in the
         overall test hierarchy.

         In case the data format uses hierarchical names like ``pyEDAA.Reports.CLI.Application``, the name is split at
         the separator and multiple hierarchy levels (test suites) are created in the unified data model. To be able to
         recreate such an hierarchical name, :class:`~pyEDAA.Reports.Unittesting.TestsuiteKind` is applied accordingly
         to test suite's :data:`~pyEDAA.Reports.Unittesting.TestsuiteBase.Kind` field.

      :data:`~pyEDAA.Reports.Unittesting.Base.StartTime`
         The test suite stores a time when the first test run was started. In combination with
         :data:`~pyEDAA.Reports.Unittesting.Base.TotalDuration`, the end time can be calculated. If the start time is
         unknown, set this value to ``None``.

      :data:`~pyEDAA.Reports.Unittesting.Base.SetupDuration`, :data:`~pyEDAA.Reports.Unittesting.Base.TestDuration`, :data:`~pyEDAA.Reports.Unittesting.Base.TeardownDuration`, :data:`~pyEDAA.Reports.Unittesting.Base.TotalDuration`
         The test suite has fields to capture the suite's setup duration, test group run duration and suite's
         teardown duration. The sum of all durations is provided by total duration.

         :pycode:`TotalDuration := SetupDuration + TestDuration + TeardownDuration`

         The :dfn:`setup duration` is the time spend on setting up a test suite. If the setup duration can't be
         distinguished from the test group's runtime, set this value to ``None``.

         The test group's runtime without setup and teardown portions is captured by :dfn:`test duration`. If the
         duration is unknown, set this value to ``None``.

         The :dfn:`teardown duration` of a test suite is the time spend on tearing down a test suite. If the teardown
         duration can't be distinguished from the test group's runtime, set this value to ``None``.

         The test suite has a field :dfn:`total duration` to sum up setup duration, test duration and teardown duration.
         If the duration is unknown, this value will be ``None``.

      :data:`~pyEDAA.Reports.Unittesting.Base.WarningCount`, :data:`~pyEDAA.Reports.Unittesting.Base.ErrorCount`, :data:`~pyEDAA.Reports.Unittesting.Base.FatalCount`
         The test suite counts for warnings, errors and fatal errors observed in a test suite while the tests were
         executed.

      :meth:`~pyEDAA.Reports.Unittesting.Base.__len__`, :meth:`~pyEDAA.Reports.Unittesting.Base.__getitem__`, :meth:`~pyEDAA.Reports.Unittesting.Base.__setitem__`, :meth:`~pyEDAA.Reports.Unittesting.Base.__delitem__`, :meth:`~pyEDAA.Reports.Unittesting.Base.__contains__`, :meth:`~pyEDAA.Reports.Unittesting.Base.__iter__`
         The test suite implements a dictionary interface, so arbitrary key-value pairs can be annotated.


      .. todo:: TestsuiteBase APIs


      :data:`~pyEDAA.Reports.Unittesting.Testsuite.Testcases`
        tbd

      :data:`~pyEDAA.Reports.Unittesting.Testsuite.TestcaseCount`
        tbd

      :data:`~pyEDAA.Reports.Unittesting.Testsuite.AssertionCount`
         The overall number of assertions (checks) in a test case.

      :meth:`~pyEDAA.Reports.Unittesting.Testsuite.Aggregate`
        Aggregate (recalculate) all durations, warnings, errors, assertions, etc.

      :meth:`~pyEDAA.Reports.Unittesting.Testsuite.Iterate`
        tbd

      :meth:`~pyEDAA.Reports.Unittesting.Testsuite.__str__`
        tbd

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         @export
         class Testsuite(TestsuiteBase[TestsuiteType]):
            def __init__(
               self,
               name: str,
               kind: TestsuiteKind = TestsuiteKind.Logical,
               startTime: Nullable[datetime] = None,
               setupDuration: Nullable[timedelta] = None,
               testDuration: Nullable[timedelta] = None,
               teardownDuration: Nullable[timedelta] = None,
               totalDuration:  Nullable[timedelta] = None,
               status: TestsuiteStatus = TestsuiteStatus.Unknown,
               warningCount: int = 0,
               errorCount: int = 0,
               fatalCount: int = 0,
               testsuites: Nullable[Iterable[TestsuiteType]] = None,
               testcases: Nullable[Iterable["Testcase"]] = None,
               parent: Nullable[TestsuiteType] = None
            ):
              ...

            @readonly
            def Parent(self) -> Nullable["Testsuite"]:
              ...

            @readonly
            def Name(self) -> str:
              ...

            @readonly
            def StartTime(self) -> Nullable[datetime]:
              ...

            @readonly
            def SetupDuration(self) -> Nullable[timedelta]:
              ...

            @readonly
            def TestDuration(self) -> Nullable[timedelta]:
              ...

            @readonly
            def TeardownDuration(self) -> Nullable[timedelta]:
              ...

            @readonly
            def TotalDuration(self) -> Nullable[timedelta]:
              ...

            @readonly
            def WarningCount(self) -> int:
              ...

            @readonly
            def ErrorCount(self) -> int:
              ...

            @readonly
            def FatalCount(self) -> int:
              ...

            def __len__(self) -> int:
              ...

            def __getitem__(self, key: str) -> Any:
              ...

            def __setitem__(self, key: str, value: Any) -> None:
              ...

            def __delitem__(self, key: str) -> None:
              ...

            def __contains__(self, key: str) -> bool:
              ...

            def __iter__(self) -> Generator[Tuple[str, Any], None, None]:
              ...

            # TestsuiteBase API


            @readonly
            def Testcases(self) -> Dict[str, "Testcase"]:
              ...

            @readonly
            def TestcaseCount(self) -> int:
              ...

            @readonly
            def AssertionCount(self) -> int:
              ...

            def Aggregate(self, strict: bool = True) -> TestsuiteAggregateReturnType:
              ...

            def Iterate(self, scheme: IterationScheme = IterationScheme.Default) -> Generator[Union[TestsuiteType, Testcase], None, None]:
              ...

            def __str__(self) -> str:
              ...


.. _UNITTEST/DataModel/TestsuiteSummary:

TestsuiteSummary
================

.. grid:: 2

   .. grid-item::
      :columns: 6

      A :class:`~pyEDAA.Reports.Unittesting.TestsuiteSummary` is the root element in the test entity hierarchy and
      describes a group of test suites as well as overall statistics for the whole set of test cases. A test suite
      summary is derived for the same base-class as a test suite, thus they share almost all properties and methods.

      A test suite summary (or its base classes) implements the following properties and methods:

      :data:`~pyEDAA.Reports.Unittesting.Base.Parent`
         The test suite summary has a parent reference, but as the root element in the test entity hierarchy, its always
         ``None``.

      :data:`~pyEDAA.Reports.Unittesting.Base.Name`
         The test suite summary has a name.

      :data:`~pyEDAA.Reports.Unittesting.Base.StartTime`
         The test suite summary stores a time when the first test runs was started. In combination with
         :data:`~pyEDAA.Reports.Unittesting.Base.TotalDuration`, the end time can be calculated. If the start time is
         unknown, set this value to ``None``.

      :data:`~pyEDAA.Reports.Unittesting.Base.SetupDuration`, :data:`~pyEDAA.Reports.Unittesting.Base.TestDuration`, :data:`~pyEDAA.Reports.Unittesting.Base.TeardownDuration`, :data:`~pyEDAA.Reports.Unittesting.Base.TotalDuration`
         The test suite summary has fields to capture the suite summary's setup duration, overall run duration and
         suite summary's teardown duration. The sum of all durations is provided by total duration.

         :pycode:`TotalDuration := SetupDuration + TestDuration + TeardownDuration`

         The :dfn:`setup duration` is the time spend on setting up an overall test run. If the setup duration can't be
         distinguished from the test's runtimes, set this value to ``None``.

         The test suite summary's runtime without setup and teardown portions is captured by :dfn:`test duration`. If
         the duration is unknown, set this value to ``None``.

         The :dfn:`teardown duration` of a test suite summary is the time spend on tearing down a test suite summary. If
         the teardown duration can't be distinguished from the test's runtimes, set this value to ``None``.

         The test suite summary has a field :dfn:`total duration` to sum up setup duration, overall run duration and
         teardown duration. If the duration is unknown, this value will be ``None``.

      :data:`~pyEDAA.Reports.Unittesting.Base.WarningCount`, :data:`~pyEDAA.Reports.Unittesting.Base.ErrorCount`, :data:`~pyEDAA.Reports.Unittesting.Base.FatalCount`
         The test suite summary counts for warnings, errors and fatal errors observed in a test suite summary while the
         tests were executed.

      :meth:`~pyEDAA.Reports.Unittesting.Base.__len__`, :meth:`~pyEDAA.Reports.Unittesting.Base.__getitem__`, :meth:`~pyEDAA.Reports.Unittesting.Base.__setitem__`, :meth:`~pyEDAA.Reports.Unittesting.Base.__delitem__`, :meth:`~pyEDAA.Reports.Unittesting.Base.__contains__`, :meth:`~pyEDAA.Reports.Unittesting.Base.__iter__`
         The test suite summary implements a dictionary interface, so arbitrary key-value pairs can be annotated.

      .. todo:: TestsuiteBase APIs

      :meth:`~pyEDAA.Reports.Unittesting.TestsuiteSummary.Aggregate`
        tbd

      :meth:`~pyEDAA.Reports.Unittesting.TestsuiteSummary.Iterate`
        tbd

      :meth:`~pyEDAA.Reports.Unittesting.TestsuiteSummary.__str__`
        tbd

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         @export
         class TestsuiteSummary(TestsuiteBase[TestsuiteType]):
            def __init__(
               self,
               name: str,
               startTime: Nullable[datetime] = None,
               setupDuration: Nullable[timedelta] = None,
               testDuration: Nullable[timedelta] = None,
               teardownDuration: Nullable[timedelta] = None,
               totalDuration:  Nullable[timedelta] = None,
               status: TestsuiteStatus = TestsuiteStatus.Unknown,
               warningCount: int = 0,
               errorCount: int = 0,
               fatalCount: int = 0,
               testsuites: Nullable[Iterable[TestsuiteType]] = None,
               parent: Nullable[TestsuiteType] = None
            ):
              ...

            @readonly
            def Parent(self) -> Nullable["Testsuite"]:
              ...

            @readonly
            def Name(self) -> str:
              ...

            @readonly
            def StartTime(self) -> Nullable[datetime]:
              ...

            @readonly
            def SetupDuration(self) -> Nullable[timedelta]:
              ...

            @readonly
            def TestDuration(self) -> Nullable[timedelta]:
              ...

            @readonly
            def TeardownDuration(self) -> Nullable[timedelta]:
              ...

            @readonly
            def TotalDuration(self) -> Nullable[timedelta]:
              ...

            @readonly
            def WarningCount(self) -> int:
              ...

            @readonly
            def ErrorCount(self) -> int:
              ...

            @readonly
            def FatalCount(self) -> int:
              ...

            def __len__(self) -> int:
              ...

            def __getitem__(self, key: str) -> Any:
              ...

            def __setitem__(self, key: str, value: Any) -> None:
              ...

            def __delitem__(self, key: str) -> None:
              ...

            def __contains__(self, key: str) -> bool:
              ...

            def __iter__(self) -> Generator[Tuple[str, Any], None, None]:
              ...

            # TestsuiteBase API

            def Aggregate(self) -> TestsuiteAggregateReturnType:
              ...

            def Iterate(self, scheme: IterationScheme = IterationScheme.Default) -> Generator[Union[TestsuiteType, Testcase], None, None]:
              ...

            def __str__(self) -> str:
              ...


.. _UNITTEST/DataModel/Document:

Document
========

.. grid:: 2

   .. grid-item::
      :columns: 6

      A :class:`~pyEDAA.Reports.Unittesting.Document` is a mixin-class ...

      :data:`~pyEDAA.Reports.Unittesting.Document.Path`
        tbd

      :data:`~pyEDAA.Reports.Unittesting.Document.AnalysisDuration`
        tbd

      :data:`~pyEDAA.Reports.Unittesting.Document.ModelConversionDuration`
        tbd

      :meth:`~pyEDAA.Reports.Unittesting.Document.Analyze`
        tbd

      :meth:`~pyEDAA.Reports.Unittesting.Document.Convert`
        tbd

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         @export
         class Document(metaclass=ExtendedType, mixin=True):
            def __init__(self, path: Path):
              ...

            @readonly
            def Path(self) -> Path:
              ...

            @readonly
            def AnalysisDuration(self) -> timedelta:
              ...

            @readonly
            def ModelConversionDuration(self) -> timedelta:
              ...

            @abstractmethod
            def Analyze(self) -> None:
              ...

            @abstractmethod
            def Convert(self):
              ...
