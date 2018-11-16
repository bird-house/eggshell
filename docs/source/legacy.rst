.. highlight:: shell

==============
Legacy Modules
==============

Eggshell is part of the `Birdhouse <http://bird-house.github.io>`_ project. It is meant as a collection of utilities
for bird-house' WPS servers. It covers server configuration, logging, file handling, general netCDF operations and OCGIS-related
functions.

You'll find the full set of utilities in the `API <autoapi/index.html>`_ section.
For the moment, it is only used by FlyingPigeon, but we encourage developers to contribute their own code to eggshell
to make it one of the building blocks of climate related PyWPS services.

Developer guide
---------------

Eggshell is being used as function library in other WPS services.

Example to import eggshell:

.. code-block:: python

  from eggshell import config
  import flyingpigeon as fp
  paths = config.Paths(fp)
  paths.data

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
