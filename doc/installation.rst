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

To supply a persistent database, see the configuration bit of the
documentation.