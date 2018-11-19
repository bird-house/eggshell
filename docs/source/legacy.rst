.. highlight:: shell

==============
Legacy Modules
==============


.. warning:: The legacy modules are deprecated and only kept as reference.

Contents
--------

Eggshell is organized in submodules which are ordered by thematic functionality:

* config
* esgf
* general
* log
* visio

Configuration
-------------

WPS servers often need to specify a number of paths for processes to find data, shapefiles, caches and determine where
outputs are stored. To make sure all birds use the same architecture, eggshell provides a :class:`Paths` class to help
with this.

* eggshell.config

General purpose utilities
-------------------------

Functions and classes in the :mod:`general` module are meant to facilitate typical operations found in
the internal handler method of PyWPS processes.
It also contains general function like datafetch.

* eggshell.general.utils
* eggshell.general.datafetch

Logging
-------

Progress and errors in WPS processes are logged by the server. The initialization of the log file for each process
is done using the :func:`init_process_logger`.

* eggshell.log

Visualisation
-------------

Functions and classes in the :mod:`visual` module are meant to facilitate typical operations to visualize data.
It contains plot functions but also graphic file handing.

* eggshell.visual.visualisation

ESGF Utilities
--------------

This set of utilities is meant to facilitate interactions Earth System Grid Federation data and standards.

* eggshell.esgf.utils
