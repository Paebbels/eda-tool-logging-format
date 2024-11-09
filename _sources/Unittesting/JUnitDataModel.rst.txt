.. _UNITTEST/SpecificDataModel/JUnit:

JUnit Data Model
================

.. grid:: 2

   .. grid-item::
      :columns: 6

      .. grid:: 2

         .. grid-item-card::
            :columns: 6

            :ref:`UNITTEST/SpecificDataModel/JUnit/Testcase`
            ^^^
            A :dfn:`test case` is the leaf-element in the test entity hierarchy and describes an individual test run.
            Test cases are grouped by test classes.

         .. grid-item-card::
            :columns: 6

            :ref:`UNITTEST/SpecificDataModel/JUnit/Testclass`
            ^^^
            A :dfn:`test class` is the mid-level element in the test entity hierarchy and describes a group of test
            runs. Test classes are grouped by test suites.

         .. grid-item-card::
            :columns: 6

            :ref:`UNITTEST/SpecificDataModel/JUnit/Testsuite`
            ^^^
            A :dfn:`test suite` is a group of test classes. Test suites are grouped by a test suite summary.

         .. grid-item-card::
            :columns: 6

            :ref:`UNITTEST/SpecificDataModel/JUnit/TestsuiteSummary`
            ^^^
            The :dfn:`test suite summary` is derived from test suite and defines the root of the test suite hierarchy.

         .. grid-item-card::
            :columns: 6

            :ref:`UNITTEST/SpecificDataModel/JUnit/Document`
            ^^^
            The :dfn:`document` is derived from a test suite summary and represents a file containing a test suite
            summary.

         .. grid-item-card::
            :columns: 6

            :ref:`UNITTEST/SpecificDataModel/JUnit/Dialects`
            ^^^
            The JUnit format is not well defined, thus multiple dialects developed over time.

   .. grid-item::
      :columns: 6

      .. mermaid::

         graph TD;
           doc[Document]
           sum[Summary]
           ts1[Testsuite]
           ts11[Testsuite]
           ts2[Testsuite]

           tc111[Testclass]
           tc112[Testclass]
           tc23[Testclass]

           tc1111[Testcase]
           tc1112[Testcase]
           tc1113[Testcase]
           tc1121[Testcase]
           tc1122[Testcase]
           tc231[Testcase]
           tc232[Testcase]
           tc233[Testcase]

           doc:::root -.-> sum:::summary
           sum --> ts1:::suite
           sum ---> ts2:::suite
           ts1 --> ts11:::suite

           ts11 --> tc111:::cls
           ts11 --> tc112:::cls
           ts2  --> tc23:::cls

           tc111 --> tc1111:::case
           tc111 --> tc1112:::case
           tc111 --> tc1113:::case
           tc112 --> tc1121:::case
           tc112 --> tc1122:::case
           tc23 --> tc231:::case
           tc23 --> tc232:::case
           tc23 --> tc233:::case

           classDef root fill:#4dc3ff
           classDef summary fill:#80d4ff
           classDef suite fill:#b3e6ff
           classDef cls fill:#ff9966
           classDef case fill:#eeccff

.. _UNITTEST/SpecificDataModel/JUnit/Testcase:

Testcase
--------

.. _UNITTEST/SpecificDataModel/JUnit/Testclass:

Testclass
---------

.. _UNITTEST/SpecificDataModel/JUnit/Testsuite:

Testsuite
---------

.. _UNITTEST/SpecificDataModel/JUnit/TestsuiteSummary:

TestsuiteSummary
----------------

.. _UNITTEST/SpecificDataModel/JUnit/Document:

Document
--------

.. _UNITTEST/SpecificDataModel/JUnit/Dialects:

JUnit Dialects
==============

As the JUnit XML format was not well specified and no XML Schema Definition (XSD) was provided, many variants and
dialects (and simplifications) were created by the various frameworks emitting JUnit XML files.

.. rubric:: JUnit Dialect Comparison

+------------------------+--------------+--------------+--------------------+------------------+--------------+
| Feature                | Any JUnit    | Ant + JUnit4 | CTest JUnit        | GoogleTest JUnit | pyTest JUnit |
+========================+==============+==============+====================+==================+==============+
| Root element           | testsuites   | testsuite    | testsuite          | testsuites       | testsuites   |
+------------------------+--------------+--------------+--------------------+------------------+--------------+
| Supports properties    |     ☑        |     ☑        |                    |       ⸺          |              |
+------------------------+--------------+--------------+--------------------+------------------+--------------+
| Testcase status        | ...          | ...          | more status values |                  |              |
+------------------------+--------------+--------------+--------------------+------------------+--------------+

.. _UNITTEST/SpecificDataModel/JUnit/Dialect/AnyJUnit:

Any JUnit
---------

.. grid:: 2

   .. grid-item::
      :columns: 6

      The Any JUnit format uses a relaxed XML schema definition aiming to parse many JUnit XML dialects, which use a
      ``<testsuites>`` root element.

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Reading Any JUnit
            :sync: ReadJUnit

            .. code-block:: Python

               from pyEDAA.Reports.Unittesting.JUnit import Document

               xmlReport = Path("AnyJUnit-Report.xml")
               try:
                 doc = Document(xmlReport, parse=True)
               except UnittestException as ex:
                 ...

         .. tab-item:: Convert to and from Unified Data Model
            :sync: ConvertToFrom

            .. code-block:: Python

               from pyEDAA.Reports.Unittesting.JUnit import Document

               # Convert to unified test data model
               summary = doc.ToTestsuiteSummary()

               # Convert back to a document
               newXmlReport = Path("New JUnit-Report.xml")
               newDoc = Document.FromTestsuiteSummary(newXmlReport, summary)

         .. tab-item:: Writing Any JUnit
            :sync: WriteJUnit

            .. code-block:: Python

               from pyEDAA.Reports.Unittesting.JUnit import Document

               xmlReport = Path("AnyJUnit-Report.xml")
               try:
                 newDoc.Write(xmlReport)
               except UnittestException as ex:
                 ...


.. _UNITTEST/SpecificDataModel/JUnit/Dialect/AntJUnit4:

Ant + JUnit4
------------

.. grid:: 2

   .. grid-item::
      :columns: 6

      The original JUnit format created by `Ant <https://github.com/apache/ant>`__ for `JUnit4 <https://github.com/junit-team/junit4>`__
      uses ``<testsuite>`` as a root element.

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Reading Ant + JUnit4
            :sync: ReadJUnit

            .. code-block:: Python

               from pyEDAA.Reports.Unittesting.JUnit.AntJUnit4 import Document

               xmlReport = Path("AntJUnit4-Report.xml")
               try:
                 doc = Document(xmlReport, parse=True)
               except UnittestException as ex:
                 ...

         .. tab-item:: Convert to and from Unified Data Model
            :sync: ConvertToFrom

            .. code-block:: Python

               from pyEDAA.Reports.Unittesting.JUnit.AntJUnit4 import Document

               # Convert to unified test data model
               summary = doc.ToTestsuiteSummary()

               # Convert back to a document
               newXmlReport = Path("New JUnit-Report.xml")
               newDoc = Document.FromTestsuiteSummary(newXmlReport, summary)

         .. tab-item:: Writing Ant + JUnit4
            :sync: WriteJUnit

            .. code-block:: Python

               from pyEDAA.Reports.Unittesting.JUnit.AntJUnit4 import Document

               xmlReport = Path("AnyJUnit-Report.xml")
               try:
                 newDoc.Write(xmlReport)
               except UnittestException as ex:
                 ...



.. _UNITTEST/SpecificDataModel/JUnit/Dialect/CTest:

CTest JUnit
-----------

.. grid:: 2

   .. grid-item::
      :columns: 6

      The CTest JUnit format written by `CTest <https://github.com/bvdberg/ctest>`__ uses ``<testsuite>`` as a root
      element.

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Reading CTest JUnit
            :sync: ReadJUnit

            .. code-block:: Python

               from pyEDAA.Reports.Unittesting.JUnit.CTestJUnit import Document

               xmlReport = Path("CTestJUnit-Report.xml")
               try:
                 doc = Document(xmlReport, parse=True)
               except UnittestException as ex:
                 ...

         .. tab-item:: Convert to and from Unified Data Model
            :sync: ConvertToFrom

            .. code-block:: Python

               from pyEDAA.Reports.Unittesting.JUnit.CTestJUnit import Document

               # Convert to unified test data model
               summary = doc.ToTestsuiteSummary()

               # Convert back to a document
               newXmlReport = Path("New JUnit-Report.xml")
               newDoc = Document.FromTestsuiteSummary(newXmlReport, summary)

         .. tab-item:: Writing CTest JUnit
            :sync: WriteJUnit

            .. code-block:: Python

               from pyEDAA.Reports.Unittesting.JUnit.CTestJUnit import Document

               xmlReport = Path("AnyJUnit-Report.xml")
               try:
                 newDoc.Write(xmlReport)
               except UnittestException as ex:
                 ...


.. _UNITTEST/SpecificDataModel/JUnit/Dialect/GoogleTest:

GoogleTest JUnit
----------------

.. grid:: 2

   .. grid-item::
      :columns: 6

      The GoogleTest JUnit format written by `GoogleTest <https://github.com/google/googletest>`__ (sometimes GTest)
      uses ``<testsuites>`` as a root element.

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Reading GoogleTest JUnit
            :sync: ReadJUnit

            .. code-block:: Python

               from pyEDAA.Reports.Unittesting.JUnit.GoogleTestJUnit import Document

               xmlReport = Path("GoogleTestJUnit-Report.xml")
               try:
                 doc = Document(xmlReport, parse=True)
               except UnittestException as ex:
                 ...

         .. tab-item:: Convert to and from Unified Data Model
            :sync: ConvertToFrom

            .. code-block:: Python

               from pyEDAA.Reports.Unittesting.JUnit.GoogleTestJUnit import Document

               # Convert to unified test data model
               summary = doc.ToTestsuiteSummary()

               # Convert back to a document
               newXmlReport = Path("New JUnit-Report.xml")
               newDoc = Document.FromTestsuiteSummary(newXmlReport, summary)

         .. tab-item:: Writing GoogleTest JUnit
            :sync: WriteJUnit

            .. code-block:: Python

               from pyEDAA.Reports.Unittesting.JUnit.GoogleTestJUnit import Document

               xmlReport = Path("AnyJUnit-Report.xml")
               try:
                 newDoc.Write(xmlReport)
               except UnittestException as ex:
                 ...


.. _UNITTEST/SpecificDataModel/JUnit/Dialect/pyTest:

pyTest JUnit
------------

.. grid:: 2

   .. grid-item::
      :columns: 6

      The pyTest JUnit format written by `pyTest <https://github.com/pytest-dev/pytest>`__ uses ``<testsuites>`` as a
      root element.

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Reading pyTest JUnit
            :sync: ReadJUnit

            .. code-block:: Python

               from pyEDAA.Reports.Unittesting.JUnit.PyTestJUnit import Document

               xmlReport = Path("PyTestJUnit-Report.xml")
               try:
                 doc = Document(xmlReport, parse=True)
               except UnittestException as ex:
                 ...

         .. tab-item:: Convert to and from Unified Data Model
            :sync: ConvertToFrom

            .. code-block:: Python

               from pyEDAA.Reports.Unittesting.JUnit.PyTestJUnit import Document

               # Convert to unified test data model
               summary = doc.ToTestsuiteSummary()

               # Convert back to a document
               newXmlReport = Path("New JUnit-Report.xml")
               newDoc = Document.FromTestsuiteSummary(newXmlReport, summary)

         .. tab-item:: Writing pyTest JUnit
            :sync: WriteJUnit

            .. code-block:: Python

               from pyEDAA.Reports.Unittesting.JUnit.PyTestJUnit import Document

               xmlReport = Path("AnyJUnit-Report.xml")
               try:
                 newDoc.Write(xmlReport)
               except UnittestException as ex:
                 ...
