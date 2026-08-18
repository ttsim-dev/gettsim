from __future__ import annotations

import datetime
import os
from datetime import timedelta
from typing import TYPE_CHECKING, Literal, cast

import dags.tree as dt
import numpy
import pytest
from dags.tree.validation import fail_if_top_level_elements_repeated_in_paths
from ttsim.interface_dag_elements.backend import xnp as get_xnp
from ttsim.testing_utils import (
    PolicyTest,
    check_env_completeness,
    check_policy_environment_unit_history,
    execute_test,
    get_policy_date_partition,
    load_policy_cases,
)

from gettsim import InputData, MainTarget, TTTargets, germany, main

if TYPE_CHECKING:
    from ttsim.typing import FlatColumnObjectsParamFunctions, FlatOrigParamSpecs

    OrigPolicyObjects = dict[str, FlatColumnObjectsParamFunctions | FlatOrigParamSpecs]

ON_CI_WITHOUT_COVERAGE = (
    os.environ.get("GITHUB_ACTIONS") == "true"
    and os.environ.get("COV_CORE_SOURCE") is None
)

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
    column_objects = cast(
        "FlatColumnObjectsParamFunctions",
        orig_objects["column_objects_and_param_functions"],
    )
    start_dates = {v.start_date for v in column_objects.values()}
    end_dates = {v.end_date + timedelta(days=1) for v in column_objects.values()}
    # Skip first date (1900-01-01), which is just used to initialize many functions.
    return sorted(start_dates | end_dates)[1:]


def unit_check_dates_in_orig_gettsim_objects() -> list[datetime.date]:
    """Every function, parameter, rounding, and currency regime (GEP 10)."""
    return get_policy_date_partition(
        orig_policy_objects=get_orig_gettsim_objects(),
        unit_system=germany.UNIT_SYSTEM,
    )


@pytest.fixture
def orig_gettsim_objects() -> OrigPolicyObjects:
    return get_orig_gettsim_objects()


@pytest.mark.parametrize(
    "test",
    POLICY_TEST_IDS_AND_CASES.values(),
    ids=POLICY_TEST_IDS_AND_CASES.keys(),
)
def test_policy_cases(test: PolicyTest, backend: Literal["numpy", "jax"]):
    execute_test(
        test=test,
        root=germany.ROOT_PATH,
        backend=backend,
        unit_system=germany.UNIT_SYSTEM,
    )


@pytest.mark.skipif(
    ON_CI_WITHOUT_COVERAGE,
    reason="Test unaffected by Python version / OS. Only run once on CI.",
)
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
        unit_system=germany.UNIT_SYSTEM,
    )


def test_gettsim_units_are_complete_and_consistent(orig_gettsim_objects):
    """Validate declarations and body coverage in every GEP 10 date regime."""
    report = check_policy_environment_unit_history(
        orig_policy_objects=orig_gettsim_objects,
        unit_system=germany.UNIT_SYSTEM,
    )
    assert report.policy_date_regimes == tuple(
        unit_check_dates_in_orig_gettsim_objects()
    )


def _create_fake_input_data_from_template(template_tree: dict, xnp, n: int = 3) -> dict:
    """Create fake input data from a template tree of dtype strings."""
    flat_template = dt.flatten_to_qnames(template_tree)

    dtype_map = {
        "IntColumn": xnp.int32,
        "FloatColumn": xnp.float32,
        "BoolColumn": bool,
    }

    fake_flat = {}
    for qname, dtype_str in flat_template.items():
        dtype = dtype_map.get(dtype_str, xnp.float32)
        if dtype is bool:
            fake_flat[qname] = xnp.zeros(n, dtype=bool)
        else:
            fake_flat[qname] = xnp.zeros(n, dtype=dtype)

    # Add p_id (always required)
    fake_flat["p_id"] = xnp.arange(n, dtype=xnp.int32)

    return dt.unflatten_from_qnames(fake_flat)


@pytest.mark.skipif(
    ON_CI_WITHOUT_COVERAGE,
    reason="Test unaffected by Python version / OS. Only run once on CI.",
)
@pytest.mark.parametrize(
    "date",
    dates_in_orig_gettsim_objects(),
    ids=lambda x: x.isoformat(),
)
def test_top_level_elements_not_repeated_in_paths(
    date, backend: Literal["numpy", "jax"]
):
    xnp = get_xnp(backend)

    # Step 1: Get template for input data (without providing input_data)
    template = main(
        main_target=MainTarget.templates.input_data_dtypes.tree,
        policy_date=date,
        rounding=False,
    )

    # Step 2: Get tt_targets (without providing input_data)
    tt_targets_qname = main(
        main_target=MainTarget.tt_targets.qname,
        policy_date=date,
        rounding=False,
    )

    # Step 3: Create fake input data from template
    fake_input = _create_fake_input_data_from_template(template_tree=template, xnp=xnp)

    # Step 4: Call main with fake input data
    gettsim_objects = main(
        main_targets=[
            "specialized_environment__with_partialled_params_and_scalars",
            "labels__top_level_namespace",
        ],
        backend=backend,
        policy_date=date,
        input_data=InputData.tree(fake_input),
        tt_targets=TTTargets.qname(tt_targets_qname),
        rounding=False,
    )

    fail_if_top_level_elements_repeated_in_paths(
        all_tree_paths=set(
            dt.flatten_to_tree_paths(
                dt.unflatten_from_qnames(
                    gettsim_objects["specialized_environment"][
                        "with_partialled_params_and_scalars"
                    ]
                )
            )
        ),
        top_level_namespace=gettsim_objects["labels"]["top_level_namespace"],
    )
