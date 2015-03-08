*****************
Environment Setup
*****************

Environment layout
==================
The general layout of an development environment looks like this::

        / appname
        |-lib
        | |-ringo
        | |-formbar
        |-src
        \-env

 * appname: Root folder of the environment. Usually named with the name of the
   application.
 * lib: Folder for libraries. To be able to have differen versions of the core
   libraries ringo and formbar I recommend to install the development version
   for each application.
 * src: The source folder of your application.
 * env: The virtual python environment.

.. _development_env:

Create development environment
==============================
This section will give you an example how create a development environment.

The example shows my personal way of organising the code which was quite
handy over the last time.

First I recommend to setup a dedicated development environment based on a
`Virtual Python Environment <https://pypi.python.org/pypi/virtualenv>`_ for
each application (including ringo itself) you want to develop::


        cd /path/to/your/development/root/folder
        # create a folder for the application you like to create.
        mkdir <yourappname>
        cd <yourappname>

        # Create and activate a new virtual environment and do all following
        steps with # the activaed virtual env.
        virtualenv --no-site-packages env
        source env/bin/activate

        # create a subfolder for all libs external libs.
        mkdir lib
        cd lib
        # Install a development version of brabbel
        hg clone https://bitbucket.org/ti/brabbel
        cd formbar
        # Install a development version of formbar.
        hg clone https://bitbucket.org/ti/formbar
        cd formbar
        python setup.py develop
        # Install a development version of ringo.
        hg clone https://bitbucket.org/ti/ringo
        cd ringo
        python setup.py develop
        cd ..

We are almost finished. The next step is either to create a new application
with this environment or get an existing application.

.. _create_ringo_based_application:

Working on an existing application
==================================
Simply clone the exiting application::

        # Change to your development folder
        cd <yourappname>
        # Get the application
        hg clone https://bitbucket/ti/plorma
        # Rename the folder to meet the naming convention
        mv plorma src
        cd src
        python setup.py develop
