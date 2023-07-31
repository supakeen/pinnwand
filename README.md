![pinnwand logo, a rabbit](https://pinnwand.readthedocs.io/en/latest/_static/logo-doc.png)

# pinnwand

[![](https://readthedocs.org/projects/pinnwand/badge/?version=latest)](https://pinnwand.readthedocs.io/en/latest/) [![](https://pinnwand.readthedocs.io/en/latest/_static/license.svg)](https://github.com/supakeen/pinnwand/blob/master/LICENSE) [![](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black) [![](https://img.shields.io/pypi/v/pinnwand)](https://pypi.org/project/pinnwand) [![](https://codecov.io/gh/supakeen/pinnwand/branch/master/graph/badge.svg)](https://codecov.io/gh/supakeen/pinnwand)

## About

`pinnwand` is Python pastebin software that tried to keep it simple but got
a little more complex.

Prerequisites
=============
* Python >= 3.8
* Tornado
* sqlalchemy
* click
* docutils
* tomli
* pygments-better-html
* a database driver

Usage
=====

Web
---
Enter text, click "Paste", easy enough.

steck
-----
[steck](https://github.com/supakeen/steck) is a command line client to pinnwand instances:

```
€ pip install --user steck
...
€ steck paste *
You are about to paste the following 7 files. Do you want to continue?
- LICENSE
- mypy.ini
- poetry.lock
- pyproject.toml
- README.rst
- requirements.txt
- steck.py

Continue? [y/N] y

Completed paste.
View link:    https://localhost:8000/W5
Removal link: https://localhost:8000/remove/TS2AFFIEHEWUBUV5HLKNAUZFEI
```

curl
----
`pinnwand` has a direct endpoint for `curl` users:

```
€ echo "foo" | curl -X POST http://localhost:8000/curl -F 'raw=<-'
Paste URL:   http://localhost:8000/OE
Raw URL:     http://localhost:8000/raw/GU
Removal URL: http://localhost:8000/remove/GQBHGJYKRWIS34D6FNU6CJ3B5M
€ curl http://localhost:8000/raw/GU
foo%
```

This will preselect the `lexer` and `expiry` arguments to be `text` and
`1day` respectively. You can provide those to change them.

API
---
`pinnwand` provides a straight forward JSON API, here's an example using the
common requests library:

```
>>> requests.post(
...     "http://localhost:8000/api/v1/paste",
...     json={
...             "expiry": "1day",
...             "files": [
...                     {"name": "spam", "lexer": "python", "content": "eggs"},
...             ],
...     }
... ).json()
{'link': 'http://localhost:8000/74', 'removal': 'http://localhost:8000/remove/KYXQLPZQEWV2L4YZM7NYGTR7TY'}
```

More information about this API is available in the [documentation](https://pinnwand.readthedocs.io/en/latest/).


More ways to use pinnwand
-------------------------
Various deprecated ways of posting are still supported, don't implement these
for any new software but if you are maintaining old software and want to know
how they used to work you can read our documentation_.

If you do use a deprecated endpoint to post a warning will be shown below any
pastes that are created this way.

Reporting bugs
==============
Bugs are reported best at `pinnwand`'s [project page](https://github.com/supakeen/pinnwand) on github. If you just
want to hang out and chat about `pinnwand` then I'm available in the
`#pinnwand` channel on Freenode IRC.

License
=======
`pinnwand` is distributed under the MIT license. See `LICENSE`
for details.

History
=======
This pastebin has quite a long history which isn't reflected entirely in its
repository.

Testing
=======
There are 2 types of tests available to verify that the application still works correctly after the changes:
* unit test
* browser e2e tests

Unit tests are run by pytest by default when executing (the browser tests will be skipped)
```
€ pytest
```
If you'd like to run browser tests you need to pass the `--e2e` option to the pytest command.
```
€ pytest --e2e
```
The browser tests are executed by [Playwright](https://playwright.dev/python/docs/intro).
The tests by default will be run in the headless mode. 
But it's possible to run them in the headed mode as well to be able to observe the execution of the tests.
For that, you just need to pass the `--headed` option to the `pytest --e2e` command:
```
€ pytest --e2e --headed
```
