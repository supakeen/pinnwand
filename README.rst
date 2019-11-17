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

``pinnwand`` is Python pastebin software.

Prerequisites
=============
* Python >= 3.6
* Tornado
* sqlalchemy
* click
* a database driver

Usage
=====

Enter text, click "Paste". Easy enough.

Using API is slightly more difficult but certainly recommended for programmatic usage.
``pinnwand`` accepts HTTP POST requests to ``/json/new`` with following body:

::

    {
        "code": "text to send",
        "lexer": "text",
        "expiry": "1day",
        "filename": "source.txt"
    }

``filename`` is optional here.

API will return JSON response with full URL for convenience and ``paste_id, removal_id`` keys.
Use first one to query existing records by GET request to ``/json/show/paste_id``.

To remove existing paste send POST request to ``/json/remove`` with data

::

    {"removal_id": <removal_id>}


Reporting bugs
==============
Bugs are reported best at ``pinnwand``'s `project page`_ on github.

License
=======
``pinnwand`` is distributed under the MIT license. See `LICENSE`
for details.

.. _project page: https://github.com/supakeen/pinnwand
