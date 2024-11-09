Command Line Interfaces
#######################

When installed via PIP, the command line program ``pyedaa-reports`` is registered in the Python installation's
``Scripts`` directory. Usually this path is listed in ``PATH``, thus this program is globally available after
installation.

The program is self-describing. Use ``pyedaa-reports`` without parameters or ``pyedaa-reports help`` to see all
available common options and commands. Each command has then it's own help page for command specific options, which can
be listed by calling ``pyedaa-reports <cmd> -h`` or ``pyedaa-reports help <cmd>``. The ``pyedaa-reports``'s version and
license information is shown by calling ``pyedaa-reports version``.

.. _References:cli:

.. autoprogram:: pyEDAA.Reports.CLI:Application().MainParser
  :prog: pyedaa-reports
  :groups:
