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

  € curl -X POST 'http://localhost:8000/curl' -d 'lexer=python' -d 'raw=foo' -d 'expiry=1day'
  Paste URL:   http://localhost:8000/ZM
  Removal URL: http://localhost:8000/remove/ZR2VVYDAQKMZ356KN6FOQE4C4Q
  €

api
---
There is also an API.

Reporting bugs
==============
Bugs are reported best at ``pinnwand``'s `project page`_ on github.

License
=======
``pinnwand`` is distributed under the MIT license. See `LICENSE`
for details.

.. _project page: https://github.com/supakeen/pinnwand
