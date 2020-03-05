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
  paste_size = 262144  # 256kB in bytes

  # Preferred lexers. This list of lexers will appear on top of the dropdown
  # on the website allowing you to preselect commonly used lexers. Note that the
  # names here have to be the identifiers used by pygments, not the human names.
  # If empty no preferred lexers are shown.
  preferred_lexers = []
   
  # The page path is used to find the pages listed in the page_list
  page_path = "/tmp"
  
  # This is the whitelist of files that should exist in the `page_path`
  # configuration directive. `pinnwand` will look for `$file.rst` in the
  # `page_path` directory and serve it at `/$file`.
  page_list = ["about", "removal", "expiry"]
  
  # The footer in raw HTML, shown at the bottom of the page and handy to link to
  # your previously configured pages.
  footer = 'View <a href="//github.com/supakeen/pinnwand" target="_BLANK">source code</a>, the <a href="/removal">removal</a> or <a href="/expiry">expiry</a> stories, or read the <a href="/about">about</a> page.'
  
  # HTML for the 'help text' that can be shown above the paste area, if left
  # empty no help text will be shown.
  paste_help = "<p>Welcome to pinnwand, this site is a pastebin. It allows you to share code with others. If you write code in the text area below and press the paste button you will be given a link you can share with others so they can view your code as well.</p><p>People with the link can view your pasted code, only you can remove your paste and it expires automatically. Note that anyone could guess the URI to your paste so don't rely on it being private.</p>"

This example file shows all currently possible configuration options.
