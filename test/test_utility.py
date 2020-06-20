import pytest

from pinnwand import utility


def test_expiries() -> None:
    assert len(utility.expiries) == 2


def test_guess_language() -> None:
    # python
    assert utility.guess_language("""
      import math
      math.ceil(0.5)
    """) == "python"
    assert utility.guess_language("""
      # this is a comment
    """, "__init__.py") == "python"

    # bash
    assert utility.guess_language("""
      #!/usr/bin/bash
      set -euxo pipefail
    """, "script.sh") == "bash"

    # php
    assert utility.guess_language("""
      <?php
      $var = 0.5;
      abs($var);
    """).endswith("php")  # for some reason this is guessed as js+php

    # yaml
    assert utility.guess_language("""
      ---
      one:
        two: 3
        four: five
    """, "some.yml") == "yaml"

    # rst
    assert utility.guess_language("""
      Title
      =====

      Subtitle
      --------
      - One
      - Two
    """, "doc.rst") == "rst"

    # markdown
    assert utility.guess_language("""
      # Title
      ## Subtitle
      [Link](http://www.example.com)
      ~~Strikethrough~~
    """, "doc.md") == "md"


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
