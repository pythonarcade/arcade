import pytest


def pytest_addoption(parser):
    parser.addoption("--twm", action="store_true", default=False, help="Disable window geometry tests when using a tiling window manager" )


@pytest.fixture(scope="function")
def twm(pytestconfig):
    if pytestconfig.getoption("twm"):
        return True
    return False
