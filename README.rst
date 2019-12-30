.. image:: https://travis-ci.org/supakeen/pinnwand.svg?branch=master
    :target: https://travis-ci.org/supakeen/pinnwand

.. image:: https://readthedocs.org/projects/pinnwand/badge/?version=latest
    :target: https://pinnwand.readthedocs.io/en/latest/

.. image:: https://pinnwand.readthedocs.io/en/latest/_static/license.svg
    :target: https://github.com/supakeen/pinnwand/blob/master/LICENSE

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

.. image:: https://img.shields.io/pypi/v/pinnwand
    :target: https://pypi.org/project/pinnwand


pinnwand
########

``pinnwand`` is Python pastebin software that tried to keep it simple but got
a little more complex.

Prerequisites
=============
* Python >= 3.6
* Tornado
* sqlalchemy
* click
* a database driver

Usage
=====

Web
---
Enter text, click "Paste", easy enough.

curl
----
``pinnwand`` has a direct endpoint for ``curl`` users::

  € echo "foo" | curl -X POST http://localhost:8000/curl -F 'raw=<-'
  Paste URL:   http://localhost:8000/OE
  Raw URL:     http://localhost:8000/raw/GU
  Removal URL: http://localhost:8000/remove/GQBHGJYKRWIS34D6FNU6CJ3B5M
  € curl http://localhost:8000/raw/GU
  foo%

This will preselect the ``lexer`` and ``expiry`` arguments to be ``text`` and
``1day`` respectively. You can provide those to change them.

API
---
There is also an API.

More ways to use pinnwand
-------------------------
Various deprecated ways of posting are still supported, don't implement these
for any new software but if you are maintaining old software and want to know
how they used to work you can read our documentation_.

If you do use a deprecated endpoint to post a warning will be shown below any
pastes that are created this way.

Reporting bugs
==============
Bugs are reported best at ``pinnwand``'s `project page`_ on github.

License
=======
``pinnwand`` is distributed under the MIT license. See `LICENSE`
for details.

.. _project page: https://github.com/supakeen/pinnwand
.. _documentationpage: https://pinnwand.readthedocs.io/en/latest/
