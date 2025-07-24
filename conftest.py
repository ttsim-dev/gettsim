from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from ttsim.interface_dag_elements.backend import dnp as ttsim_dnp
from ttsim.interface_dag_elements.backend import xnp as ttsim_xnp

if TYPE_CHECKING:
    from types import ModuleType
    from typing import Literal


# content of conftest.py
def pytest_addoption(parser):
    parser.addoption(
        "--backend",
        action="store",
        default="numpy",
        help="The backend to test against (e.g., --backend=numpy --backend=jax)",
    )


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
