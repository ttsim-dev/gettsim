"""This module contains the main namespace of gettsim."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import pytest
import ttsim
from ttsim import (
    InputData,
    Labels,
    MainTarget,
    RawResults,
    Results,
    SpecializedEnvironment,
    TTTargets,
    merge_trees,
)

from _gettsim._version import __version__, __version_tuple__, version, version_tuple
from _gettsim_tests import TEST_DIR

if TYPE_CHECKING:
    import datetime
    from collections.abc import Iterable

    from ttsim.interface_dag_elements.typing import (
        DashedISOString,
        FlatColumnObjectsParamFunctions,
        FlatOrigParamSpecs,
        NestedTargetDict,
        PolicyEnvironment,
        QNameData,
    )


def test(backend: Literal["numpy", "jax"] = "numpy") -> None:
    pytest.main([str(TEST_DIR), "--backend", backend])


@dataclass(frozen=True)
class OrigPolicyObjects(ttsim.main_args.MainArg):
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
        orig_policy_objects = ttsim.main_args.OrigPolicyObjects(
            root=Path(__file__).parent.parent / "_gettsim"
        )

    return ttsim.main(**locals())


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
    "main",
    "merge_trees",
    "test",
    "version",
    "version_tuple",
]
