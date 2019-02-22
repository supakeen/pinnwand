Configuration
#############

``unchaind`` uses the TOML_ configuration language. It also requires a
configuration file to start. It is handy to familiarize yourself with the TOML
configuration language but not necessary as one can go off the provided example
file as well.

The configuration is formatted in multiple sections which each do different
things. Some options are configured globally:

home_system
-----------
Used for route finding. This is currently an EVE system ID.

Mappers
=======
The mappers section refer to the mappers from the features. In short these
allow you to connect common EVE Online wormhole space mappers to be integrated
with ``unchaind`` so they can be used by other parts of ``unchaind``.

A generic mapper block looks like:::

  [[mapper]]
  type = "siggy"
  username = "username"
  password = "password"
  home_system = 31002238

The values are semi-obvious but here they are written out:

type
----
The type of mapper. Refer to the mappers section for those supported.

username
--------
A username for the mapper, make sure this user has access to the appropriate
maps that you want ``unchaind`` to use.

password
--------
The password for the username you provided.

Notifiers
=========
Notifiers are the meat and bones of what ``unchaind`` can send to your outputs.
Their configuration is very dependent on the type of notifier they are attached
to but there are some generic things. You can find all supported notifier
types in the notifiers section.

type
----
The type of notifier this is, find them in the notifiers section.

webhook
-------
Some types of notifier have a webhook URL.

subscribes_to
-------------
Subscribe to a certain event. Find these in the events section.

notifier.filter
---------------
Filters related to the event chosen. All of these can be found in the events
section of the documentation.


.. _toml: https://github.com/toml-lang/toml
