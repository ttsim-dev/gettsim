from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import pytest
from ttsim.interface_dag_elements.backend import dnp as ttsim_dnp
from ttsim.interface_dag_elements.backend import xnp as ttsim_xnp
from ttsim.tt.column_objects_param_function import PolicyFunction

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


_original_vectorize = PolicyFunction.vectorize


def _vectorize_with_loop(self, backend, xnp):
    """Force 'loop' strategy so coverage.py sees the original function body.

    See https://github.com/ttsim-dev/ttsim/issues/91
    """
    if self.vectorization_strategy == "vectorize":
        self = replace(self, vectorization_strategy="loop")
    return _original_vectorize(self, backend, xnp)


@pytest.fixture(autouse=True, scope="session")
def _force_loop_vectorization_for_coverage(request):
    """Switch 'vectorize' to 'loop' strategy when running with coverage.

    Only active when pytest-cov is running (``--cov`` is passed).
    """
    try:
        cov_source = request.config.getoption("--cov")
    except ValueError:
        cov_source = None
    if not cov_source:
        yield
        return

    PolicyFunction.vectorize = _vectorize_with_loop  # type: ignore[assignment]
    yield
    PolicyFunction.vectorize = _original_vectorize
