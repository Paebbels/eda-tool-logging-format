Introduction
############

While all tools provide feedback by logging into terminal, many of them do also provide results through some report file
format.
However, there is no standard/universal report format which can gather all the diferent types of results that EDA tools
can provide.
pyEDAA.Reports is a proposal for achieving it.

As shown in the figure below, the main purpose is to allow reusing existing frontends (such as `GitHub Checks <https://docs.github.com/en/rest/reference/checks>`__,
Gitlab `job artifacts <https://docs.gitlab.com/ee/ci/pipelines/job_artifacts.html#artifactsreports>`__ and `unit test reports <https://docs.gitlab.com/ee/ci/unit_test_reports.html>`__,
and/or `Grafana <https://grafana.com/>`__) from software testing/verification, rather than reinventing a solution from
scratch. By the same token, we would like to use coverage and test report formats which are compatible with the existing
open source ecosystem used by software people.

.. figure:: _static/overview.png
  :alt: Open Source Verification Report
  :align: center

  Sources, core and outputs.

The most basic functionality is adding a hierarchy level on top of xUnit, for aggregating multiple xUnit reports
corresponding to the same design/project.
That additional hierarchy might be encoded as an additional field in the XML, or by prepending suite names with specific
keywords.
On top of that, some content in hardware project reports need some more elaborated formats.
In the following subsections, each report type is analysed.
