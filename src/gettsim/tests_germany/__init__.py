"""This module is necessary to configure mypy's behavior for the tests."""

from __future__ import annotations

from pathlib import Path

# Obtain the test directory of the package.
TEST_DIR = Path(__file__).parent.resolve()
