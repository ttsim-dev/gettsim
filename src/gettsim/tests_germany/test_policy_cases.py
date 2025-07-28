from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Literal

import dags.tree as dt
import numpy
import pytest
from ttsim.testing_utils import (
    PolicyTest,
    check_env_completeness,
    execute_test,
    load_policy_cases,
)

from gettsim import MainTarget, germany, main

if TYPE_CHECKING:
    import datetime

    from gettsim.typing import OrigPolicyObjects


POLICY_TEST_IDS_AND_CASES = load_policy_cases(
    policy_cases_root=germany.ROOT_PATH.parent / "tests_germany" / "policy_cases",
    policy_name="",
    xnp=numpy,
)


def get_orig_gettsim_objects() -> OrigPolicyObjects:
    return main(
        main_targets=[
            MainTarget.orig_policy_objects.column_objects_and_param_functions,
            MainTarget.orig_policy_objects.param_specs,
        ],
    )["orig_policy_objects"]


def dates_in_orig_gettsim_objects() -> list[datetime.date]:
    orig_objects = get_orig_gettsim_objects()
    start_dates = {
        v.start_date
        for v in orig_objects["column_objects_and_param_functions"].values()
    }
    end_dates = {
        v.end_date + timedelta(days=1)
        for v in orig_objects["column_objects_and_param_functions"].values()
    }
    return sorted(start_dates | end_dates)


@pytest.fixture
def orig_gettsim_objects() -> OrigPolicyObjects:
    return get_orig_gettsim_objects()


@pytest.mark.parametrize(
    "test",
    POLICY_TEST_IDS_AND_CASES.values(),
    ids=POLICY_TEST_IDS_AND_CASES.keys(),
)
def test_policy_cases(test: PolicyTest, backend: Literal["numpy", "jax"]):
    execute_test(test=test, root=germany.ROOT_PATH, backend=backend)


@pytest.mark.parametrize(
    "date",
    dates_in_orig_gettsim_objects(),
    ids=lambda x: x.isoformat(),
)
def test_gettsim_policy_environment_is_complete(orig_gettsim_objects, date):
    """Test that GETTSIM's policy environment contains all root nodes of its DAG."""
    if date.year < 2015:  # noqa: PLR2004
        pytest.skip(
            "Policy environment for dates before 2015 are not complete. See issue #962."
        )

    check_env_completeness(
        name="GETTSIM",
        policy_date=date,
        orig_policy_objects=orig_gettsim_objects,
    )


@pytest.mark.parametrize(
    "date",
    dates_in_orig_gettsim_objects(),
    ids=lambda x: x.isoformat(),
)
def test_top_level_elements_not_repeated_in_paths(
    date, backend: Literal["numpy", "jax"]
):
    try:
        gettsim_objects = main(
            main_targets=[
                "specialized_environment__with_partialled_params_and_scalars",
                "labels__top_level_namespace",
            ],
            backend=backend,
            policy_date=date,
            rounding=False,
        )
    except Exception:  # noqa: BLE001
        msg = (
            "Skipped because environment cannot be created for date "
            f"{date.isoformat()}."
        )
        pytest.skip(msg)

    dt.fail_if_top_level_elements_repeated_in_paths(
        all_tree_paths=dt.flatten_to_tree_paths(
            dt.unflatten_from_qnames(
                gettsim_objects["specialized_environment"][
                    "with_partialled_params_and_scalars"
                ]
            )
        ),
        top_level_namespace=gettsim_objects["labels"]["top_level_namespace"],
    )
