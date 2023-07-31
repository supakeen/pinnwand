Changelog
#########

``pinnwand`` is Python pastebin software that tried to keep it simple but got
a little more complex.

v1.6.0 (unreleased)
*******************
* Added an initial browser test suite by nekhvoya_.

v1.5.0 (20230727)
*****************
* Change the tab size in the HTML to be 4.
* List lexer endpoint in configuration by ChrisLovering_.
* Reorder Containerfile to optimise caching by ChrisLovering_.
* Logo is now limited on height, allowing for banner-style logos by ChrisLovering_.
* Make environment variable parsing better by accepting `SyntaxError` by ChrisLovering_.
* Allow selecting the default lexer in configuration by ChrisLovering_.
* Ctrl+S now submits pastes by ChrisLovering_.
* `pdm` is now used as the build backend and package solution.
* Containers are now published by CI to GHCR_ by ChrisLovering_.
* Add line range(s) highlight support.
* Add file upload (drag-and-drop or file picker) support.

v1.4.0 (20221127)
*****************
Focus on prettier pages, ease of development, and more defensive posturing. The
`reap` subcommand is now deprecated and instead ran in-process.

A big change is the fact that you can now configure ``pinnwand`` through
environment variables, this makes running in containerized systems a fair bit
easier.

For _packagers_, if you previously shipped timer units for `reap` you can remove
them from your packages in this new version.

* A `Containerfile` is now provided by default. This allows developers to build
  a container.
* If only a single file is pasted the code area for this single file is now
  larger.
* Update major versions of some dependencies.
* Replace the `toml` dependency with the maintained `tomli`.
* Provide example systemd service and timer file for reaping expired pastes.
* The CSS is now generated from SASS, this means that you need `sassc`
  installed if you want to change/rebuild assets.
* The `reap` subcommand is deprecated and will be removed in `1.6`, it now
  runs when the `http` subcommand is running every 1800 seconds instead. The
  example files for `reap` have been removed as well.
* ``pinnwand`` can now be configured through environment variables, these
  start with `PINNWAND_` and are all upper case, then the prefix is removed
  and the key lowercased. This *overwrites* any previously set value.
* `isort` was added to `pre-commit` checks.
* The package layout has been changed to a src-layout, if you are running tests
  with a `pytest < 7` you will need the additional `pytest-srcpaths` plugin.
* Configuration examples have moved to the `etc/` subdirectory.

v1.3.2 (20220711)
*****************
Changing some dependencies to make packaging easier.

v1.3.1 (20220220)
*****************
Bumping some major dependencies to make packaging easier.

* Update major versions of many dependencies.

v1.3.0 (20210522)
*****************
More quality of life and code quality changes.

* Provide archive download of a full paste (#92)
* Add a ``resyntax`` command to rerun lexer over all pastes (#70)
* Paste expiry options now come from the configuration file (#53)
* Convert tabs/enters to indentation, contributed by millefalcon_ (#90)
* Add line highlighting, contributed by erlliam_ (#39)
* Implement naive defensive measures (ratelimiting) (#98)

v1.2.3 (20210109)
*****************
Fixes to packaging and build setup.

* Use poetry-core as build-backend (#101)
* Remove dependency on ``poetry-dynamic-versioning`` as it breaks build.

v1.2.2 (20200829)
*****************
Some longer standing bugs get squatted in pragmatic ways.

* Ensure minimum body width to prevent button falling off (#79)
* Select initial lexer for additional files (#97)

v1.2.1 (20200806)
*****************
Minor updates to the underlying build system for easier packaging by
distros.

* Set build system correctly (#93)
* Update version number in pyproject.toml (#93)

v1.2.0 (20200806)
*****************
New features all around, minor bugfixes, code quality improvements.

* Add language autodetection, contributed by mweinelt_. (#83)
* Provide a hex view for pastes. (#86)
* Add copy to clipboard button. (#87)
* Command line option (-v) to change log level. (#88)
* Make the outline color of the focused form elements be in-line with the
  general highlight color.
* Sum up filesizes and check against paste size. This change now makes the
  paste size limit the total size, not a per-file limit! Adjust your
  configuration accordingly. (#89)
* Add a report link for files that may be problematic, this link will be
  added only if the ``report_email`` field is set to anything than None in the
  configuration file, contributed by Bruce1347_ (#2)
* Expanded testcase coverage for website from 69% to 84% by adding and fixing
  broken testcases.

v1.1.3 (20200620)
*****************
An older bug that occurs rarely resurfaced. This time a bunch of code has been
written to eradicate the problem.

* Race condition in slug_create (#34)
* Fix the millibyte notation.

v1.1.2 (20200608)
*****************
More bugfixes to some things that were either introduced in 1.1.1 or were
lower priority.

* Update our dependencies.
* Use the /static URLs directly for logo/favicon (#85)

v1.1.1 (20200602)
*****************
*The traditional bugfix release for the previous release. No real bugs here
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
.. _Bruce1347: https://github.com/Bruce1347
.. _millefalcon: https://github.com/millefalcon
.. _erlliam: https://github.com/erlliam
.. _ChrisLovering: https://github.com/ChrisLovering
.. _GHCR: https://ghcr.io/supakeen/pinnwand
.. _nekhvoya: https://github.com/nekhvoya
