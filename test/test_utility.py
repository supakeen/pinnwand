from pinnwand import utility


def test_expiries() -> None:
    assert len(utility.expiries) == 2
