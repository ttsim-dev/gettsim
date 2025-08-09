from __future__ import annotations

import datetime
import functools
import inspect
from typing import TYPE_CHECKING, Literal

import dags.tree as dt
import pytest
from dags import get_free_arguments

from gettsim import MainTarget, main
from gettsim.tt import ColumnFunction

if TYPE_CHECKING:
    from gettsim.typing import SpecEnvWithPartialledParamsAndScalars


def get_orig_gettsim_column_functions() -> list[ColumnFunction]:
    orig = main(
        main_target=MainTarget.orig_policy_objects.column_objects_and_param_functions,
    )
    return [(tp, cf) for tp, cf in orig.items() if isinstance(cf, ColumnFunction)]


@functools.lru_cache(maxsize=100)
def cached_specialized_environment(
    policy_date: datetime.date,
    backend: Literal["numpy", "jax"],
) -> SpecEnvWithPartialledParamsAndScalars:
    return main(
        main_target=(
            "specialized_environment_for_plotting_and_templates",
            "with_partialled_params_and_scalars",
        ),
        policy_date=policy_date,
        backend=backend,
        include_fail_nodes=False,
        include_warn_nodes=False,
    )


@pytest.mark.skipif_numpy
@pytest.mark.parametrize(
    ("tree_path", "fun"),
    get_orig_gettsim_column_functions(),
    ids=[str(x[0]) for x in get_orig_gettsim_column_functions()],
)
def test_jittable(tree_path, fun, backend, xnp):
    policy_date = min(fun.end_date, datetime.date.today())  # noqa: DTZ011
    qname = dt.qname_from_tree_path((*tree_path[:-2], fun.leaf_name))
    env = {qname: cached_specialized_environment(policy_date, backend)[qname]}

    processed_data = {}
    for arg_name in get_free_arguments(env[qname]):
        arg = inspect.signature(env[qname]).parameters[arg_name]
        if "FloatColumn" in arg.annotation:
            processed_data[arg_name] = xnp.zeros(1, dtype=float)
        elif "IntColumn" in arg.annotation:
            processed_data[arg_name] = xnp.zeros(1, dtype=int)
        elif "BoolColumn" in arg.annotation:
            processed_data[arg_name] = xnp.zeros(1, dtype=bool)
        else:
            raise ValueError(f"Unknown column type: {arg.annotation}")

    func = env[qname].func if isinstance(env[qname], functools.partial) else env[qname]
    if not func.fail_msg_if_included:
        main(
            main_target=("raw_results", "columns"),
            policy_date=policy_date,
            specialized_environment={"with_partialled_params_and_scalars": env},
            processed_data=processed_data,
            tt_targets={"qname": [qname]},
            backend=backend,
            include_fail_nodes=False,
            include_warn_nodes=False,
        )
