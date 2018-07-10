
.. eggshell documentation master file, created by
   sphinx-quickstart on Fri Oct 23 10:42:25 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to eggshell's documentation!
====================================

.. _introduction:

Introduction
============

Eggshell is part of the `Birdhouse <http://bird-house.github.io>`_ project. It is meant as a collection of utilities
for bird-house' WPS servers. It covers server configuration, logging, file handling, general netCDF operations and OCGIS-related
functions.

You'll find the full set of utilities in the `API <autoapi/index.html>`_ section.
For the moment, it is only used by FlyingPigeon, but we encourage developers to contribute their own code to eggshell
to make it one of the building blocks of climate related PyWPS services.

Developer guide:
----------------
Eggshell is being used as function library in other WPS services.

Example to import eggshell:

`from eggshell import config`
`import flyingpigeon as fp`
`paths = config.Paths(fp)`
`paths.data`

Contents:
---------

Eggshell is organized in submodules which are ordered by thematic functionality.

.. toctree::
   :caption: Main
   :maxdepth: 2

   config
   esgf
   general
   log
   visio

.. toctree::
   :caption: API Documentation
   :glob:
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
