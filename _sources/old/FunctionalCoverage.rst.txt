Functional coverage
===================

* `xUnit <https://en.wikipedia.org/wiki/XUnit>`__ (*every unit test is a cover point that has a binary pass|fail*).
  VUnit, cocotb, fsva and others can generate xUnit reports of unit testing suites.
* When PSL is used, GHDL can generate a JSON report of cover and assert statements: :option:`--psl-report <ghdl:ghdl.--psl-report>`.
* OSVVM has an internal coverge database format.
* There is an specification by Accellera, Mentor Graphics and Cadence named Unified Coverage Interoperability Standard (UCIS) and a matching Unified Coverage Database (UCDB).

xUnit
-----

VUnit has built-in support for generating `xUnit <https://en.wikipedia.org/wiki/XUnit>`__ (XML) reports. In fact,
VUnit's name comes from *VHDL unit testing framework* (see `Wikipedia: List of unit testing frameworks <https://en.wikipedia.org/wiki/List_of_unit_testing_frameworks>`__).
CLI option ``-x`` allows specifying the target file name. Two different formats are supported: `Jenkins <https://www.jenkins.io/>`__
(`JUnit <https://plugins.jenkins.io/junit/>`__) and `Bamboo <https://www.atlassian.com/software/bamboo>`__. JUnit is
also supported on GitLab CI: `docs.gitlab.com: Unit test reports <https://docs.gitlab.com/ee/ci/unit_test_reports.html>`__.
Python's unittest (and, therefore, pytest) was originally inspired by JUnit, so it has a similar flavor as unit testing
frameworks in other languages. Moreover, there is `junitparser <https://pypi.org/project/junitparser/>`__, a Python tool
for manipulating xUnit XML files.

Therefore, by using VUnit's simulator interface and test runner infrastructure, it is already possible to generate fine
grained reports in a standard format. This might be useful for users of OSVVM and/or UVVM, which don't have an
equivalent feature.

Cocotb can also generate xUnit reports, independently from VUnit. See `docs.cocotb.org: COCOTB_RESULTS_FILE <https://docs.cocotb.org/en/stable/building.html?highlight=xunit#envvar-COCOTB_RESULTS_FILE>`__.
Precisely, this is related to the duplicated test/regression management features in both frameworks. At the moment,
users are expected to handle them independently when mixed (HDL + cocotb) testsuites are run. However, there is work in
progress for hopefully unifying them automatically (through some post-simulation helper hook). Anyway, while generated
independently, the OSVR core can be used for aggregating them.

.. NOTE:: In the JUnit XML format, the result of each test is only explicitly provided in case of failure, error or skip.
  Therefore, the absence of result indicates a passed test case.

PSL report
----------

As explained in :option:`--psl-report <ghdl:ghdl.--psl-report>`, "*for each PSL cover and assert statements, the name, source location and whether it passed or failed is reported*" by GHDL in a JSON format. Therefore, it should be trivial
to import these reports in OSVR similarly to how xUnit reports are handled.

OSVVM
-----

OSVVM has a non-trivial built-in database format for the advanced functional coverage features provided by
`CoveragePkg <https://github.com/OSVVM/OSVVM/blob/master/CoveragePkg.vhd>`__ (see `OSVVM/Documentation: CoveragePkg_*.pdf <https://github.com/OSVVM/Documentation>`__). There is work in progress with developers of OSVVM for evaluating how
to export it to some standard format, such as xUnit, UCB, or some other XML/JSON/YAML format.

The main constraint for displaying combined results of multidimensional coverage analysis is that xUnit is expected to have a single level of hierarchy (suites and tests). Hence, unlike previous projects, OSVVM might need some more elaborated format.

Unified Coverage Database (UCDB)
--------------------------------

Unified Coverage Database (UCDB) is one of the components of the Unified Coverage Interoperability Standard (UCIS)
developed by Accellera, Mentor Graphics and Cadence. The UCDB is used by Siemens' tools for tracking results, and they
have a GUI module for browsing them. At first sight, UCDB/UCIS are complex and not easy to work with, however, most of
the potential result types are already covered by the specification (see `Unified Coverage Interoperability Standard Version <https://www.accellera.org/downloads/standards/ucis>`__
and `OSVVM Forums: Cover group and Mentor UCDB <https://osvvm.org/forums/topic/cover-group-and-mentor-ucdb>`__).
See also `OSVVM Forums: UCIS / UCDB <https://osvvm.org/forums/topic/ucis-ucdb>`__.
Fortunately, there is an open source Python package that provides an API to UCIS data (`fvutils/pyucis <https://github.com/fvutils/pyucis>`__)
as well as an open source Qt based GUI (`fvutils/pyucis-viewer <https://github.com/fvutils/pyucis-viewer>`__). pyucis
can write coverage data in UCIS XML-interchange format and to mentor UCDB via the UCIS library provided by Questa.
Hence, it might be possible to dump results from open source frameworks/methodologies/tools to UCDB for reusing Siemens'
or fvutils' GUIs, or vice versa.

.. NOTE:: From an open source community perspective, it feels more sensible to dump content from UCDB to an open source
  XML/JSON/YAML format specification. However, as far as we are aware, such FLOSS specification adapted to hardware
  designs does not exist yet. Moreover, the most used HDL languages are neither open source. Hence, although not ideal,
  using UCDB wouldn't be disruptive in this regard. Should you know about any open source alternative, or if you
  represent Accelera, Siemens' and/or Cadence and want to open source UCDB/UCIS, please `let us know <https://github.com/umarcor/osvb/issues/new>`__!
