.. highlight:: shell

=====
Usage
=====

Eggshell is organized in submodules which are ordered by thematic functionality.

To use Eggshell in a project:

.. code-block:: python

    import eggshell

Example:

.. code-block:: python

  from eggshell import utils
  tar_output = utils.archive(['tas.nc', 'tasmax.nc'], output_dir=workdir)


Legacy Modules
--------------

.. warning:: The legacy modules are deprecated and only kept as reference.

The ledacy modules are from the `FlyingPigeon` project and need to be refactored
for common usage. You can find them in the `legacy` package.
Check the documentation in the API reference.
