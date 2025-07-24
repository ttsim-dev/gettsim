from __future__ import annotations

import inspect
import re
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import dags
import dags.tree as dt
import networkx as nx
import optree

from ttsim.interface_dag_elements import MainTarget, MainTargetABC
from ttsim.interface_dag_elements.fail_if import (
    format_errors_and_warnings,
    format_list_linewise,
)
from ttsim.interface_dag_elements.interface_node_objects import (
    FailFunction,
    InputDependentInterfaceFunction,
    InterfaceFunction,
    InterfaceInput,
    WarnFunction,
)
from ttsim.interface_dag_elements.orig_policy_objects import load_module
from ttsim.main_args import MainArg

if TYPE_CHECKING:
    import datetime
    from collections.abc import Iterable

    from ttsim.interface_dag_elements.typing import (
        DashedISOString,
        FlatInterfaceObjects,
        NestedTargetDict,
        PolicyEnvironment,
        QNameData,
        UnorderedQNames,
    )
    from ttsim.main_args import (
        InputData,
        Labels,
        OrigPolicyObjects,
        RawResults,
        Results,
        SpecializedEnvironment,
        TTTargets,
    )


def main(
    *,
    main_target: str | tuple[str, ...] | NestedTargetDict | None = None,
    main_targets: Iterable[str | tuple[str, ...]] | None = None,
    policy_date_str: DashedISOString | None = None,
    input_data: InputData | None = None,
    tt_targets: TTTargets | None = None,
    rounding: bool = True,
    backend: Literal["numpy", "jax"] = "numpy",
    evaluation_date_str: DashedISOString | None = None,
    include_fail_nodes: bool = True,
    include_warn_nodes: bool = True,
    orig_policy_objects: OrigPolicyObjects | None = None,
    raw_results: RawResults | None = None,
    results: Results | None = None,
    specialized_environment: SpecializedEnvironment | None = None,
    policy_environment: PolicyEnvironment | None = None,
    processed_data: QNameData | None = None,
    policy_date: datetime.date | None = None,
    evaluation_date: datetime.date | None = None,
    labels: Labels | None = None,
) -> dict[str, Any]:
    """
    Main function that processes the inputs and returns the outputs.
    """
    input_qnames = _harmonize_inputs(locals())
    if main_target is not None:
        if main_targets is not None:
            raise ValueError(
                "Either `main_target` or `main_targets` must be provided, but not both."
            )
        main_target = _harmonize_main_target(main_target)
        main_targets = [main_target]
    elif main_targets is not None:
        main_targets = _harmonize_main_targets(main_targets)

    # If requesting an input template, we do not require any data.
    if not any(re.match("(input|processed)_data", s) for s in input_qnames):
        input_qnames["processed_data"] = {}
        input_qnames["processed_data_columns"] = None

    flat_interface_objects = load_flat_interface_functions_and_inputs()
    nodes = _resolve_dynamic_interface_objects_to_static_nodes(
        flat_interface_objects=flat_interface_objects,
        input_qnames=list(input_qnames),
    )

    _fail_if_requested_nodes_cannot_be_found(
        main_targets=main_targets,  # type: ignore[arg-type]
        nodes=nodes,
    )

    functions = {
        qn: n
        for qn, n in nodes.items()
        if isinstance(n, InterfaceFunction) and qn not in input_qnames
    }

    main_targets = include_fail_or_warn_nodes(
        functions=functions,
        explicit_main_targets=main_targets,  # type: ignore[arg-type]
        include_fail_nodes=include_fail_nodes,
        include_warn_nodes=include_warn_nodes,
    )

    dag = dags.create_dag(
        functions=functions,
        targets=main_targets,
    )

    _fail_if_root_nodes_of_interface_dag_are_missing(
        dag=dag,
        input_qnames=input_qnames,
        flat_interface_objects=flat_interface_objects,
    )

    def lexsort_key(x: str) -> int:
        return 0 if x.startswith("fail_if") else 1

    if main_target:
        f = dags.concatenate_functions(
            dag=dag,
            functions=functions,
            targets=main_target,
            enforce_signature=False,
            set_annotations=True,
            lexsort_key=lexsort_key,
        )
        return f(**input_qnames)
    f = dags.concatenate_functions(
        dag=dag,
        functions=functions,
        targets=main_targets,
        return_type="dict",
        enforce_signature=False,
        set_annotations=True,
        lexsort_key=lexsort_key,
    )
    return dt.unflatten_from_qnames(f(**input_qnames))


def _harmonize_inputs(inputs: dict[str, Any]) -> dict[str, Any]:
    expected_structure = MainTarget.to_dict()
    # Remove existing top-level elements that are None, these will be calculated.
    dict_inputs = {
        k: v.to_dict() if isinstance(v, MainArg) else v
        for k, v in inputs.items()
        if v is not None and k in expected_structure
    }
    qname_inputs = {}
    # Special treatment for orig_policy_objects.root because we do not list it in
    # `MainTarget` so as not to confuse users of GETTSIM, where it is set.
    if (
        dict_inputs.get("orig_policy_objects")
        and "root" in dict_inputs["orig_policy_objects"]
    ):
        qname_inputs["orig_policy_objects__root"] = dict_inputs[
            "orig_policy_objects"
        ].pop("root")

    _fail_if_input_structure_is_invalid(
        user_treedef=optree.tree_flatten(dict_inputs, none_is_leaf=True)[1],  # type: ignore[arg-type]
        expected_treedef=optree.tree_flatten(expected_structure, none_is_leaf=True)[1],
    )
    for acc in optree.tree_accessors(expected_structure, none_is_leaf=True):
        qname = dt.qname_from_tree_path(acc.path)
        with suppress(KeyError, TypeError):
            qname_inputs[qname] = acc(dict_inputs)
    return {k: v for k, v in qname_inputs.items() if v is not None}


def _fail_if_input_structure_is_invalid(
    user_treedef: optree.PyTreeDef,
    expected_treedef: optree.PyTreeDef,
) -> None:
    """
    Recursively check that all keys/paths in user_treedef are valid.

    Raise ValueError if
    - any invalid keys/paths are found.
    - if the user input is not a dict where a dict is expected.
    """

    def check(
        user_spec: optree.PyTreeDef,
        expected_spec: optree.PyTreeDef,
        path: tuple[str, ...],
    ) -> list[tuple[str, ...]]:
        invalid = []
        # If a dict is expected but user_spec is not a dict, mark as invalid
        if (
            expected_spec.kind == optree.PyTreeKind.DICT
            and user_spec.kind != optree.PyTreeKind.DICT
        ):
            invalid.append(path)
            return invalid
        if user_spec.kind == expected_spec.kind == optree.PyTreeKind.DICT:
            # This level of the expected pytree as a dict.
            expected_map = dict(
                zip(expected_spec.entries(), expected_spec.children(), strict=False)
            )
            # Loop over the actually provided pytree.
            for k, child in zip(
                user_spec.entries(), user_spec.children(), strict=False
            ):
                if k not in expected_map:
                    invalid.append((*path, k))
                else:
                    invalid.extend(
                        check(
                            user_spec=child,
                            expected_spec=expected_map[k],
                            path=(*path, k),
                        )
                    )
        return invalid

    invalid_paths = check(
        user_spec=user_treedef, expected_spec=expected_treedef, path=()
    )
    if invalid_paths:
        raise ValueError(
            "Invalid inputs for main(): the following keys/paths are not valid:\n"
            + "\n".join(str(p) for p in invalid_paths)
            + "\nPlease use only the documented structure for main()."
        )


def _harmonize_main_target(
    main_target: str | tuple[str, ...] | NestedTargetDict,
) -> str:
    msg = (
        "`main_target` must be a single qualified name, a tuple, or a dict with "
        "one element. If in doubt, use `MainTarget` and tab-complete. If you want to "
        "output multiple elements, use `main_targets` instead."
    )
    if isinstance(main_target, tuple):
        return dt.qname_from_tree_path(main_target)
    if isinstance(main_target, dict):
        if len(optree.tree_flatten(main_target, none_is_leaf=True)[0]) > 1:  # type: ignore[arg-type]
            raise ValueError(msg)
        return dt.qnames(main_target)[0]
    if isinstance(main_target, str):
        return main_target
    if isinstance(main_target, type(MainTargetABC)):
        raise TypeError(
            "`main_target` must be an atomic element of `MainTarget`, got: "
            f"`{main_target.__name__}`. Best use an IDE and tab-complete until you "
            "have reached the end of a path."
        )
    raise ValueError(msg)


def _harmonize_main_targets(
    main_targets: Iterable[str | tuple[str, ...]] | NestedTargetDict,
) -> list[str]:
    if isinstance(main_targets, dict):
        out = dt.qnames(main_targets)
    elif isinstance(main_targets[0], tuple):  # type: ignore[index]
        out = [dt.qname_from_tree_path(tp) for tp in main_targets]
    else:
        out = list(main_targets)

    for i in out:
        if isinstance(i, type(MainTargetABC)):
            raise TypeError(
                "Elements of `main_targets` must be atomic elements of `MainTarget`, "
                f"got: `{i.__name__}`. Best use an IDE and tab-complete until you "
                "have reached the end of a path."
            )

    return out


def _resolve_dynamic_interface_objects_to_static_nodes(
    flat_interface_objects: FlatInterfaceObjects,
    input_qnames: list[str],
) -> dict[str, InterfaceFunction | InterfaceInput]:
    """Resolve dynamic interface objects to static nodes.

    Make InputDependentInterfaceFunctions static by checking the input data and picking
    among the functions with the same leaf name the one that satisfies the include
    condition.

    Fail if multiple functions with the same leaf name satisfy the include condition.

    Parameters
    ----------
    flat_interface_objects
        The interface objects to resolve.
    input_qnames
        The input qnames to check the include conditions against.

    Returns
    -------
    A dictionary of static interface objects.

    """
    static_nodes: dict[str, InterfaceFunction | InterfaceInput] = {}
    path_to_idif: dict[tuple[str, ...], list[InputDependentInterfaceFunction]] = {}
    for orig_p, orig_object in flat_interface_objects.items():
        if isinstance(orig_object, InputDependentInterfaceFunction):
            new_path = (*orig_p[:-1], orig_object.leaf_name)
            if new_path not in path_to_idif:
                path_to_idif[new_path] = []
            path_to_idif[new_path].append(orig_object)
        else:
            static_nodes[dt.qname_from_tree_path(orig_p)] = orig_object

    for p, functions in path_to_idif.items():
        functions_satisfying_include_condition = [
            f for f in functions if f.include_condition_satisfied(input_qnames)
        ]
        _fail_if_multiple_functions_satisfy_include_condition(
            funcs=functions_satisfying_include_condition,
            path=p,
        )
        if functions_satisfying_include_condition:
            static_nodes[dt.qname_from_tree_path(p)] = (
                functions_satisfying_include_condition[0]
            )
    return static_nodes


def _fail_if_multiple_functions_satisfy_include_condition(
    funcs: list[InputDependentInterfaceFunction],
    path: tuple[str, ...],
) -> None:
    """Fail if multiple functions satisfy the include condition."""
    if len(funcs) > 1:
        func_names = "\n".join(f.original_function_name for f in funcs)
        msg = (
            f"Multiple InputDependentInterfaceFunctions with the path {path} "
            "satisfy their include conditions:\n\n"
            f"{func_names}\n\n"
            "Put differently, there are multiple ways to build a specific target. "
            "Make sure the input data you provide satisfies only one of the include "
            "conditions."
        )
        raise ValueError(msg)


def include_fail_or_warn_nodes(
    functions: dict[str, InterfaceFunction],
    explicit_main_targets: list[str] | None,
    include_fail_nodes: bool,
    include_warn_nodes: bool,
) -> list[str] | None:
    """Extend main targets with failures and warnings that can be computed.

    FailFunctions and WarnFunctions which are included explicitly among the main targets
    are treated like regular functions.

    """
    # If main_targets are None, all failures and warnings are included, anyhow.
    if explicit_main_targets is None:
        return explicit_main_targets

    fail_functions = {
        p: n
        for p, n in functions.items()
        if isinstance(n, FailFunction)
        and p not in explicit_main_targets
        and include_fail_nodes
    }
    warn_functions = {
        p: n
        for p, n in functions.items()
        if isinstance(n, WarnFunction)
        and p not in explicit_main_targets
        and include_warn_nodes
    }
    fail_or_warn_nodes = {**fail_functions, **warn_functions}
    initial_dag = dags.create_dag(
        functions={
            p: n
            for p, n in functions.items()
            if p
            not in {
                **fail_functions,
                **warn_functions,
            }
        },
        targets=explicit_main_targets,
    )
    all_main_targets = explicit_main_targets.copy()

    for p, n in fail_or_warn_nodes.items():
        args = inspect.signature(n).parameters
        if n.include_if_all_elements_present or n.include_if_any_element_present:
            # all(()) evaluates to True, so include first bit
            all_cond = n.include_if_all_elements_present and all(
                a in initial_dag for a in n.include_if_all_elements_present
            )
            any_cond = any(a in initial_dag for a in n.include_if_any_element_present)
            check = all_cond or any_cond
        else:
            check = all(a in initial_dag for a in args)
        if check:
            all_main_targets.append(p)
    return all_main_targets


def load_flat_interface_functions_and_inputs() -> FlatInterfaceObjects:
    """Load the collection of functions and inputs from the current directory."""
    orig_functions = _load_orig_functions()
    return _remove_tree_logic_from_functions_in_collection(
        orig_functions=orig_functions,
        top_level_namespace={
            (*path[:-1], func.leaf_name)[0] for path, func in orig_functions.items()
        },
    )


def _load_orig_functions() -> dict[tuple[str, ...], InterfaceFunction | InterfaceInput]:
    """
    Load the interface functions and inputs from the current directory.

    """
    root = Path(__file__).parent / "interface_dag_elements"
    paths = [
        p for p in root.rglob("*.py") if p.name not in ["__init__.py", "typing.py"]
    ]
    flat_functions: dict[
        tuple[str, ...],
        InterfaceFunction | InterfaceInput | FailFunction | WarnFunction,
    ] = {}
    for path in paths:
        module = load_module(path=path, root=root)
        for qname, obj in inspect.getmembers(module):
            # If nesting happens (e.g., df+mapper), we need to be consistent.
            tree_path = dt.tree_path_from_qname(qname)
            if isinstance(obj, InterfaceFunction | InterfaceInput):
                if obj.in_top_level_namespace:
                    flat_functions[tree_path] = obj
                else:
                    flat_functions[(str(module.__name__), *tree_path)] = obj

    return flat_functions


def _remove_tree_logic_from_functions_in_collection(
    orig_functions: dict[tuple[str, ...], InterfaceFunction | InterfaceInput],
    top_level_namespace: UnorderedQNames,
) -> FlatInterfaceObjects:
    """Map paths to column objects / param functions without tree logic."""
    return {
        path: obj.remove_tree_logic(
            tree_path=path,
            top_level_namespace=top_level_namespace,
        )
        for path, obj in orig_functions.items()
    }


def _fail_if_root_nodes_of_interface_dag_are_missing(
    dag: dags.DiGraph,
    input_qnames: dict[str, Any],
    flat_interface_objects: FlatInterfaceObjects,
) -> None:
    """Fail if root nodes are missing."""
    root_nodes = nx.subgraph_view(
        dag,
        filter_node=lambda n: dag.in_degree(n) == 0,
    ).nodes
    missing_nodes = [node for node in root_nodes if node not in input_qnames]

    missing_dynamic_nodes: dict[
        tuple[str, ...], list[InputDependentInterfaceFunction]
    ] = {}
    for p, f in flat_interface_objects.items():
        if isinstance(f, InputDependentInterfaceFunction):
            new_path = (*p[:-1], f.leaf_name)
            if (
                dt.qname_from_tree_path(new_path) in missing_nodes
                and new_path not in missing_dynamic_nodes
            ):
                missing_dynamic_nodes[new_path] = [f]
            elif new_path in missing_dynamic_nodes:
                missing_dynamic_nodes[new_path].append(f)

    if missing_nodes:
        msg = (
            "The following arguments to `main` are missing for computing the "
            "desired output:\n"
            + format_list_linewise(
                [str(dt.tree_path_from_qname(mn)) for mn in missing_nodes]
            )
        )
        if missing_dynamic_nodes:
            msg += _msg_for_missing_dynamic_nodes(missing_dynamic_nodes)
        raise ValueError(msg)


def _msg_for_missing_dynamic_nodes(
    paths_to_dynamic_nodes: dict[
        tuple[str, ...], list[InputDependentInterfaceFunction]
    ],
) -> str:
    """List the include conditions of dynamic nodes to provide them along the missing
    nodes error message."""
    msg_nodes = []
    for p, dynamic_nodes in paths_to_dynamic_nodes.items():
        include_conditions_for_this_path: list[str] = []
        for f in dynamic_nodes:
            conditions: list[str] = []
            if f.include_if_all_inputs_present:
                paths = [
                    dt.tree_path_from_qname(qn)
                    for qn in f.include_if_all_inputs_present
                ]
                conditions.append(f"All of: {paths}")
            if f.include_if_any_input_present:
                paths = [
                    dt.tree_path_from_qname(qn) for qn in f.include_if_any_input_present
                ]
                conditions.append(f"Any of: {paths}")
            if conditions:
                include_conditions_for_this_path.append(
                    " or\n        ".join(conditions)
                )
        if include_conditions_for_this_path:
            formatted_string = (
                f"{p}:\n   Provide one of the following:\n        "
                + "\n        ".join(include_conditions_for_this_path)
            )
            msg_nodes.append(formatted_string)

    return (
        "\n\nNote that the following missing nodes can also be provided via "
        "the following inputs:\n"
        "\n".join(msg_nodes)
    )


def _fail_if_requested_nodes_cannot_be_found(
    main_targets: list[str] | None,
    nodes: dict[str, InterfaceFunction | InterfaceInput],
) -> None:
    """Fail if some qname is not among nodes."""
    all_nodes = set(nodes.keys())
    interface_function_names = {
        p for p, n in nodes.items() if isinstance(n, InterfaceFunction)
    }
    fail_or_warn_functions = {
        p: n for p, n in nodes.items() if isinstance(n, (FailFunction, WarnFunction))
    }

    # main targets not in interface functions
    if main_targets is not None:
        missing_main_targets = set(main_targets) - set(interface_function_names)
    else:
        missing_main_targets = set()

    # Qnames from include condtions of fail_or_warn functions not in nodes
    for n in fail_or_warn_functions.values():
        ns: set[str] = {
            *n.include_if_all_elements_present,
            *n.include_if_any_element_present,
        }
        missing_main_targets_from_include_conditions = ns - all_nodes

    if missing_main_targets or missing_main_targets_from_include_conditions:
        if missing_main_targets:
            msg = format_errors_and_warnings(
                "The following output names for the interface DAG are not among the "
                "interface functions or inputs:\n"
            ) + format_list_linewise(sorted(missing_main_targets))
        else:
            msg = ""
        if missing_main_targets_from_include_conditions:
            msg += format_errors_and_warnings(
                "\n\nThe following elements specified in some include condition of "
                "`fail_or_warn_function`s are not among the interface functions or "
                "inputs:\n"
            ) + format_list_linewise(
                sorted(missing_main_targets_from_include_conditions)
            )
        raise ValueError(msg)
