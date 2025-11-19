import os
print(f"\n🔍 Loading conftest.py from: {os.path.abspath(__file__)}")


from lib.tests.fixtures import *


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    print(f"\n🚀 {item.nodeid}")


def pytest_report_teststatus(report, config):
    if report.when == 'call':
        if report.passed:
            return "passed", "✅", "✅✅✅ PASSED\n"
        elif report.failed:
            return "failed", "❌", "❌❌❌ FAILED\n"
        elif report.skipped:
            return "skipped", "⏭️", "⏭⏭⏭ SKIPPED\n"
