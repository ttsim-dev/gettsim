from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ttsim import plot
from ttsim.plot.dag import NodeSelector

if TYPE_CHECKING:
    import plotly.graph_objects as go

NodeSelector = NodeSelector


def interface(
    include_fail_and_warn_nodes: bool = True,
    show_node_description: bool = False,
    output_path: Path | None = None,
) -> go.Figure:
    return plot.dag.interface(
        include_fail_and_warn_nodes=include_fail_and_warn_nodes,
        show_node_description=show_node_description,
        output_path=output_path,
        remove_orig_policy_objects__root=True,
    )


def tt(
    policy_date_str: str,
    node_selector: NodeSelector | None = None,
    title: str = "",
    include_params: bool = True,
    show_node_description: bool = False,
    output_path: Path | None = None,
) -> go.Figure:
    return plot.dag.tt(
        policy_date_str=policy_date_str,
        root=Path(__file__).parent.parent / "_gettsim",
        node_selector=node_selector,
        title=title,
        include_params=include_params,
        show_node_description=show_node_description,
        output_path=output_path,
    )


__all__ = [
    "NodeSelector",
    "interface",
    "tt",
]
