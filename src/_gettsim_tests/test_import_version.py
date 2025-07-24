from __future__ import annotations

import sys

import gettsim


def test_import():
    assert hasattr(gettsim, "__version__")


def test_python_version():
    assert sys.version_info >= (3, 11)
