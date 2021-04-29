from typing import Dict, Optional, List, Any

import logging
import math
import re

from os import urandom
from base64 import b32encode

from pygments.lexers import (
    get_all_lexers,
    guess_lexer,
    guess_lexer_for_filename,
)

from pinnwand import database


log = logging.getLogger(__name__)


def list_languages() -> Dict[str, str]:
    # Start with converting the pygments lexers index into a dict.
    lexers = {
        lexer[1][0]: lexer[0]
        for lexer in get_all_lexers()
        # Guard against the lexer format in Pygments not being all that
        # consistent.
        if len(lexer) > 1 and len(lexer[1])
    }

    # Add autodetection option
    lexers["autodetect"] = "Autodetect"

    # Since dicts are sorted since Python 3.7 (and 3.6 per implementation
    # detail) and the Pygments ordering is a bit inane we sort and turn back
    # into a dict here.
    return dict(sorted(lexers.items(), key=lambda x: x[1]))


GUESS_LANG_OVERRIDES = {"as3": "yaml", "python2": "python"}

GUESS_LANG_IGNORES = ["mime", "tsql"]


def guess_language(raw: str, filename: Optional[str] = None) -> str:
    options = {"stripnl": True}

    # Guess a lexer based on filename and raw text first
    if filename:
        try:
            return str(
                guess_lexer_for_filename(filename, raw, **options).aliases[0]
            )
        except (ValueError, IndexError):
            pass

    # If that didn't work guess lexer just by looking at the raw text
    try:
        language = str(guess_lexer(raw, **options).aliases[0])
    except (ValueError, IndexError):
        # If no lexer was detected, fallback to plain text.
        return "text"

    # These are odd lexers that match far too often, so exclude them.
    if language in GUESS_LANG_IGNORES:
        return "text"

    # Finally check for language overrides and return
    return GUESS_LANG_OVERRIDES.get(language, language)


def hash_create(length: int = 16) -> str:
    return b32encode(urandom(length)).decode("ascii").replace("=", "")


def slug_create(
    auto_scale: bool = True, dont_use: Optional[List[str]] = None
) -> str:
    """Creates a new slug, a slug has to be unique within both the Paste and
    File namespace. These slugs auto-lengthen unless they are specified not
    to."""

    if dont_use is None:
        dont_use = []

    with database.session() as session:
        if auto_scale:
            # We count our new paste as well
            count = (
                session.query(database.Paste).count()
                + session.query(database.File).count()
                + len(dont_use)
                + 1
            )

            # The amount of bits necessary to store that count times two, then
            # converted to bytes with a minimum of 1.

            # We double the count so that we always keep half of the space
            # available (e.g we increase the number of bytes at 127 instead of
            # 255). This ensures that the probing below can find an empty space
            # fast in case of collision.
            necessary = math.ceil(math.log2(count * 2)) // 8 + 1
        else:
            necessary = 16  # 16 bytes should do, right?

        # Now generate random ids in the range with a maximum amount of
        # retries, continuing until an empty slot is found
        tries = 0
        slug = hash_create(necessary)

        # If a slug exists in either the Paste or File namespace create a new
        # one, we also check if we've already generated this slug.
        while any(
            (
                session.query(database.Paste)
                .filter_by(slug=slug)
                .one_or_none(),
                session.query(database.File).filter_by(slug=slug).one_or_none(),
                slug in dont_use,
            )
        ):
            log.debug("slug_create: triggered a collision")
            if tries > 10:
                raise RuntimeError("We exceeded our retry quota on a collision")
            tries += 1
            slug = hash_create(necessary)

        return slug


class SlugContext:
    """Since pinnwand often has to create multiple slugs in one go without
    generating any duplicates we have a context that keeps track of slugs
    already created in the current grouping. See issue #34 for more
    information on the *why*."""

    def __init__(self, auto_scale: bool = True) -> None:
        self._slugs: List[str] = []
        self._auto_scale = auto_scale

    def __enter__(self) -> "SlugContext":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        return None

    def __next__(self) -> str:
        slug = slug_create(
            self._auto_scale,
            self._slugs,
        )
        self._slugs.append(slug)
        return slug


units = [
    (1 << 20, "Mb"),
    (1 << 10, "kb"),
    (1, "b"),
]


def size_postfix(count: int) -> str:
    for f, p in units:
        if count > f:
            break

    return f"{count/f:.0f}{p}"


def filename_clean(filename: str) -> str:
    """Try to clean a filename for safe consumption as much as we can. These
    filenames are sent to other users."""

    # If there's a dot we remove the suffix
    if "." in filename:
        filename = filename.rsplit(".", 1)[0]

    # Replace anything that could be misinterpreted by an operating system
    return re.sub(r"[^A-Za-z0-9-_]", "", filename)
