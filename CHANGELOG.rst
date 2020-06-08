Changelog
#########

``pinnwand`` is Python pastebin software that tried to keep it simple but got
a little more complex.

v1.2.0 (unreleased)
*******************
New features all around.

* Add language autodetection, contributed by mweinelt_. (#83)

v1.1.2 (20200608)
*****************
More bugfixes to some things that were either introduced in 1.1.1 or were
lower priority.

* Update our dependencies.
* Use the /static URLs directly for logo/favicon (#85)

v1.1.1 (20200602)
*****************
The traditional bugfix release for the previous release. No real bugs here
but something to prevent CSS changes from not being loaded.

* Prevent browsers from aggressively caching (#74)

v1.1.0 (20200524)
*****************
The 1.1.0 release is focused on new features to improve ease of use.

* Provide a button to toggle line wrapping, contributed by Kwpolska_. (#51)
* Auto-delete pastes on view when they've expired. (#63)
* Include original filename if given for paste downloads (#26)
* Provide a button to toggle opposite colorschemes. (#69)
* For pastes the first file will now have the same slug as the paste itself,
  this allows for users to replace part of the URL to get to raw and download
  links. (#64)
* Allow access to raw and download handlers through /:id/(raw|download) to
  let people more easily change the URL by hand when linked to a paste (#72)
* Consolidate separate pygments and pinnwand stylesheets into one.

v1.0.2 (20200408)
*****************

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
.. _mweinelt: https://github.com/mweinelt
