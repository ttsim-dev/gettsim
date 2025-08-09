from __future__ import annotations

from gettsim import plot


def test_gettsim_policy_environment_dag_with_params():
    plot.dag.tt(
        policy_date_str="2025-01-01",
        include_params=True,
        show_node_description=True,
    )


def test_gettsim_policy_environment_dag_without_params():
    plot.dag.tt(
        policy_date_str="2025-01-01",
        include_params=False,
        show_node_description=True,
    )


def test_pass_plotly_kwargs_to_plot_tt_dag():
    plot.dag.tt(
        policy_date_str="2025-01-01",
        include_params=True,
        show_node_description=True,
        title="GETTSIM policy environment DAG with parameters",
        width=200,
        height=800,
        showlegend=True,
        hovermode="closest",
    )
