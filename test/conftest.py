import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--e2e",
        action="store_true",
        help="run browser tests only if the option is passed",
    )


def pytest_runtest_setup(item):
    if "e2e" in item.keywords and not item.config.getoption("--e2e"):
        pytest.skip(
            "browser tests are skipped because no --e2e option was given"
        )
    elif item.config.getoption("--e2e") and "e2e" not in item.keywords:
        pytest.skip("only browser tests are run when --e2e option is given")


def pytest_configure(config):
    config.addinivalue_line("markers", "e2e: mark browser tests")
