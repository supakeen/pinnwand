import pytest

from pinnwand import configuration, database, utility


def test_expiries() -> None:
    assert len(configuration.expiries) == 2


def test_guess_language() -> None:
    # python
    assert (
        utility.guess_language(
            """
      import math
      math.ceil(0.5)
    """
        )
        == "python"
    )
    assert (
        utility.guess_language(
            """
      # this is a comment
    """,
            "__init__.py",
        )
        == "python"
    )

    # bash
    assert (
        utility.guess_language(
            """
      #!/usr/bin/bash
      set -euxo pipefail
    """,
            "script.sh",
        )
        == "bash"
    )

    # php
    assert utility.guess_language(
        """
      <?php
      $var = 0.5;
      abs($var);
    """
    ).endswith(
        "php"
    )  # for some reason this is guessed as js+php

    # yaml
    assert (
        utility.guess_language(
            """
      ---
      one:
        two: 3
        four: five
    """,
            "some.yml",
        )
        == "yaml"
    )

    # rst
    assert (
        utility.guess_language(
            """
      Title
      =====

      Subtitle
      --------
      - One
      - Two
    """,
            "doc.rst",
        )
        == "restructuredtext"
    )

    # markdown
    assert (
        utility.guess_language(
            """
      # Title
      ## Subtitle
      [Link](http://www.example.com)
      ~~Strikethrough~~
    """,
            "doc.md",
        )
        == "markdown"
    )


@pytest.mark.parametrize(
    "path,result",
    [
        ("/tmp", "tmp"),
        ("tmp.txt", "tmp"),
        ("tmp.txt.exe", "tmptxt"),
        ("tmp/../../txt.exe.scr", "tmptxtexe"),
    ],
)
def test_filename_clean(path: str, result: str) -> None:
    assert utility.filename_clean(path) == result


def test_slug_context() -> None:
    count = 512

    with utility.SlugContext(True) as slug_context:
        L = [next(slug_context) for _ in range(count)]

    assert len(slug_context._slugs) == count
    assert len(set(L)) == count

    # Make sure none of the generated slugs are already in the database
    # in a very slow way
    with database.session() as session:
        for slug in L:
            assert (
                not session.query(database.Paste)
                .filter_by(slug=slug)
                .one_or_none()
            )
            assert (
                not session.query(database.File)
                .filter_by(slug=slug)
                .one_or_none()
            )


# TODO assert raises RuntimeError for dont_use
# TODO assert raises RuntimeError for database
