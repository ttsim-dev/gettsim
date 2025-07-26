from __future__ import annotations

from gettsim import plot


def test_gettsim_policy_environment_dag_with_params():
    plot.dag.tt(
        policy_date_str="2025-01-01",
        include_params=True,
        title="GETTSIM Policy Environment DAG with parameters",
        show_node_description=True,
    )


def test_gettsim_policy_environment_dag_without_params():
    plot.dag.tt(
        policy_date_str="2025-01-01",
        include_params=False,
        title="GETTSIM Policy Environment DAG without parameters",
        show_node_description=True,
    )
