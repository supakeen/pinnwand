from pinnwand import utility, database


def test_expiries() -> None:
    assert len(utility.expiries) == 2


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
