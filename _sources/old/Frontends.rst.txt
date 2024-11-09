Frontends
=========

Both GitHub and GitLab do provide features for displaying CI results through their web GUIs. Although they are not rich
enough for displaying all the details, OSVR generators can provide stripped down file formats matching some of the
supported readers; similarly to the JSON and xUnit outputs provided by VUnit.

.. _API:Logging:OSVRE:

Open Source Verification Report Explorer
----------------------------------------

It would be interesting to have a vendor agnostic tool for visualizing reports locally and/or in self-hosted services.
Since XML, JSON or YAML are used, web technologies (HTML + CSS + JavaScript) feel like a sensible choice. Generating an
static page which can be hosted on GitHub Pages or GitLab Pages allows granular analysis of CI results, while also being
usable locally. There are several simple and not-so-simple solutions available for xUnit files:

* `w3schools.com/howto/howto_js_treeview <https://www.w3schools.com/howto/howto_js_treeview.asp>`__
* `lukejpreston.github.io/xunit-viewer <https://lukejpreston.github.io/xunit-viewer/>`__
* `Standalone JUnit XML report viewer <https://softwarerecs.stackexchange.com/questions/3666/standalone-junit-xml-report-viewer>`__
* `docs.qameta.io/allure <https://docs.qameta.io/allure/>`__
* `inorton/junit2html <https://github.com/inorton/junit2html>`__

Similar solutions exist based on unittest or pytest:

* `xmlrunner/unittest-xml-reporting <https://github.com/xmlrunner/unittest-xml-reporting>`__
* `pytest-reporter <https://pypi.org/project/pytest-reporter/>`__

  * `pytest-reporter-html1 <https://pypi.org/project/pytest-reporter-html1/>`__

As a complement, extending `pyucis-viewer <https://github.com/fvutils/pyucis-viewer>`__ might be evaluated, for providing
a Qt based solution. pyucis-viewer currently provides a simple bar-chart viewer for coverage data read via pyucis.

GitHub
------

Although there is no official feature for using the `GitHub Checks <https://docs.github.com/en/rest/reference/checks>`__
API, there are some community actions for e.g. analysing xUnit files: `publish-unit-test-results <https://github.com/marketplace/actions/publish-unit-test-results>`__. There are also multiple bindings in JavaScript, Python or golang for
interacting with GitHub's API.

GitLab
------

Apart from `unit test reports <https://docs.gitlab.com/ee/ci/unit_test_reports.html>`__, GitLab supports over a dozen
`artifact reports <https://docs.gitlab.com/ee/ci/unit_test_reports.html>`__.

Grafana
-------

On top of visualizing individual reports or sets of reports at one point in time, tracking the evolution of certain
metrics throughout the development of a project can provide valuable insight. GitLab does have a built-in `Prometheus <https://prometheus.io/>`_ monitoring system and `Grafana <https://grafana.com/>`_ can be optionally used as a dashboard:
`docs.gitlab.com: Grafana Dashboard Service <https://docs.gitlab.com/omnibus/settings/grafana.html>`__. Therefore, it
would be useful to send OSVR reports to either Prometheus or some other temporal database (say Graphite, InfluxDB, etc.).

References
----------

* `EDAAC/EDAAC <https://github.com/EDAAC/EDAAC>`__: EDA Analytics Central
