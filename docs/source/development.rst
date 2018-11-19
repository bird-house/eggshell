.. highlight:: shell

===========
Development
===========


Get Started!
------------

Ready to contribute? Here's how to set up `eggshell` for local development.

1. Fork the `eggshell` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/eggshell.git

3. Install your local copy into a conda_ environment. Assuming you have conda installed, this is how you set up your fork for local development::

    $ cd eggshell/
    $ conda env create -f environment.yml
    $ conda activate eggshell
    $ pip install -r requirements_dev.txt # install develop tools like pytest
    $ python setup.py develop

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the
   tests::

    $ flake8
    $ pytest

   Or use the Makefile::

     $ make lint
     $ make test
     $ make test-all

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

.. _conda: https://conda.io/docs/

Write Documentation
-------------------

You can find the documentation in the `docs/source` folder. To generate the Sphinx
documentation locally you can use the `Makefile`::

  $ make docs

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 2.7, 3.6 and 3.7, and for PyPy. Check
   https://travis-ci.org/bird-house/eggshell/pull_requests
   and make sure that the tests pass for all supported Python versions.

Tips
----

To run a subset of tests::

$ pytest tests.test_utils


Deploying
---------

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in CHANGES.rst).
Then run::

$ bumpversion patch # possible: major / minor / patch
$ git push
$ git push --tags

Travis will then deploy to PyPI if tests pass.
