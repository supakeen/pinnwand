.. _installation:

Installation
############

The common way of installing ``pinnwand`` is by installing from PyPI. I suggest
you to use a virtual environment, these prevent accidentally updating libraries
that your other projects or even your operating system depend on.

For a Debian based distribution installation would look like this:

  .. code:

  python3 -m venv virtual-environment
  virtual-environment/bin/pip install pinnwand

After this you can run ``pinnwand`` in the following way:

  .. code:

  virtual-environment/bin/pinnwand http

This will start the built-in HTTP server on localhost, port 8000, and will
use an in-memory sqlite3 database. This means that your pastes will be gone
when the process exits.

To supply a persistent database, see the :ref:`configuration` bit of the
documentation.

As a container
**************
Containers are published on the GitHub Container Registry, you can run `pinnwand`
from a container:

  .. code:

  docker run -p 8000:8000 ghcr.io/supakeen/pinnwand:latest

You can use :ref:`configuration` through environment variables to configure the
instance. If you want to run against `mysql` or `postgresql` then containers are
provided with the drivers installed: `pinnwand:<version>-psql` and `pinnwand:<version>-mysql`.

Running on boot
***************
If you wish to run ``pinnwand`` as an actual service there's a few more things
we will need to take care of. This bit of the documentation has strong ideas
about how to host a website and doesn't provide commands but general guidance.

This guide only applies to Linux and BSD systems though I am sure it can be
applied to Windows systems as well if you read synonymous terms where
necessary.

Prerequisites
=============

* A HTTP server or proxy such as nginx, haproxy, apache2, etc.

Setup
=====
Start by creating a separate user for your ``pinnwand`` this way we can make
use of the filesystem.

After you've created this user it's now time to setup an environment where
this users code will live. Let's get into their homedir and then perform the
initial section of this document as the user you've just created.

From now on I'll assume you have ``/home/youruser/virtual-environment`` with
``pinnwand`` installed to it.

To have persistence we need to use a persistent database so install your
favourite one and then install its drivers into your virtual environment.

Make sure you create a database with a user and password for pinnwand so that
we can go to the next step.

We'll create a configuration file ``/home/youruser/pinnwand.toml`` with the
following content::

  database_uri = "mysql+pymysql://user:password@host/database"

If you want to configure more then read the :ref:`configuration` section.

Now that we have all of this setup it's time to test out ``pinnwand`` real
quick::

  /home/youruser/virtual-environment/bin/pinnwand --configuration-path /home/youruser/pinnwand.toml http

This should start ``pinnwand`` listening on localhost port 8000. Verify
that this is the case and make sure to paste some data and see if it ends
up in the expected database. If it does you can stop it again and we can
continue to configuring the system.

I will use systemd for this example since it comes pre-installed on most of
our systems nowadays.

Take the example systemd unit file from the repository_ and place it in
``/etc/systemd/system/pinnwand.service``. Then open the file and adjust
the paths to the paths you've created.

After you've done this you can ``systemctl daemon-reload`` and 
``systemctl enable pinnwand.service``. Check its status, if it has come up
verify that you can connect to localhost port 8000 as well and get served
with the ``pinnwand`` pastebin.

Now it's time to configure our webserver to forward requests to ``pinnwand``.
I'll use ``nginx`` in this example but the ideas carry over to anything you
might be using.

Here's an example nginx configuration file::

  server {
          listen 443 ssl ;
          listen [::]:443 ssl ;
  
          root /var/www/empty;
  
          server_name mypastebin.net; # managed by Certbot
  
          add_header X-Xss-Protection "1; mode=block" always;
          add_header X-Content-Type-Options "nosniff" always;
          add_header X-Frame-Options "SAMEORIGIN" always;
          add_header Content-Security-Policy "default-src 'self'" always;
          add_header Strict-Transport-Security "max-age=31536000; includeSubdomains; preload" always;
          add_header Referrer-Policy "no-referrer" always;
          add_header Feature-Policy "accelerometer 'none'; camera 'none'; geolocation 'none'; gyroscope 'none'; magnetometer 'none'; microphone 'none'; payment 'none'; usb 'none'" always;
   
          location / {
                  limit_req zone=mypastebin burst=100;
                  proxy_pass http://127.0.0.1:8000;
                  proxy_set_header Host $host;
                  proxy_set_header X-Forwarded-Proto https;
          }
  
          access_log /home/youruser/mypastebin.net_access.log;
  
          ssl_certificate /etc/letsencrypt/live/mypastebin.net/fullchain.pem; # managed by Certbot
          ssl_certificate_key /etc/letsencrypt/live/mypastebin.net/privkey.pem; # managed by Certbot
  }

Place that file in ``/etc/nginx/sites-enabled/mypastebin.net`` and reload your
nginx. It is important that you pass the Host header and protocol as ``pinnwand``
will use these to build its URLs.

Your pastebin is now up and running!


.. _repository: https://github.com/supakeen/pinnwand
