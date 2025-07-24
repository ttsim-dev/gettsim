"""Some tests for the policy_environment module."""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import optree
import pandas as pd
import pytest

from ttsim import main
from ttsim.interface_dag_elements.orig_policy_objects import (
    column_objects_and_param_functions,
)
from ttsim.interface_dag_elements.policy_environment import (
    _active_column_objects_and_param_functions,
    _active_param_objects,
    _get_param_value,
)
from ttsim.tt_dag_elements import ScalarParam, policy_function

if TYPE_CHECKING:
    from types import ModuleType

    from ttsim.interface_dag_elements.typing import (
        NestedColumnObjectsParamFunctions,
    )

METTSIM_ROOT = Path(__file__).parent.parent / "mettsim"


@pytest.fixture(scope="module")
def some_params_spec_with_updates_previous():
    return [
        {
            "a": 1,
            "b": 2,
        },
        {
            "updates_previous": True,
            "b": 4,
        },
    ]


@pytest.fixture(scope="module")
def some_int_param():
    return ScalarParam(
        value=1,
        leaf_name="some_int_param",
        start_date="2025-01-01",
        end_date="2025-12-31",
        name="some_int_param",
        description="Some int param",
        unit=None,
        reference_period=None,
        note=None,
        reference=None,
    )


def test_add_jahresanfang(xnp: ModuleType):
    spec = {
        "name": {"de": "Test", "en": "Check"},
        "description": {"de": "Nichts zu sehen", "en": "Nothing to do"},
        "type": "scalar",
        "add_jahresanfang": True,
        datetime.date(2020, 1, 1): {"value": 1},
        datetime.date(2020, 7, 1): {"value": 2},
    }
    _active_ttsim_tree_with_params = _active_param_objects(
        orig={("spam.yaml", "foo"): spec},
        policy_date=pd.to_datetime("2020-07-01").date(),
        xnp=xnp,
    )
    assert _active_ttsim_tree_with_params["foo"].value == 2
    assert _active_ttsim_tree_with_params["foo_jahresanfang"].value == 1


def test_input_is_recognized_as_potential_group_id(backend):
    assert "kin" in main(
        main_target="labels__grouping_levels",
        orig_policy_objects={"root": METTSIM_ROOT},
        policy_date=datetime.date(2020, 1, 1),
        backend=backend,
    )


def test_p_id_not_recognized_as_potential_group_id(backend):
    assert "p" not in main(
        main_target="labels__grouping_levels",
        orig_policy_objects={"root": METTSIM_ROOT},
        policy_date=datetime.date(2020, 1, 1),
        backend=backend,
    )


@pytest.mark.parametrize(
    ("date_string", "expected"),
    [
        ("2023-01-20", datetime.date(2023, 1, 20)),
    ],
)
def test_start_date_valid(date_string: str, expected: datetime.date):
    @policy_function(start_date=date_string)
    def test_func():
        pass

    assert test_func.start_date == expected


@pytest.mark.parametrize(
    "date_string",
    [
        "20230120",
        "20.1.2023",
        "20th January 2023",
    ],
)
def test_start_date_invalid(date_string: str):
    with pytest.raises(
        ValueError,
        match="neither matches the format YYYY-MM-DD nor is a datetime.date",
    ):

        @policy_function(start_date=date_string)
        def test_func():
            pass


def test_start_date_missing():
    @policy_function()
    def test_func():
        pass

    assert test_func.start_date == datetime.date(1900, 1, 1)


@pytest.mark.parametrize(
    ("date_string", "expected"),
    [
        ("2023-01-20", datetime.date(2023, 1, 20)),
    ],
)
def test_end_date_valid(date_string: str, expected: datetime.date):
    @policy_function(end_date=date_string)
    def test_func():
        pass

    assert test_func.end_date == expected


@pytest.mark.parametrize(
    "date_string",
    [
        "20230120",
        "20.1.2023",
        "20th January 2023",
    ],
)
def test_end_date_invalid(date_string: str):
    with pytest.raises(
        ValueError,
        match="neither matches the format YYYY-MM-DD nor is a datetime.date",
    ):

        @policy_function(end_date=date_string)
        def test_func():
            pass


def test_end_date_missing():
    @policy_function()
    def test_func():
        pass

    assert test_func.end_date == datetime.date(2099, 12, 31)


def test_active_period_is_empty():
    with pytest.raises(ValueError, match="must be before the end date"):

        @policy_function(start_date="2023-01-20", end_date="2023-01-19")
        def test_func():
            pass


@pytest.mark.parametrize(
    ("tree", "last_day", "function_name_last_day", "function_name_next_day"),
    [
        (
            {"housing_benefits": {"eligibility": {"requirement_fulfilled_fam": None}}},
            datetime.date(2019, 12, 31),
            "requirement_fulfilled_fam_not_considering_children",
            "requirement_fulfilled_fam_considering_children",
        ),
    ],
)
def test_active_tree_with_column_objects_and_param_functions(
    tree: NestedColumnObjectsParamFunctions,
    last_day: datetime.date,
    function_name_last_day: str,
    function_name_next_day: str,
):
    orig = column_objects_and_param_functions(root=METTSIM_ROOT)
    functions_last_day = _active_column_objects_and_param_functions(
        orig=orig,
        policy_date=last_day,
    )
    functions_next_day = _active_column_objects_and_param_functions(
        orig=orig,
        policy_date=last_day + datetime.timedelta(days=1),
    )

    accessor = optree.tree_accessors(tree, none_is_leaf=True)[0]

    assert accessor(functions_last_day).__name__ == function_name_last_day
    assert accessor(functions_next_day).__name__ == function_name_next_day


def test_get_params_contents_with_updated_previous(
    some_params_spec_with_updates_previous,
):
    params_contents = _get_param_value(some_params_spec_with_updates_previous)
    expected = {
        "a": 1,
        "b": 4,
    }
    assert params_contents == expected
