.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/ringo-framework/ringo/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
and "help wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

Ringo could always use more documentation, whether as part of the
official Ringo docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/ringo-framework/ringo/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

.. _bootstrapenv:

Get Started!
------------

Ready to contribute? Here's how to set up `ringo` for local development.

1. Bootstrap a ringo development environment::

    $ apt-get install git
    $ curl -O https://raw.githubusercontent.com/ringo-framework/ringo/master/bootstrap-dev-env.sh
    $ sh bootstrap-dev-env.sh ringo

This command will generate a folder which includes some subfolder for the
virtualenv and needed libraries::

        ringo
        |-- env
        |   |-- ...
        |   `-- bin
        `-- lib
            |-- brabbel
            |-- formbar
            `-- ringo

The general layout of an development environment looks like this::

 * appname: Root folder of the environment. Usually named with the name of the
   application.
 * lib: Folder for libraries. To be able to have differen versions of the core
   libraries ringo and formbar I recommend to install the development version
   for each application.
 * env: The virtual python environment.

2. Activate your virtualenv::

    $ cd ringo
    $ source env/bin/active

3. Create a branch for local development::

    $ cd lib/ringo
    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

4. When you're done making changes, check that your changes pass flake8 and the tests, including testing other Python versions with tox::

    $ flake8 ringo tests
    $ python setup.py test or py.test
    $ tox

   To get flake8 and tox, just pip install them into your virtualenv.

5. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 2.6, 2.7, 3.3, 3.4 and 3.5, and for PyPy. Check
   https://travis-ci.org/ringo-framework/ringo/pull_requests
   and make sure that the tests pass for all supported Python versions.

Tips
----

To run a subset of tests::

$ py.test tests.test_ringo

