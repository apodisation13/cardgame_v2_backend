import pytest

from lib.tests.factories.fixtures import *  # noqa 403
from lib.tests.fixtures import *  # noqa 403


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    print("\n🚀")


def pytest_report_teststatus(report, config) -> tuple:
    if report.when == "call":
        if report.passed:
            return "passed", "P", "✅ PASSED\n"
        elif report.failed:
            return "failed", "F", "❌ FAILED\n"
        elif report.skipped:
            return "skipped", "S", "⏭ SKIPPED\n"
