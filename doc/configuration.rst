.. _configuration:

Configuration
#############
``pinnwand`` is configured in two ways, one is by arguments and the other is
through a configuration file.

The options available are dependent on the command you're running. You can
always pass the ``--config-path`` argument to ``pinnwand``.

Here is a quick example::

  pinnwand --config-path /tmp/foo.toml http --port 9000

The ``http`` subcommand takes a separate argument ``--port`` to override
the default listening port (8000).

File
----
The configuration file has a bunch more properties to configure ``pinnwand``
with. Here's an example file::

  # Example configuration file for `pinnwand`. Shows what you can adjust. More
  # information can be found at `pinnwand`'s documentation:
  # https://pinnwand.readthedocs.io/en/latest/ or you can file an issue at our
  # GitHub: https://github.com/supakeen/pinnwand
  
  # Database URI to connect to see: https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls
  # if you want to use databases other than sqlite be sure to install the
  # appropriate packages and then format this url to correspond to them.
  database_uri = "sqlite:///:memory:"
  
  # Maximum paste size you want to allow.
  paste_size = 256 * 1024  # in bytes
  
  # The page path is used to find the pages listed in the page_list
  page_path = "/tmp"
  
  # This is the whitelist of files that should exist in the `page_path`
  # configuration directive. `pinnwand` will look for `$file.rst` in the
  # `page_path` directory and serve it at `/$file`.
  page_list = ["about", "removal", "expiry"]
  
  # The footer in raw HTML, shown at the bottom of the page and handy to link to
  # your previously configured pages.
  footer = 'View <a href="//github.com/supakeen/pinnwand" target="_BLANK">source code</a>, the <a href="/removal">removal</a> or <a href="/expiry">expiry</a> stories, or read the <a href="/about">about</a> page.'

This example file shows all currently possible configuration options.
