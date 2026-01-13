import pytest

from lib.tests.fixtures import *  # noqa 403
from lib.tests.factories.fixtures import *  # noqa 403
from services.api.tests.fixtures import *  # noqa 403
from services.api.tests.factories.fixtures import *  # noqa 403


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    print("\n🚀")
