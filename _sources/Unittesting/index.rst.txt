.. _UNITTEST:

Unittesting
###########

*pyEDAA.Reports* provides a unified and generic unittest summary data model. The data model allows the description of
testcases grouped in testsuites. Testsuites can be nested in other testsuites. The data model's root element is a
special testsuite called testsuite summary. It contains only testsuites, but no testcases.

The data model can be filled from various sources like **Ant JUnit test reports** or **OSVVM testsuite summaries** (more
to be added). Many programming languages and/or unit testing frameworks support exporting results in the Ant JUnit
format. See below for supported formats and their variations (dialects).

.. attention::

   The so called JUnit XML format is the weakest file format and standard ever seen. At first was not created by JUnit
   (version 4). It was added by the built system Ant, but it's not called Ant XML format nor Ant JUnit XML format. The
   latest JUnit 5 uses a completely different format called :ref:`open test reporting <UNITTEST/FileFormats/OTR>`. As
   JUnit is not the formats author, no file format documentation nor XML schema was provided. Also Ant isn't providing
   any file format documentation or XML schema. Various Ant JUnit XML adopters have tried to reverse engineer a
   description and XML schemas, but unfortunately many are not even compatible to each other.


.. include:: DataModel.rst

.. _UNITTEST/SpecificDataModels:

Specific Data Models
********************

.. include:: JUnitDataModel.rst
.. include:: OSVVMDataModel.rst


.. include:: Features.rst



.. _UNITTEST/CLI:

Command Line Tool
*****************

.. code-block:: bash

   pyedaa-reports unittest --input=Ant-JUnit:data/JUnit.xml


.. _UNITTEST/FileFormats:

File Formats
************

Unittest summary reports can be stored in various file formats. Usually these files are XML based. Due to missing
(clear) specifications and XML schema definitions, some file formats have developed dialects. Either because the
specification was unclear/not existing or because the format was specific for a single programming language, so tools
added extensions or misused XML attributes instead of designing their own file format.

.. _UNITTEST/FileFormats/AntJUnit4:

Ant and JUnit 4 XML
===================

The so-called JUnit XML format was defined by Ant when running JUnit4 test suites. Because the format was not specified
by JUnit4, many dialects spread out. Many tools and test frameworks have minor or major differences compared to the
original format. While some modifications seam logical additions or adjustments to the needs of the respective
framework, others undermine the ideas and intents of the data format.

Many issues arise because the :ref:`Ant + JUnit4 <UNITTEST/SpecificDataModel/JUnit/Dialect/AntJUnit4>` format is
specific to unit testing with Java. Other languages and frameworks were lazy and didn't derive their own format, but
rather stuffed their language constructs into the concepts and limitations of the Ant + JUnit4 XML format.

.. rubric:: JUnit Dialects

* 🚧 Bamboo JUnit (planned)
* ✅ :ref:`CTest JUnit format <UNITTEST/SpecificDataModel/JUnit/Dialect/CTest>`
* ✅ :ref:`GoogleTest JUnit format <UNITTEST/SpecificDataModel/JUnit/Dialect/GoogleTest>`
* 🚧 Jenkins JUnit (planned)
* ✅ :ref:`pyTest JUnit format <UNITTEST/SpecificDataModel/JUnit/Dialect/PyTest>`


.. _UNITTEST/FileFormats/JUnit5:

JUnit 5 XML
===========

JUnit5 uses a new format called :ref:`UNITTEST/FileFormats/OTR` (see the following section for details). This format
isn't specific to Java (packages, classes, methods, ...), but describes a generic data model. Of cause an extension for
Java specifics is provided too.


.. _UNITTEST/FileFormats/OTR:

Open Test Reporting
===================

The `Open Test Alliance <https://github.com/ota4j-team>`__ created a new format called
`Open Test Reporting <https://github.com/ota4j-team/open-test-reporting>`__ (OTR) to overcome the shortcommings of a
missing file format for JUnit5 as well as the problems of Ant + JUnit4.

OTR defines a structure of test groups and tests, but no specifics of a certain programming languge. The logical
structure of tests and test groups is decoupled from language specifics like namespaces, packages or classes hosting the
individual tests.


.. _UNITTEST/FileFormats/OSVVM:

OSVVM YAML
==========

The `Open Source VHDL Verification Methodology (OSVVM) <https://github.com/OSVVM>`__ defines its own test report format
in YAML. While OSVVM is able to convert its own YAML files to JUnit XML files, it's recommended to use the YAML files as
data source, because these contain additional information, which can't be expressed with JUnit XML.

The YAML files are created when OSVVM-based testbenches are executed with OSVVM's embedded TCL scripting environment
`OSVVM-Scripts <https://github.com/OSVVM/OSVVM-Scripts>`__.

.. hint::

   YAML was chosen instead of JSON or XML, because a YAML document isn't corrupted in case of a runtime error. The
   document might be incomplete (content), but not corrupted (structural). Such a scenario is possible if a VHDL
   simulator stops execution, then the document structure can't be finalized.




.. _UNITTEST/Tools:

Frameworks / Tools
******************

.. _UNITTEST/Tool/CTest:

CTest
=====

* https://github.com/bvdberg/ctest


.. _UNITTEST/Tool/GoogleTest:

GoogleTest (gtest)
==================

* https://github.com/google/googletest


.. _UNITTEST/Tool/JUnit4:

JUnit4
======

* https://github.com/apache/ant
* https://github.com/junit-team/junit4


.. _UNITTEST/Tool/JUnit5:

JUnit5
======


.. _UNITTEST/Tool/OSVVM:

OSVVM
=====

* https://github.com/OSVVM/OSVVM
* https://github.com/OSVVM/OSVVM-Scripts


.. _UNITTEST/Tool/pytest:

pytest
======

* https://github.com/pytest-dev/pytest


.. _UNITTEST/Tool/VUnit:

VUnit
=====

* https://github.com/VUnit/vunit


.. _UNITTEST/Consumers:


Consumers
*********

.. _UNITTEST/Consumer/GitLab:

GitLab
======

.. _UNITTEST/Consumer/Jenkins:

Jenkins
=======


.. _UNITTEST/Consumer/Dorney:

Dorney (GitHub Action)
======================

* https://github.com/dorny/test-reporter
