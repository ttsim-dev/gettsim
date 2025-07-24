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

import sys as _sys
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
    tt,
    typing,
)

from _gettsim_tests import TEST_DIR

if TYPE_CHECKING:
    import datetime
    from collections.abc import Iterable

    import plotly.graph_objects as go
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
tt = tt


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


def plot_interface_dag(
    include_fail_and_warn_nodes: bool = True,
    show_node_description: bool = False,
    output_path: Path | None = None,
) -> go.Figure:
    return _ttsim.plot_interface_dag(
        include_fail_and_warn_nodes=include_fail_and_warn_nodes,
        show_node_description=show_node_description,
        output_path=output_path,
        remove_orig_policy_objects__root=True,
    )


def plot_tt_dag(
    policy_date_str: str,
    node_selector: NodeSelector | None = None,
    title: str = "",
    include_params: bool = True,
    include_other_objects: bool = False,
    show_node_description: bool = False,
    output_path: Path | None = None,
) -> go.Figure:
    return _ttsim.plot_tt_dag(
        policy_date_str=policy_date_str,
        root=Path(__file__).parent.parent / "_gettsim",
        node_selector=node_selector,
        title=title,
        include_params=include_params,
        include_other_objects=include_other_objects,
        show_node_description=show_node_description,
        output_path=output_path,
    )


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
    "plot_interface_dag",
    "plot_tt_dag",
    "test",
    "tt",
    "version",
    "version_tuple",
]
