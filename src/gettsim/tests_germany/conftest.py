from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from ttsim.interface_dag_elements.backend import dnp as ttsim_dnp
from ttsim.interface_dag_elements.backend import xnp as ttsim_xnp

if TYPE_CHECKING:
    from types import ModuleType
    from typing import Literal


def pytest_addoption(parser):
    """Register the --backend option if it does not exist already.

    Note this happens when running from dev-gettsim workspace root.
    """
    try:
        parser.addoption(
            "--backend",
            action="store",
            default="numpy",
            help="The backend to test against (e.g., --backend=numpy --backend=jax)",
        )
    except ValueError as e:
        if "option names {'--backend'} already added" not in str(e):
            raise


@pytest.fixture
def backend(request) -> Literal["numpy", "jax"]:
    return request.config.getoption("--backend")


@pytest.fixture
def xnp(request) -> ModuleType:
    return ttsim_xnp(request.config.getoption("--backend"))


@pytest.fixture
def dnp(request) -> ModuleType:
    return ttsim_dnp(request.config.getoption("--backend"))


@pytest.fixture(autouse=True)
def skipif_jax(request, backend):
    """Automatically skip tests marked with skipif_jax when backend is jax."""
    if request.node.get_closest_marker("skipif_jax") and backend == "jax":
        pytest.skip("Cannot run this test with Jax")


@pytest.fixture(autouse=True)
def skipif_numpy(request, backend):
    """Automatically skip tests marked with skipif_numpy when backend is numpy."""
    if request.node.get_closest_marker("skipif_numpy") and backend == "numpy":
        pytest.skip("Cannot run this test with Numpy")
