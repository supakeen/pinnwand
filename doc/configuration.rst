.. _configuration:

Configuration
#############
``pinnwand`` is configured in three ways, one is by arguments and the other is
through a configuration file and the last is by environment variables.

The options available are dependent on the command you're running. You can
always pass the ``--configuration-path`` argument to ``pinnwand``.

Here is a quick example::

  pinnwand --configuration-path /tmp/foo.toml http --port 9000

The ``http`` subcommand takes a separate argument ``--port`` to override
the default listening port (8000).

Any value in this file can be overridden by passing `PINNWAND_DATABASE_URI` in
the environment (for example).

File
****
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
  # The keys returned by /api/v1/lexer are an exhaustive list of supported lexers.
  # If empty no preferred lexers are shown.
  preferred_lexers = []

  # The lexer selected by default when creating a new paste.
  # Similar to preferred_lexers, only supports lexer identifiers used by pygments.
  default_selected_lexer = "text"

  # Logo path, used to render your logo. If left out the default logo will be
  # used. This file must be a png file.
  # logo_path = "/path/to/a/file.png"
  
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

  # Email used for file reporting. If the value is not None then a href with a mailto link will be added to every paste page thus allowing the users to report pastes that may need removal.
  report_email = "maintainer@example.com"

  # Expiries are given by a name and their duration in seconds, if you want to do
  # 'forever' set a really large number...
  expiries.1hour = 3600
  expiries.1day = 86400
  expiries.1week = 604800
  
  # These are application level ratelimits, if you use proxies for your pinnwand
  # instance you should set limits there as well. These limits describe a token
  # bucket and are per-IP. 
  #
  # The capacity is how many tokens there are available, the consumption is how
  # many tokens are used by an action and the refill is how many tokens are added
  # per second. So the read bucket below allows a burst of a 100 reads then another
  # 2 per second.
  ratelimit.read.capacity = 100
  ratelimit.read.consume = 1
  ratelimit.read.refill = 2
  
  ratelimit.create.capacity = 2
  ratelimit.create.consume = 2
  ratelimit.create.refill = 1
  
  ratelimit.delete.capacity = 2
  ratelimit.delete.consume = 2
  ratelimit.delete.refill = 1
  
  # pinnwand uses a naive anti-spam measure where a regex is ran over the text
  # that is pasted. It then checks how large a percentage of the incoming bytes
  # consist of links. If that percentage is larger than the number below the
  # paste is denied. Set to a 100 to disable.
  spamscore = 50

Options
*******

database_uri
============
A URI as accepted by sqlalchemy for the database to use.

Default: ``sqlite:///:memory```

paste_size
==========
Maximum size of a formatted paste. This includes the HTML as generated by
pygments. The size should be supplied in bytes.

Default: ``262144`` (256 kB).

preferred_lexers
================
The lexers that are shown on the homepage above all other lexers. This allows
you to customize your homepage to the most-used lexers for your users.

Leaving this list empty will not show any preferred lexers. The lexer names
in this list must be supported by pygments.

Default: ``[]``.

default_selected_lexer
======================
The lexer that is selected by default when creating a new paste.

Default: ``text``

logo_path
=========
Path to a custom logo file. Needs to be readable by the user ``pinnwand`` runs
as. Leave out of the configuration file if you want to use the default logo.

Default: ``unset``.

page_path
=========
A filesystem path where pages listed in ``page_path`` are looked up in. If
unset the default ``pinnwand`` path will be used.

Default: ``unset``.

page_list
=========
List of static text pages. If set these pages will be looked up in the
``page_path`` variable. These files should exist in ``page_path`` with a
``.rst`` suffix.

Default: ``["about", "removal", "expiry"]``

footer
======
HTML to render in the footer.

Default: ``bunch of html``

paste_help
==========
HTML to render above the new paste page to help users on how to use your
instance.

Default: ``bunch of html``

report_email
============

An email address that allows users to report a paste that may need removal or
edition.

Default: ``None``

expiries
========
Several expiries exist, these are shown in the drop down by name and are used
for reaping pastes. They are denoted in seconds and the keys are free to choose.


expiries.1hour
^^^^^^^^^^^^^^
Default: `3600`

expiries.1day
^^^^^^^^^^^^^
Default: `86400`

expiries.1week
^^^^^^^^^^^^^^
Default: `604800`

ratelimit
=========
These are application level ratelimits, if you use proxies for your pinnwand
instance you should set limits there as well. These limits describe a token
bucket and are per-IP. 

The capacity is how many tokens there are available, the consumption is how
many tokens are used by an action and the refill is how many tokens are added
per second. So the read bucket below allows a burst of a 100 reads then another
2 per second.

ratelimit.read.capacity
^^^^^^^^^^^^^^^^^^^^^^^
Default: `100`

ratelimit.read.consume
^^^^^^^^^^^^^^^^^^^^^^
Default: `1`

ratelimit.read.refill
^^^^^^^^^^^^^^^^^^^^^
Default: `2`

ratelimit.create.capacity
^^^^^^^^^^^^^^^^^^^^^^^^^
Default: `2`

ratelimit.create.consume
^^^^^^^^^^^^^^^^^^^^^^^^
Default: `2`

ratelimit.create.refill
^^^^^^^^^^^^^^^^^^^^^^^
Default: `1`

ratelimit.delete.capacity
^^^^^^^^^^^^^^^^^^^^^^^^^
Default: `2`

ratelimit.delete.consume
^^^^^^^^^^^^^^^^^^^^^^^^
Default: `2`

ratelimit.delete.refill
^^^^^^^^^^^^^^^^^^^^^^^
Default: `1`

spamscore
=========
pinnwand uses a naive anti-spam measure where a regex is ran over the text
that is pasted. It then checks how large a percentage of the incoming bytes
consist of links. If that percentage is larger than the number below the
paste is denied. Set to a 100 to disable.

Default: `50`
