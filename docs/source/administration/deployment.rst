**********************
Application Deployment
**********************
Nginx
=====
uWSGI
-----
.. rubric:: Application configuration 

Add the following into your ini file::

        [uwsgi]
        socket = /tmp/uwsgi.sock
        chmod-socket = 777
        master = true
        daemonize = ./uwsgi.log
        pidfile = ./uwsgi.pid
        virtualenv = /path/to/virtualenv

.. rubric:: Nginx configuration 

Add the following into your ngnix configuration::

        location /myapp-prefix {
            include     uwsgi_params;
            uwsgi_param SCRIPT_NAME /myapp-prefix;
            uwsgi_modifier1 30;
            uwsgi_pass  unix:///tmp/uwsgi.sock;
        }

The magic value of 30 tells uWSGI to remove the parameter of SCRIPT_NAME from
the start of PATH_INFO in the request. Pyramid receives the request and
processes it correctly. (According to
https://stackoverflow.com/questions/30768696/uwsgi-how-can-i-mount-a-paste-deploy-pyramid-app/31474384#31474384)

Reverse Proxy
-------------
.. rubric:: Application configuration 

Add the following into your ini file::

        [filter:paste_prefix]
        use = egg:PasteDeploy#prefix
        prefix = myapp-prefix

        [pipeline:main]
        pipeline =
           paste_prefix
           myapp

        [app:myapp]
        use = egg:myapp


.. rubric:: Nginx configuration 

Add the following into your ngnix configuration::

        location /xxx {
            proxy_set_header        Host $http_host;
            proxy_set_header        X-Real-IP $remote_addr;
            proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header        X-Forwarded-Proto $scheme;
            proxy_pass http://localhost:7450;

        }
