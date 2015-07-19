**********************
Application Deployment
**********************

.. _deployment_subpath:

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

To get thet logging right, you need to make sure that your logging
configuration of the application does not contain any place holders like
"%(here)s". They are not valid in the scope of uWSGI.
On default the log of the uwsgi process will contain the requests as same as
the logging from the application. If you want to seperate this I advice you to
disable to console logging in your pyramid application. Instead use a
FileLogger which will log the logging in the application to a different
location. See `Pyramid logging documentation for more details <http://docs.pylonsproject.org/projects/pyramid//en/latest/narr/logging.html>`_

Add the following into your ngnix configuration::

        location / {
            uwsgi_pass  unix:///tmp/uwsgi.sock;
            include     uwsgi_params;
        }

Start the uwsgi server by invoking the following command::

        uwsgi --ini-paste--logged development.ini

You can disable daemonizing for debugging purpose.


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
