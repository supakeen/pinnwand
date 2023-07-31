from pinnwand import database


def test_regression_issue_14() -> None:
    # In #14 it was noticed that the tablename for models is calculated
    # incorrectly. This testcase ensures this bug isn't reintroduced
    assert database.Paste.__tablename__ == "paste"
