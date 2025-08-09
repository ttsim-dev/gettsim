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
    """Plot the interface DAG.

    Parameters
    ----------
    include_fail_and_warn_nodes
        Whether to include fail and warn nodes.
    show_node_description
        Whether to show the node description.
    output_path
        If provided, the figure is written to the path.

    Returns
    -------
    The figure.
    """
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
    """Plot the TT DAG.

    Parameters
    ----------
    primary_nodes
        The qnames or paths of the primary nodes. Primary nodes are used to determine
        which other nodes to include in the plot based on the selection_type. They may
        be root nodes (for descendants), end nodes (for ancestors), or middle nodes
        (for neighbors). If not provided, the entire DAG is plotted.
    selection_type
        The type of the DAG to plot. Can be one of:
            - "neighbors": Plot the neighbors of the primary nodes.
            - "descendants": Plot the descendants of the primary nodes.
            - "ancestors": Plot the ancestors of the primary nodes.
            - "nodes": Plot the primary nodes only.
        If not provided, the entire DAG is plotted.
    selection_depth
        The depth of the selection. Only used if selection_type is "neighbors",
        "descendants", or "ancestors".
    include_params
        Include params and param functions when plotting the DAG. Default is True.
    show_node_description
        Show a description of the node when hovering over it.
    output_path
        If provided, the figure is written to the path.
    policy_date_str
        The date for which to plot the DAG.
    orig_policy_objects
        The orig policy objects.
    input_data
        The input data.
    processed_data
        The processed data.
    labels
        The labels.
    policy_environment
        The policy environment.
    backend
        The backend to use when executing main.
    include_fail_nodes
        Whether to include fail nodes when executing main.
    include_warn_nodes
        Whether to include warn nodes when executing main.
    kwargs
        Additional keyword arguments. Will be passed to
        plotly.graph_objects.Figure.layout.

    Returns
    -------
    The figure.
    """
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
