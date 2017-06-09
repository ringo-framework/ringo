**********
Deployment
**********

.. _deployment_subpath:

Heroku
======
Ringo applications can be deployed on `Heroko <https://heroku.com>`_.  In this
tutorial it is assumed that you already have your application running in your
virtual environment and you already have a configured account on Heroku. For
more information how to start deploying python application see `the tutorial on Heroku <https://https://devcenter.heroku.com/articles/getting-started-with-python#introduction>`_


0 Initialise a new application::

       # Create a new application named "myapp" with location EU
       heroku apps:create myapp --region eu 

       # Now add a new git remote to the git repo in the output of the last
       # command.
       git remote add heroku $gitrepoatheroku
       # Create a Database
       heroku addons:create heroku-postgresql:hobby-dev --app myapp
       # Make sure sessions work as expected
       heroku features:enable http-session-affinity -a myapp

        
1. Pip freeze your environment. To ensure that your application runs with the
same versions as your local version please store the excact packages using
`pip freeze`::

        pip freeze > requirements.txt
        # Or in case you just want to pin development versions of the
        # ringo-framework
        pip freeze | grep ringo-framework > requirements.txt

2. Prepare your ini file to use a custom port for the server::

        ----------development.ini--------------
        @@ -90,7 +90,7 @@ mail.default_sender =
        [server:main]
        use = egg:waitress#main
        host = 0.0.0.0
        -port = 6543
        +port = %(http_port)s 
        #url_schema = http
        #url_prefix =

 3. Create a shell script `run-heroku.sh` which does the application initialisation and
     start. Make the script executable::

        #!/bin/sh
        python setup.py develop
        ringo-admin db init
        pserve development.ini http_port=$PORT

 4. Create a `.env` file to set some environment variables::

        PORT=6543
        DATABASE_URL=postgres:///$(whoami)

    This file must not be checked into the repository.

 5. Create a `Proc` file which will used by Heroku to start your application::

        web: ./run-heroku.sh


 6. Test your application locally::

        heroku local

 7. Finally add your modfied development.ini and the shell script to the
     repository and push to heroku which will trigger the build process.::

        git add development.ini
        git add run-heroku.sh
        git add Proc 
        git commit -m "Added support for Heroku"

        # Push 
        git push heroku


The last command will trigger the build on the server and shows the URL where
the application is reachable.


====================================================
Running the application in a different path than "/"
====================================================
If the application is hosted in a subpath, than need to make sure that the
`SCRIPT_NAME` and `PATH_INFO` variable are set correct, as both variables are
crucial for a pyramid application to handle the requests and build urls using
the `request.route_*` functions correct. 

Ideally those variables are set before the request enters your application.
This means you do this directly in the serving component. The configuration of
the server components are out of scope of this documentation. Please refer to
the documentation of your server component!

But instead of transforming the variables directly in the server you can also
configure your application to do so. This way you get indepentend from the
server, with the drawback that the information about the path need also be set
in your application configuration. Here comes the following options.

.. rubric:: Use a "prefix" middleware

All requests are routed through another middleware which will modify the
`SCRIPT_NAME` and `PATH_INFO`. Here is how to configure it::

        [filter:paste_prefix]
        use = egg:PasteDeploy#prefix
        prefix = /myapp

        [pipeline:main]
        pipeline =
           paste_prefix
           myapp

        [app:myapp]
        ...

.. rubric:: Build a "composite" application

Originally intended to map differen URLs to different
applications/services (SAS) this can be also used to get the SCRIPT_NAME and
PATH_INFO right. See `Paste documentation for urlmap
<http://pythonpaste.org/deploy/index.html?highlight=urlmap>`_ for more
informations. Here is a short example to get the idea::

        [composite:main]
        use = egg:Paste#urlmap
        # This is the mapping of the path /myapp to an application named
        # myapp 
        /myapp = myapp
        ...

        [app:myapp]
        ...

========
Examples
========

uWSGI & Nginx
-------------
Make sure your have installed the follwing additional packages in your virtualenv:

 * uWSGI
 * PasteDeploy (needed to be able to read the application configuration from
   the ini file)
 * PasteScript (needed to get the logging configured based on the setting in
   the ini file)

Add the following into your ini file::

        [uwsgi]
        master = true
        socket = /tmp/uwsgi.sock
        virtualenv = /path/to/virtualenv

        # PERMISSIONS
        # Make sure that ngnix has permission to read and write to the socket.
        # You can use one or more of the following options:
        #chmod-socket =
        #uid =
        #gid =

        # DAEMONIZE
        # Send it in the background. If daemonize is set it wil log its output
        # into given logfile
        #daemonize = ./uwsgi.log
        #pidfile = ./uwsgi.pid

        # LOGGING
        # paste-logger =
        # Yes, there is no argument for the paste-logger.

Some notes on logging:

1. The Logfile must be writeable for the uWSGI process!

2. Make sure that your logging configuration of the application does not
   contain any place holders like "%(here)s". They are not valid in the scope
   of uWSGI.

3. On default the log of the uwsgi process will contain the requests as same
   as the logging from the application. If you want to separate this I advice
   you to disable to console logging in your pyramid application. Instead use
   a FileLogger which will log the logging in the application to a different
   location. See `Pyramid logging documentation for more details
   <http://docs.pylonsproject.org/projects/pyramid//en/latest/narr/logging.html>`_

Add the following into your ngnix configuration::

        location / {
            uwsgi_pass  unix:///tmp/uwsgi.sock;
            include     uwsgi_params;
        }

Start the uwsgi server by invoking the following command::

        uwsgi --ini-paste--logged development.ini

For debugging purpose I recommend to disable daemonizing in the uWSGI
configuration.


Nginx as Reverse Proxy
----------------------
Add the following into your ngnix configuration::

        location / {
            proxy_set_header        Host $http_host;
            proxy_set_header        X-Real-IP $remote_addr;
            proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header        X-Forwarded-Proto $scheme;
            proxy_pass http://localhost:7450;

        }
