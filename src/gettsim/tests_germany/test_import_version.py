from __future__ import annotations

import gettsim


def test_import():
    assert hasattr(gettsim, "__version__")


def test_germany_root():
    if not gettsim.germany.ROOT_PATH.is_dir():
        raise NotADirectoryError
