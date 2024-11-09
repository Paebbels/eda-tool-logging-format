Synthesis and implementation results
====================================

Some synthesis and all implementation tools do provide reports about area/resource usage and estimated maximum clock
frequency. However, most tools do print tables in logs. Parsing them is not complex (see `YosysHQ/arachne-pnr#78 <https://github.com/YosysHQ/arachne-pnr/issues/78>`__), but it needs to be done ad-hoc. Some vendors, such as Vivado, do also
report resource in text logs, but do allow to export them as ``*.xls`` (say CSV) files.

Edalize supports parsing/reading reports from some EDA tools:

* ``edalize.reporting``
* ``edalize.vivado_reporting``
* ``edalize.quartus_reporting``
* ``edalize.ise_reporting``

`SymbiFlow/fpga-tool-perf <https://github.com/SymbiFlow/fpga-tool-perf>`__ does also support extracting results from
Vivado, Yosys, Verilog to Routing and Nextpnr.
Moreover, results are gathered in a Collab Dashboard: `Symbiflow Dashboard GCS <https://colab.research.google.com/drive/1Ny5OZ06R1KVjDykrAQbR0vTsTyiTT1Q7>`__.

`mattvenn/logLUTs <https://github.com/mattvenn/logLUTs>`__ allows parsing yosys and nextpnr logfiles to then plot LUT,
flip-flop and maximum frequency stats.

.. NOTE::
  The fields in resource usage reports can be provided as absolute values or relative to the capacity of the device.
  Therefore, fields in resource reports of OSVR can and should match the ones in `hdl/constraints: template/device.info.yml <https://github.com/hdl/constraints/blob/main/template/device.info.yml#L14-L19>`__.
  Since both OSVR and the device template in hdl/constraints are subject to change yet, we should make them similar to
  existing solutions.
