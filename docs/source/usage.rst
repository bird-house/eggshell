=====
Usage
=====

To use Eggshell in a project:

.. code-block:: python

    import eggshell

Example:

.. code-block:: python

  from eggshell import utils
  tar_output = utils.archive(['tas.nc', 'tasmax.nc'], output_dir=workdir)
