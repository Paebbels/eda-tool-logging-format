Line coverage
=============

Several open source tools (such as GCC or PyPI's `coverage <https://pypi.org/project/coverage/>`__ package) produce
line coverage results in `gcov <https://en.wikipedia.org/wiki/Gcov>`__ format. Moreover, utilities exist for generating
reports from gcov files. For instance `gcovr <https://pypi.org/project/gcovr/>`__ can produce ``html``, ``xml``
(`Cobertura <http://cobertura.sourceforge.net/>`__), ``sonarqube`` and ``json``. Furthermore, some HDL tools, such
as GHDL with GCC backend, can generate gcov results too.
