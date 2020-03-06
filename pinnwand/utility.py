from typing import Dict

import logging
import math

from os import urandom
from base64 import b32encode
from datetime import timedelta

from pygments.lexers import get_all_lexers

from pinnwand import database


log = logging.getLogger(__name__)


def list_languages() -> Dict[str, str]:
    # Start with converting the pygments lexers index into a dict.
    lexers = {lexer[1][0]: lexer[0] for lexer in get_all_lexers()}

    # Since dicts are sorted since Python 3.7 (and 3.6 per implementation
    # detail) and the Pygments ordering is a bit inane we sort and turn back
    # into a dict here.
    return dict(sorted(lexers.items(), key=lambda x: x[1]))


expiries = {"1day": timedelta(days=1), "1week": timedelta(days=7)}


def hash_create(length: int = 16) -> str:
    return b32encode(urandom(length)).decode("ascii").replace("=", "")


def slug_create(auto_scale: bool = True) -> str:
    """Creates a new slug, a slug has to be unique within both the Paste and
       File namespace. These slugs auto-lengthen unless they are specified not
       to."""

    with database.session() as session:
        if auto_scale:
            # We count our new paste as well
            count = (
                session.query(database.Paste).count()
                + session.query(database.File).count()
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
        # one.
        while any(
            (
                session.query(database.Paste)
                .filter_by(slug=slug)
                .one_or_none(),
                session.query(database.File).filter_by(slug=slug).one_or_none(),
            )
        ):
            log.debug("slug_create: triggered a collision")
            if tries > 10:
                raise RuntimeError(
                    "We exceeded our retry quota on a collision."
                )
            tries += 1
            slug = hash_create(necessary)

        return slug


units = [
    (1 << 20, "mb"),
    (1 << 10, "kb"),
    (1, "b"),
]


def size_postfix(count: int) -> str:
    for f, p in units:
        if count > f:
            break

    return f"{count/f:.0f}{p}"
