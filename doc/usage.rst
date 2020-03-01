.. _usage:

Usage
#####

APIs
****

The ``pinnwand`` project has several 'APIs' and I use the word loosely here
as some of these were never meant to be used as an API but they are being used
as such.

Currently the only officially supported APIs are the ``v1`` and ``curl``, the
others are deprecated. That doesn't mean they'll disappear anytime soon but is
an indication to users that their tooling is using endpoints that could be using
the newer API which has more features such as multiple files.

Each API has several endpoints and you can find their usecases here.

v1
==
The ``v1`` API supports all current features of ``pinnwand`` including multi
file pastes. It currently has three endpoints. All of which take JSON bodies
as their inputs. Examples are provided with the requests library.

/api/v1/paste
-------------
This is the main endpoint for creating new pastes. It takes a JSON body as its
input for a ``POST`` request, the JSON body must contain the following fields:

expiry
  The expiry for this paste, you can list the expiries that are valid on the
  ``/api/v1/expiry`` endpoint.

files
  A list of file objects.

A file object needs the following fields:

lexer
  The lexer to use for this file, you can retrieve a list of valid lexers from
  the ``/api/v1/lexer`` endpoint.

content
  Content of the file, the max filesize depends on the configuration of the
  ``pinnwand`` instance you are talking to.

name (optional)
  If applicable add a ``name`` field to set the filename of the file.

Here's an example with the ``requests`` library that ticks all the above boxes::

  >>> requests.post(
  ...     "http://localhost:8000/api/v1/paste",
  ...     json={
  ...             "expiry": "1day",
  ...             "files": [
  ...                     {"name": "spam", "lexer": "python", "content": "eggs"},
  ...             ],
  ...     }
  ... ).json()
  {'link': 'http://localhost:8000/74', 'removal': 'http://localhost:8000/remove/KYXQLPZQEWV2L4YZM7NYGTR7TY'}a

To remove a paste a ``GET`` request to the ``removal`` URL returned is
sufficient.


/api/v1/lexer
-------------
An endpoint to list all lexers available in the ``pinnwand`` instance whose
API you're using. The keys returned are valid for the ``lexer`` field::

  >>> requests.get("http://localhost:8000/api/v1/lexer")
  {'abap': 'ABAP', 'apl': 'APL', 'abnf': 'ABNF', ...}


/api/v1/expiry
--------------
Used to list all valid expiries to be used in the ``expiry`` field. These
expiries are dependent on the configuration of the ``pinnwand`` instance that
you're talking to::

  >>> requests.get("http://localhost:8000/api/v1/expiry")
  {'1day': '1 day, 0:00:00', '1week': '7 days, 0:00:00'}

curl
====
The ``curl`` API provides a handy one-stop for using ``curl`` to submit a file
to ``pinnwand`` quickly. It doesn't support multi file but it does give you
a quick way to create a shell alias for pasting to a ``pinnwand`` instance.

See :ref:`tricks` for such a shell alias.

/curl
-----

This is an endpoint that only takes ``POST`` requests, the body should be
formencoded, ``curl`` will handle this for you. The following other parameters
are available:

expiry
  The expiry for this paste, if not supplied ``1day`` is selected. Valid
  expiries depend on the configuration of the ``pinnwand`` instance.

lexer
  The lexer to use for this paste. If not supplied ``text`` is selected. Valid
  lexers depend on the configuration of the ``pinnwand`` instance but are
  generally those provided by ``pygments``.

An example of where the ``/curl`` endpoint comes in handy::

  € echo "foo" | curl -X POST http://localhost:8000/curl -F 'raw=<-'
  Paste URL:   http://localhost:8000/OE
  Raw URL:     http://localhost:8000/raw/GU
  Removal URL: http://localhost:8000/remove/GQBHGJYKRWIS34D6FNU6CJ3B5M
  € curl http://localhost:8000/raw/GU
  foo%


deprecated-web
==============

In the beginning there was only the ``/`` endpoint so people started posting
to it directly. This endpoint is really the worst one to use as it doesn't give
you any useful information back in an easily readable format. You'll have to
parse the data out of the response and form your own URLs for for example the
``removal`` URL.

/
-
When you throw a ``POST`` request at this endpoint it requires the following
parameters as form encoded data:

code
  The code to paste.

lexer
  The lexer to use. Valid lexers depend on the configuration of the
  ``pinnwand`` instance but are generally those provided by ``pygments``.

expiry
  The expiry for this paste. Valid expiries depend on the configuration of the
  ``pinnwand`` instance.

The response of this endpoint is a redirect to the URL at which the newly
created paste can be viewed. The removal ID is in the ``Set-Cookie`` header on
this response, you'll have to format it into a URL ``/remove/{id}`` yourself.

Here's an example using ``curl`` to send data to this endpoint::

  € curl -v http://localhost:8000/ -d 'code=foo' -d 'lexer=c' -d 'expiry=1day'
  *   Trying ::1...
  * TCP_NODELAY set
  * Connected to localhost (::1) port 8000 (#0)
  > POST / HTTP/1.1
  > Host: localhost:8000
  > User-Agent: curl/7.58.0
  > Accept: */*
  > Content-Length: 28
  > Content-Type: application/x-www-form-urlencoded
  >
  * upload completely sent off: 28 out of 28 bytes
  < HTTP/1.1 302 Found
  < Server: TornadoServer/6.0.3
  < Content-Type: text/html; charset=UTF-8
  < Date: Sun, 01 Mar 2020 13:03:24 GMT
  < Location: /SA
  < Content-Length: 0
  < Set-Cookie: removal=U35UORIU6SEEGRICOJFNIAGZBM; Path=/SA
  <
  * Connection #0 to host localhost left intact


deprecated-api
==============
``pinnwand`` provided a json based API for the bpython_ project early on, this
API does not support multi file pastes but is in common use.

Of special note is that these endpoints do not serve json in their error
responses so you should not blindly try to parse their results.

/json/new
---------

/json/remove
------------

/json/show/([A-Z2-7]+)(?:#.+)?
------------------------------

/json/lexers
------------

/json/expiries
--------------

.. _bpython: https://bpython-interpreter.org/
