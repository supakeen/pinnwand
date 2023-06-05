pinnwand
########

Welcome to the documentation of the ``pinnwand`` pastebin software.

Introduction
============
``pinnwand`` is a straightforward pastebin written for Python 3.8 and up
using the Tornado_ web framework and the sqlalchemy_ ORM. It uses the awesome
pygments_ library for its syntax highlighting.

It's no nonsense and has no features aside from pasting code temporarily.

Usage
=====
You can run the built in ``pinnwand`` HTTP server through the ``pinnwand
http`` command. This will serve up a HTTP server listening on localhost
on port 8000 and use an in-memory sqlite_ database to store data.

If you stop the process then the database will be gone again.

For persistence you'll need to configure ``pinnwand`` to use another
database. See the :ref:`configuration` page for the howto.

Installation
============
You can install ``pinnwand`` from PyPI_ by running pip_ as follows:

  .. code:

  pip install pinnwand

I suggest you use a virtual environment for installation. There are extended
:ref:`installation` instructions available which explain how to do so.

Contributing
============
``pinnwand`` is a place that will accept your first contribution to an open
source project. The preferred place to start out is to visit our GitHub_ page
and look at the issues_ there. If you can solve any of them then you can send
a pull request. I will make sure to review your code.

If you are thinking about contributing a new feature then keep in mind that
``pinnwand`` is trying to stay as small and lean of a project as possible. Open
a ticket first if you have a specific feature in mind.

Table of Contents
=================
.. toctree::

   installation
   configuration
   usage
   tricks
   autodoc
   changelog

.. _GitHub: https://github.com/supakeen/pinnwand
.. _issues: https://github.com/supakeen/pinnwand/issues
.. _PyPI: https://pypi.org
.. _pip: https://pip.pypa.org
.. _tornado: https://www.tornadoweb.org
.. _sqlalchemy: https://www.sqlalchemy.org
.. _pygments: http://pygments.org
.. _sqlite: https://sqlite.org
