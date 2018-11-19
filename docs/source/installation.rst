.. highlight:: shell

============
Installation
============

Install with Conda
------------------

.. image:: https://anaconda.org/birdhouse/birdhouse-eggshell/badges/installer/conda.svg
   :target: https://anaconda.org/birdhouse/birdhouse-eggshell
   :alt: Conda Installer

.. image:: https://anaconda.org/birdhouse/birdhouse-eggshell/badges/version.svg
   :target: https://anaconda.org/birdhouse/birdhouse-eggshell
   :alt: Conda Version

.. image:: https://anaconda.org/birdhouse/birdhouse-eggshell/badges/downloads.svg
   :target: https://anaconda.org/birdhouse/birdhouse-eggshell
   :alt: Conda Downloads

.. image:: https://anaconda.org/birdhouse/birdhouse-eggshell/badges/latest_release_date.svg
   :target: https://anaconda.org/birdhouse/birdhouse-eggshell
   :alt: Conda Release Date

Install `eggshell` with the following command::

  $ conda install -c birdhouse -c conda-forge birdhouse-eggshell

This is the preferred method to install Eggshell, as it will always install the most recent stable release.

.. Stable release
.. --------------
..
.. To install Eggshell, run this command in your terminal:
..
.. .. code-block:: console
..
..     $ pip install eggshell
..
.. This is the preferred method to install Eggshell, as it will always install the most recent stable release.
..
.. If you don't have `pip`_ installed, this `Python installation guide`_ can guide
.. you through the process.
..
.. .. _pip: https://pip.pypa.io
.. .. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


Install from GitHub
-------------------

The sources for Eggshell can be downloaded from the `Github repo`_.

Check out code from the birdy GitHub repo and start the installation:

.. code-block:: console

    $ git clone git://github.com/bird-house/eggshell
    $ cd eggshell
    $ conda env create -f environment.yml
    $ python setup.py install

.. _Github repo: https://github.com/bird-house/eggshell
