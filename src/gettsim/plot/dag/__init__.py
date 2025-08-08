from __future__ import annotations

from typing import TYPE_CHECKING

from ttsim import plot as ttsim_plot

from gettsim import germany

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any, Literal

    import plotly.graph_objects as go
    from ttsim.main_args import InputData, Labels, OrigPolicyObjects
    from ttsim.typing import DashedISOString, PolicyEnvironment, QNameData


def interface(
    include_fail_and_warn_nodes: bool = True,
    show_node_description: bool = False,
    output_path: Path | None = None,
) -> go.Figure:
    return ttsim_plot.dag.interface(
        include_fail_and_warn_nodes=include_fail_and_warn_nodes,
        show_node_description=show_node_description,
        output_path=output_path,
        remove_orig_policy_objects__root=True,
    )


def tt(
    *,
    # Args specific to TTSIM plotting
    primary_nodes: set[str] | set[tuple[str, str]] | None = None,
    selection_type: Literal["neighbors", "descendants", "ancestors", "nodes"]
    | None = None,
    selection_depth: int | None = None,
    include_params: bool = True,
    show_node_description: bool = False,
    output_path: Path | None = None,
    # Elements of main
    policy_date_str: DashedISOString | None = None,
    orig_policy_objects: OrigPolicyObjects | None = None,
    input_data: InputData | None = None,
    processed_data: QNameData | None = None,
    labels: Labels | None = None,
    policy_environment: PolicyEnvironment | None = None,
    backend: Literal["numpy", "jax"] = "numpy",
    include_fail_nodes: bool = True,
    include_warn_nodes: bool = True,
    # Args specific to plotly
    **kwargs: Any,  # noqa: ANN401
) -> go.Figure:
    return ttsim_plot.dag.tt(
        root=germany.ROOT_PATH,
        primary_nodes=primary_nodes,
        selection_type=selection_type,
        selection_depth=selection_depth,
        include_params=include_params,
        show_node_description=show_node_description,
        output_path=output_path,
        policy_date_str=policy_date_str,
        orig_policy_objects=orig_policy_objects,
        input_data=input_data,
        processed_data=processed_data,
        labels=labels,
        policy_environment=policy_environment,
        backend=backend,
        include_fail_nodes=include_fail_nodes,
        include_warn_nodes=include_warn_nodes,
        **kwargs,
    )


__all__ = [
    "interface",
    "tt",
]
