Tracking requirements
=====================

Industries developing systems for critical applications do typically require tracking specification requirements through
the developement of the products.
See, for instance, `Using GitLab for ISO 26262-6:2018 - Product development at the software level <https://about.gitlab.com/solutions/iso-26262/>`__.
Hence, it is very valuable to annotate tests with requirements, and then cross-reference tests and CI runs with those.
In the open source ecosystem, some projects create test cases for each reported MWE through a GitHub/GitLab issue.
Therefore, in such contexts the issue numbers, tags or milestones might be considered requirements to be tracked.

There is an example by Lars Asplund (from VUnit), for illustrating the usage of VUnit attributes for tracking requirements:
`LarsAsplund/vunit_attributes <https://github.com/LarsAsplund/vunit_attributes>`__.
It provides requirement to attribute mapping through the ``--export-json`` option, which is a richer format than the
xUnit produced with ``-x``.
In the example, additional analysis features are provided through a requirement coverage analysis script:
`analyze_requirement_coverage.py <https://github.com/LarsAsplund/vunit_attributes/blob/main/analyze_requirement_coverage.py>`__.
The list of requirements is defined in a CSV file.

Precisely, field ``Metadata`` proposed in the OSVR ``Testcase`` class is expected to contain data such as the attributes.
That is, to integrate VUnit's attribute tracking, with other frameworks which might provide similar features.
