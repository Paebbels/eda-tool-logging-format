Semantic/rich logging
=====================

xUnit report files (XML) typically provide the relevant raw log output together with the errored, failed or skipped
result.
However, most verification frameworks, tools and methodologies do have more granular information about each entry.
At least, the severity level is a built-in feature in VHDL, and several projects do provide additional logging utilities
with further severity levels or failure reasons.
For instance, VUnit supports custom logging levels, and can export rich logs to CSV files.
Moreover, `pyIPCMI <https://github.com/paebbels/pyIPCMI>`__ includes vendor log processing features for classifying and
optionally filtering the logs.
Therefore, it would be interesting to support preserving the semantic information (at least the severity or specific
vendor error/report code), in the extended xUnit report format used in OSVR.
On top of that, `librecores/eda-log-parser <https://github.com/librecores/eda-log-parser>`__ supports parsing logs from
Verilator and Vivado, along with generating custom log entries to be used in CI systems/services, such as Azure or
GitHub Actions.
