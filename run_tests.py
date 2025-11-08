#!/usr/bin/env python3
"""Скрипт для запуска тестов с настройками"""

import subprocess
import sys


def run_tests():
    """Запускает pytest с нужными параметрами"""
    result = subprocess.run([
        "pytest",
        "tests/",
        "-v",
        "-s",
        "--tb=short",
        "--cov=app",
        "--cov-report=term-missing"
    ])

    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
