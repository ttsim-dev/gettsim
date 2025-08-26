from __future__ import annotations

from typing import TYPE_CHECKING

import ttsim

from gettsim import germany

GETTSIM_COLORMAP = {
    # Top-level, background variables - blue.
    ("top-level",): "lightskyblue",
    ("einnahmen",): "mediumblue",
    ("familie",): "skyblue",
    ("wohnen",): "mediumturquoise",
    ("hh_characteristics",): "skyblue",
    ("ids",): "deepskyblue",
    ("unterhalt",): "teal",
    # Taxes - red. Exception: Einkünfte are mix of Einnahmen/Tax rules - purple.
    ("einkommensteuer",): "crimson",
    ("einkommensteuer", "einkünfte"): "purple",
    ("lohnsteuer",): "red",
    ("solidaritätszuschlag",): "darkred",
    # Social insurance - differentiate between programs and between pension
    # contributions and pension benefits.
    ("sozialversicherung",): "gold",
    ("sozialversicherung", "arbeitslosen"): "palegoldenrod",
    ("sozialversicherung", "kranken"): "yellow",
    ("sozialversicherung", "pflege"): "khaki",
    ("sozialversicherung", "rente"): "goldenrod",
    ("sozialversicherung", "rente", "beitrag"): "darkgoldenrod",
    # Transfers - green
    ("kindergeld",): "olive",
    ("kinderbonus",): "darkolivegreen",
    ("kinderzuschlag",): "mediumseagreen",
    ("elterngeld",): "darkgreen",
    ("erziehungsgeld",): "darkgreen",
    ("unterhaltsvorschuss",): "seagreen",
    ("wohngeld",): "darkseagreen",
    ("grundsicherung",): "limegreen",
    ("bürgergeld",): "lime",
    ("arbeitslosengeld_2",): "lime",
    ("vorrangprüfungen",): "green",
}

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
    node_colormap: dict[tuple[str, ...], str]
    | None = ttsim.plot.dag.INTERFACE_COLORMAP,
    **kwargs: Any,  # noqa: ANN401
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
    node_colormap
        Dictionary mapping namespace tuples to colors.
            - Tuples can represent any level of the namespace hierarchy (e.g.,
              ("input_data",) would be the first level,
              ("input_data", "df_and_mapper") the second level.
            - The tuple ("top-level",) is used to catch all members of the top-level
              namespace.
            - Individual elements or sub-namespaces can be overridden as the longest
              match will be used.
            - Fallback color is black.
            - Use any color from https://plotly.com/python/css-colors/
        If None, cycle through colors at the uppermost level of the namespace hierarchy.
    kwargs
        Additional keyword arguments. Will be passed to
        plotly.graph_objects.Figure.layout.

    Returns
    -------
    The figure.
    """
    return ttsim.plot.dag.interface(
        include_fail_and_warn_nodes=include_fail_and_warn_nodes,
        show_node_description=show_node_description,
        output_path=output_path,
        remove_orig_policy_objects__root=True,
        node_colormap=node_colormap,
        **kwargs,
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
    node_colormap: dict[tuple[str, ...], str] | None = GETTSIM_COLORMAP,
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
        be root nodes (for descendants), end nodes (for ancestors), or middle nodes (for
        neighbors). If not provided, the entire DAG is plotted.
    selection_type
        The type of the DAG to plot. Can be one of:
            - "neighbors": Plot the neighbors of the primary nodes.
            - "descendants": Plot the descendants of the primary nodes.
            - "ancestors": Plot the ancestors of the primary nodes.
            - "all_paths": All paths between the primary nodes are displayed (including
              any other nodes lying on these paths). You must pass at least two primary
              nodes.
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
    node_colormap
        Dictionary mapping namespace tuples to colors.
            - Tuples can represent any level of the namespace hierarchy (e.g.,
              ("sozialversicherung",) would be the first level,
              ("sozialversicherung", "arbeitslosenversicherung") the second level.
            - The tuple ("top-level",) is used to catch all members of the top-level
              namespace.
            - Individual elements or sub-namespaces can be overridden as the longest
              match will be used.
            - Fallback color is black.
            - Use any color from https://plotly.com/python/css-colors/
        If None, cycle through colors at the uppermost level of the namespace hierarchy.
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
    return ttsim.plot.dag.tt(
        root=germany.ROOT_PATH,
        primary_nodes=primary_nodes,
        selection_type=selection_type,
        selection_depth=selection_depth,
        include_params=include_params,
        show_node_description=show_node_description,
        output_path=output_path,
        node_colormap=node_colormap,
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
    "GETTSIM_COLORMAP",
    "interface",
    "tt",
]
