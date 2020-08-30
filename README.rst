.. image:: https://pinnwand.readthedocs.io/en/latest/_static/logo-readme.png
    :width: 950px
    :align: center

pinnwand
########

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

.. image:: https://codecov.io/gh/supakeen/pinnwand/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/supakeen/pinnwand

About
=====

``pinnwand`` is Python pastebin software that tried to keep it simple but got
a little more complex.

Prerequisites
=============
* Python >= 3.6
* Tornado
* sqlalchemy
* click
* docutils
* toml
* pygments-better-html
* a database driver

Usage
=====

Web
---
Enter text, click "Paste", easy enough.

steck
-----
steck_ is a command line client to pinnwand instances::

  € pip install --user steck
  ...
  € steck paste *
  You are about to paste the following 7 files. Do you want to continue?
   - LICENSE
   - mypy.ini
   - poetry.lock
   - pyproject.toml
   - README.rst
   - requirements.txt
   - steck.py

  Continue? [y/N] y

  Completed paste.
  View link:    https://localhost:8000/W5
  Removal link: https://localhost:8000/remove/TS2AFFIEHEWUBUV5HLKNAUZFEI

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
``pinnwand`` provides a straight forward JSON API, here's an example using the
common requests library::

  >>> requests.post(
  ...     "http://localhost:8000/api/v1/paste",
  ...     json={
  ...             "expiry": "1day",
  ...             "files": [
  ...                     {"name": "spam", "lexer": "python", "content": "eggs"},
  ...             ],
  ...     }
  ... ).json()
  {'link': 'http://localhost:8000/74', 'removal': 'http://localhost:8000/remove/KYXQLPZQEWV2L4YZM7NYGTR7TY'}

More information about this API is available in the documentation_.


More ways to use pinnwand
-------------------------
Various deprecated ways of posting are still supported, don't implement these
for any new software but if you are maintaining old software and want to know
how they used to work you can read our documentation_.

If you do use a deprecated endpoint to post a warning will be shown below any
pastes that are created this way.

Reporting bugs
==============
Bugs are reported best at ``pinnwand``'s `project page`_ on github. If you just
want to hang out and chat about ``pinnwand`` then I'm available in the
``#pinnwand`` channel on Freenode IRC.

License
=======
``pinnwand`` is distributed under the MIT license. See `LICENSE`
for details.

History
=======
This pastebin has quite a long history which isn't reflected entirely in its
repository.

.. _project page: https://github.com/supakeen/pinnwand
.. _documentation: https://pinnwand.readthedocs.io/en/latest/
.. _steck: https://supakeen.com/project/steck
