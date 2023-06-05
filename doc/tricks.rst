.. _tricks:

Tricks
######

Some tricks to make talking to ``pinnwand`` easier.

steck
*****

``steck`` is an in-development command line tool to talk to ``pinnwand``
instances. You can find it on its homepage_ or github_::

  pip install steck

bash alias
**********
You can add the following bash alias to your ``.bashrc``::

  function paste-to-pinnwand() {
      cat $1 | curl -X POST http://localhost:8000/curl -F 'raw=<-'
  }

Make sure to adjust the URL to your favourite pinnwand instance. After this you
can paste files with::

  $ paste-to-pinnwand configuration.html
  Paste URL:   http://localhost:8000/OA
  Raw URL:     http://localhost:8000/raw/CY
  Removal URL: http://localhost:8000/remove/Z4SAXX5Y7QU2NQUT7KCQX4ZGQU


.. _homepage: https://github.com/supakeen/steck
.. _github: https://github.com/supakeen/steck
