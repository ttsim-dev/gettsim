"""This module contains the main namespace of gettsim."""

from __future__ import annotations

try:
    # Import the version from _version.py which is dynamically created by
    # setuptools-scm upon installing the project with pip.
    # Do not put it under version control!
    from _gettsim._version import __version__, __version_tuple__, version, version_tuple
except ImportError:
    __version__ = "unknown"
    __version_tuple__ = ("unknown", "unknown", "unknown")
    version = "unknown"
    version_tuple = ("unknown", "unknown", "unknown")

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import pytest
import ttsim as _ttsim
from ttsim import (
    InputData,
    Labels,
    MainTarget,
    RawResults,
    Results,
    SpecializedEnvironment,
    TTTargets,
    __version__,
    __version_tuple__,
    copy_environment,
    merge_trees,
    upsert_tree,
)

from _gettsim_tests import TEST_DIR

if TYPE_CHECKING:
    import datetime
    from collections.abc import Iterable

    from ttsim import typing
    from ttsim.typing import (
        DashedISOString,
        FlatColumnObjectsParamFunctions,
        FlatOrigParamSpecs,
        NestedTargetDict,
        PolicyEnvironment,
        QNameData,
    )

    typing = typing

InputData = InputData
Labels = Labels
MainTarget = MainTarget
RawResults = RawResults
Results = Results
SpecializedEnvironment = SpecializedEnvironment
TTTargets = TTTargets
__version__ = __version__
__version_tuple__ = __version_tuple__
copy_environment = copy_environment
merge_trees = merge_trees
upsert_tree = upsert_tree


def test(backend: Literal["numpy", "jax"] = "numpy") -> None:
    pytest.main([str(TEST_DIR), "--backend", backend])


@dataclass(frozen=True)
class OrigPolicyObjects(_ttsim.main_args.MainArg):
    column_objects_and_param_functions: FlatColumnObjectsParamFunctions | None = None
    param_specs: FlatOrigParamSpecs | None = None


def main(
    *,
    main_target: str | tuple[str, ...] | NestedTargetDict | None = None,
    main_targets: Iterable[str | tuple[str, ...]] | None = None,
    policy_date_str: DashedISOString | None = None,
    input_data: InputData | None = None,
    tt_targets: TTTargets | None = None,
    rounding: bool = True,
    backend: Literal["numpy", "jax"] = "numpy",
    evaluation_date_str: DashedISOString | None = None,
    include_fail_nodes: bool = True,
    include_warn_nodes: bool = True,
    orig_policy_objects: OrigPolicyObjects | None = None,
    raw_results: RawResults | None = None,
    results: Results | None = None,
    specialized_environment: SpecializedEnvironment | None = None,
    policy_environment: PolicyEnvironment | None = None,
    processed_data: QNameData | None = None,
    policy_date: datetime.date | None = None,
    evaluation_date: datetime.date | None = None,
    labels: Labels | None = None,
) -> dict[str, Any]:
    if orig_policy_objects is None:
        orig_policy_objects = _ttsim.main_args.OrigPolicyObjects(
            root=Path(__file__).parent.parent / "_gettsim"
        )

    return _ttsim.main(**locals())


__all__ = [
    "InputData",
    "Labels",
    "MainTarget",
    "OrigPolicyObjects",
    "RawResults",
    "Results",
    "SpecializedEnvironment",
    "TTTargets",
    "__version__",
    "__version_tuple__",
    "copy_environment",
    "main",
    "merge_trees",
    "test",
    "upsert_tree",
    "version",
    "version_tuple",
]
