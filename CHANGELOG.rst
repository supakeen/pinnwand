Changelog
#########

``pinnwand`` is Python pastebin software that tried to keep it simple but got
a little more complex.

v1.1.0 (unreleased)
*******************
The 1.1.0 release is focused on new features to improve ease of use.

* Provide a button to toggle line wrapping, contributed by Kwpolska_. (#51)
* Auto-delete pastes on view when they've expired. (#63)
* Include original filename if given for paste downloads (#26)

v1.0.2 (unreleased)
===================

Bugfix release to deal with spaces at the front of pastes being eaten leading
to wonky things when people paste pre-indented code.

* something eats spaces at the start of a paste (#68)

v1.0.1 (20200326)
*****************

A quick bugfix release to depend on a newer version of ``pygments-better-html``.

* Empty lines don't survive copy/paste. (#67)

v1.0.0 (20200323)
*****************

After a period of darkness (changelog-wise) version 1.0.0 was released and this
changelog created.

.. _Kwpolska: https://github.com/Kwpolska
