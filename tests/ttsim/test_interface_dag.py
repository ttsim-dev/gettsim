from __future__ import annotations

import inspect

import dags
import dags.tree as dt
import optree
import pytest

from ttsim import InputData, OrigPolicyObjects, TTTargets
from ttsim.interface_dag import (
    _fail_if_input_structure_is_invalid,
    _fail_if_requested_nodes_cannot_be_found,
    _fail_if_root_nodes_of_interface_dag_are_missing,
    _harmonize_inputs,
    _harmonize_main_target,
    _harmonize_main_targets,
    _resolve_dynamic_interface_objects_to_static_nodes,
    load_flat_interface_functions_and_inputs,
)
from ttsim.interface_dag_elements import MainTarget
from ttsim.interface_dag_elements.fail_if import format_list_linewise
from ttsim.interface_dag_elements.interface_node_objects import (
    fail_function,
    input_dependent_interface_function,
    interface_function,
)
from ttsim.plot_dag import dummy_callable
from ttsim.tt_dag_elements.column_objects_param_function import policy_function


@interface_function(leaf_name="interface_function_a")
def interface_function_a(a: int) -> int:
    return a


@interface_function(leaf_name="interface_function_b")
def interface_function_b(b: int) -> int:
    return b


@interface_function(leaf_name="interface_function_c")
def interface_function_c(interface_function_a: int, interface_function_b: int) -> int:
    return interface_function_a + interface_function_b


@fail_function(
    include_if_all_elements_present=["a"],
    include_if_any_element_present=["b"],
)
def some_fail_function() -> None:
    pass


@input_dependent_interface_function(
    leaf_name="some_idif",
    include_if_all_inputs_present=["input_1"],
)
def some_idif_require_input_1(input_1: int) -> int:
    return input_1


@input_dependent_interface_function(
    leaf_name="some_idif",
    include_if_all_inputs_present=["input_2", "n1__input_2"],
)
def some_idif_require_input_2_and_n1__input_2(input_2: int, n1__input_2: int) -> int:
    return input_2 + n1__input_2


@input_dependent_interface_function(
    leaf_name="some_idif_with_conflicting_conditions",
    include_if_all_inputs_present=["input_1"],
)
def some_idif_with_conflicting_conditions_require_input_1(input_1: int) -> int:
    return input_1


@input_dependent_interface_function(
    leaf_name="some_idif_with_conflicting_conditions",
    include_if_any_input_present=["input_1", "n1__input_2"],
)
def some_idif_with_conflicting_conditions_require_input_1_or_n1__input_2(
    input_1: int, n1__input_2: int
) -> int:
    return input_1 + n1__input_2


@input_dependent_interface_function(
    include_if_any_input_present=["input_1"],
    include_if_all_inputs_present=["input_2", "input_3"],
)
def a() -> int:
    return 1


@policy_function()
def e(c: int, d: float) -> float:
    return c + d


def test_load_flat_interface_functions_and_inputs() -> None:
    load_flat_interface_functions_and_inputs()


def test_interface_dag_is_complete() -> None:
    # This will keep only one of possibly many InputDependentInterfaceFunctions. Here,
    # we only care about some function with a leaf name, not the precise content.
    nodes = {
        dt.qname_from_tree_path((*p[:-1], f.leaf_name)): f
        for p, f in load_flat_interface_functions_and_inputs().items()
    }

    nodes_with_dummy_callables = {
        qn: dummy_callable(n) if not callable(n) else n for qn, n in nodes.items()
    }
    f = dags.concatenate_functions(
        functions=nodes_with_dummy_callables,
        targets=None,
        return_type="dict",
        enforce_signature=False,
        set_annotations=False,
    )
    args = inspect.signature(f).parameters
    if args:
        raise ValueError(
            "The full interface DAG should include all root nodes but requires inputs:"
            f"\n\n{format_list_linewise(args.keys())}"
        )


def test_main_target_class_is_complete() -> None:
    # This will keep only one of possibly many InputDependentInterfaceFunctions. Here,
    # we only care about some function with a leaf name, not the precise content.
    nodes = {
        (*p[:-1], f.leaf_name)
        for p, f in load_flat_interface_functions_and_inputs().items()
    }

    # We do include the root path in MainTarget because it will be pre-defined in
    # user-facing implementations.
    nodes -= {
        (
            "orig_policy_objects",
            "root",
        ),
    }

    main_target_elements = set(dt.tree_paths(MainTarget.to_dict()))

    assert nodes == main_target_elements


@pytest.mark.parametrize(
    ("main_targets", "nodes", "error_match"),
    [
        (
            ["a"],
            {
                dt.qname_from_tree_path(p): n
                for p, n in load_flat_interface_functions_and_inputs().items()
            },
            r'output\snames[\s\S]+interface\sfunctions\sor\sinputs:[\s\S]+"a"',
        ),
        (
            ["input_data"],
            {
                dt.qname_from_tree_path(p): n
                for p, n in load_flat_interface_functions_and_inputs().items()
            },
            r'output\snames[\s\S]+interface\sfunctions\sor\sinputs:[\s\S]+"input_data"',
        ),
        (
            [],
            {
                **{
                    dt.qname_from_tree_path(p): n
                    for p, n in load_flat_interface_functions_and_inputs().items()
                },
                "some_fail_function": some_fail_function,
            },
            r'include\scondition[\s\S]+functions or inputs:[\s\S]+"a",\s+"b"',
        ),
    ],
)
def test_fail_if_requested_nodes_cannot_be_found(
    main_targets, nodes, error_match
) -> None:
    with pytest.raises(ValueError, match=error_match):
        _fail_if_requested_nodes_cannot_be_found(
            main_targets=main_targets,
            nodes=nodes,
        )


def test_harmonize_inputs_main_args_input():
    x = {
        "input_data": InputData.df_and_mapper(
            df={"cannot use df because comparison fails"},
            mapper={"c": "a", "d": "b", "p_id": "p_id"},
        ),
        "tt_targets": TTTargets(tree={"e": "f"}),
        "policy_date_str": "2025-01-01",
        "backend": "numpy",
        "rounding": True,
        "orig_policy_objects": OrigPolicyObjects(
            column_objects_and_param_functions={("x.py", "e"): e},
            param_specs={},
        ),
    }
    harmonized = _harmonize_inputs(inputs=x)

    assert harmonized == {
        "input_data__df_and_mapper__df": {"cannot use df because comparison fails"},
        "input_data__df_and_mapper__mapper": {"c": "a", "d": "b", "p_id": "p_id"},
        "tt_targets__tree": {"e": "f"},
        "policy_date_str": "2025-01-01",
        "orig_policy_objects__column_objects_and_param_functions": {("x.py", "e"): e},
        "orig_policy_objects__param_specs": {},
        "backend": "numpy",
        "rounding": True,
    }


def test_harmonize_inputs_tree_input():
    x = {
        "input_data": {
            "df_and_mapper": {
                "df": {"cannot use df because comparison fails"},
                "mapper": {"c": "a", "d": "b", "p_id": "p_id"},
            }
        },
        "tt_targets": {"tree": {"e": "f"}},
        "policy_date_str": "2025-01-01",
        "backend": "numpy",
        "rounding": True,
        "orig_policy_objects": {
            "column_objects_and_param_functions": {("x.py", "e"): e},
            "param_specs": {},
        },
    }
    harmonized = _harmonize_inputs(inputs=x)

    assert harmonized == {
        "input_data__df_and_mapper__df": {"cannot use df because comparison fails"},
        "input_data__df_and_mapper__mapper": {"c": "a", "d": "b", "p_id": "p_id"},
        "tt_targets__tree": {"e": "f"},
        "policy_date_str": "2025-01-01",
        "orig_policy_objects__column_objects_and_param_functions": {("x.py", "e"): e},
        "orig_policy_objects__param_specs": {},
        "backend": "numpy",
        "rounding": True,
    }


@pytest.mark.parametrize(
    ("main_target", "expected"),
    [
        ("a__b", "a__b"),
        (("a", "b"), "a__b"),
        ({"a": {"b": None}}, "a__b"),
    ],
)
def test_harmonize_main_target(main_target, expected):
    harmonized = _harmonize_main_target(main_target=main_target)

    assert harmonized == expected


@pytest.mark.parametrize(
    "dict_inputs",
    [
        {"input_data": {"df_and_mapper": None}},
        {"input_data": {"not_around": None}},
        {"not_around": None},
    ],
)
def test_fail_if_input_structure_is_invalid(dict_inputs):
    with pytest.raises(ValueError, match="Invalid inputs for main()"):
        _fail_if_input_structure_is_invalid(
            user_treedef=optree.tree_flatten(dict_inputs)[1],
            expected_treedef=optree.tree_flatten(MainTarget.to_dict())[1],
        )


@pytest.mark.parametrize(
    "main_target",
    [
        ["a", "b"],
        {"a": {"b": None}, "c": None},
        {"a": {"b": None, "c": None}},
    ],
)
def test_harmonize_main_target_fails_for_multiple_elements(main_target):
    with pytest.raises(
        ValueError, match="must be a single qualified name, a tuple, or a dict"
    ):
        _harmonize_main_target(main_target=main_target)


@pytest.mark.parametrize(
    ("main_targets", "expected"),
    [
        (["a__b"], ["a__b"]),
        ([("a", "b")], ["a__b"]),
        ({"a": {"b": None}}, ["a__b"]),
    ],
)
def test_harmonize_main_targets(main_targets, expected):
    harmonized = _harmonize_main_targets(main_targets=main_targets)

    assert harmonized == expected


@pytest.mark.parametrize(
    (
        "flat_interface_objects",
        "input_qnames",
        "expected_function_name",
    ),
    [
        (
            {
                ("some_idif_require_input_1",): some_idif_require_input_1,
                (
                    "some_idif_require_input_2_and_n1__input_2",
                ): some_idif_require_input_2_and_n1__input_2,
            },
            ["input_2", "n1__input_2"],
            "some_idif_require_input_2_and_n1__input_2",
        ),
        (
            {
                ("some_idif_require_input_1",): some_idif_require_input_1,
                (
                    "some_idif_require_input_2_and_n1__input_2",
                ): some_idif_require_input_2_and_n1__input_2,
            },
            ["input_1"],
            "some_idif_require_input_1",
        ),
        (
            {
                ("some_idif_require_input_1",): some_idif_require_input_1,
                (
                    "some_idif_require_input_2_and_n1__input_2",
                ): some_idif_require_input_2_and_n1__input_2,
            },
            ["input_2", "n1__input_2", "input_3"],
            "some_idif_require_input_2_and_n1__input_2",
        ),
    ],
)
def test_resolve_dynamic_interface_objects_to_static_nodes_returns_correct_function(
    flat_interface_objects, input_qnames, expected_function_name
):
    static_func = next(
        iter(
            _resolve_dynamic_interface_objects_to_static_nodes(
                flat_interface_objects=flat_interface_objects,
                input_qnames=input_qnames,
            ).values()
        )
    )
    assert static_func.original_function_name == expected_function_name


def test_resolve_dynamic_interface_objects_to_static_nodes_with_conflicting_conditions():  # noqa: E501
    match = r"Multiple InputDependentInterfaceFunctions"
    with pytest.raises(ValueError, match=match):
        _resolve_dynamic_interface_objects_to_static_nodes(
            flat_interface_objects={
                (
                    "some_idif_with_conflicting_conditions_require_input_1",
                ): some_idif_with_conflicting_conditions_require_input_1,
                (
                    "some_idif_with_conflicting_conditions_require_input_1_or_n1__input_2",
                ): some_idif_with_conflicting_conditions_require_input_1_or_n1__input_2,
            },
            input_qnames=["input_1", "n1__input_2"],
        )


def test_fail_if_root_nodes_of_interface_dag_are_missing_without_missing_dynamic_nodes():  # noqa: E501
    flat_interface_objects = {
        ("interface_function_a",): interface_function_a,
        ("interface_function_b",): interface_function_b,
        ("interface_function_c",): interface_function_c,
    }
    dag = dags.create_dag(
        functions={
            dt.qname_from_tree_path(p): f for p, f in flat_interface_objects.items()
        },
        targets=None,
    )

    with pytest.raises(
        ValueError,
        match=(r"The following arguments to `main` are missing for computing the"),
    ):
        _fail_if_root_nodes_of_interface_dag_are_missing(
            dag=dag,
            input_qnames=["a"],
            flat_interface_objects=flat_interface_objects,
        )


def test_fail_if_root_nodes_of_interface_dag_are_missing_with_missing_dynamic_nodes():
    flat_interface_objects = {
        ("a",): a,
        ("interface_function_a",): interface_function_a,
    }
    dag = dags.create_dag(
        functions={
            "interface_function_a": interface_function_a,
        },
        targets=None,
    )

    with pytest.raises(
        ValueError,
        match=(
            r"All of: \[\('input_2',\), \('input_3',\)\] or\n        Any of: \[\('input_1',\)\]"  # noqa: E501
        ),
    ):
        _fail_if_root_nodes_of_interface_dag_are_missing(
            dag=dag,
            input_qnames=[],
            flat_interface_objects=flat_interface_objects,
        )


def test_fail_if_root_nodes_of_interface_dag_are_missing_dynamic_node_as_target():
    flat_interface_objects = {
        ("some_idif_require_input_1",): some_idif_require_input_1,
    }
    dag = dags.create_dag(
        functions={
            "some_idif_require_input_1": some_idif_require_input_1,
        },
        targets=["some_idif_require_input_1"],
    )

    with pytest.raises(
        ValueError,
        match=(
            r"(?!.*Note that the following missing nodes can also be provided via the following input).*"  # noqa: E501
        ),
    ):
        _fail_if_root_nodes_of_interface_dag_are_missing(
            dag=dag,
            input_qnames=[],
            flat_interface_objects=flat_interface_objects,
        )
