import pytest

from lib.tests.factories.fixtures import *  # noqa 403
from lib.tests.fixtures import *  # noqa 403
from services.cron.tests.fixtures import *  # noqa 403


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    print("\n🚀")
