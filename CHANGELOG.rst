Changelog
#########

``pinnwand`` is Python pastebin software that tried to keep it simple but got
a little more complex.


v1.0.2 (unreleased)
===================

Bugfix release to deal with spaces at the front of pastes being eaten leading
to wonky things when people paste pre-indented code.

* #68_: something eats spaces at the start of a paste

v1.0.1 (20200326)
=================

A quick bugfix release to depend on a newer version of ``pygments-better-html``.

* #67_: Empty lines don't survive copy/paste

v1.0.0 (20200323)
*******************

After a period of darkness (changelog-wise) version 1.0.0 was released and this
changelog created.

.. _67: https://github.com/supakeen/pinnwand/issues/67
.. _68: https://github.com/supakeen/pinnwand/issues/68
