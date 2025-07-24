from __future__ import annotations

import inspect
from functools import lru_cache
from typing import TYPE_CHECKING, Literal

import dags
import dags.tree as dt
import optree
import pandas as pd
import yaml

from ttsim import main, merge_trees
from ttsim.interface_dag_elements.data_converters import (
    nested_data_to_df_with_nested_columns,
)
from ttsim.interface_dag_elements.fail_if import format_list_linewise
from ttsim.interface_dag_elements.shared import to_datetime
from ttsim.plot_dag import dummy_callable
from ttsim.tt_dag_elements.column_objects_param_function import PolicyInput

# Set display options to show all columns without truncation
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

if TYPE_CHECKING:
    import datetime
    from pathlib import Path
    from types import ModuleType

    from ttsim.interface_dag_elements.typing import (
        FlatColumnObjectsParamFunctions,
        FlatOrigParamSpecs,
        NestedData,
        NestedInputStructureDict,
        PolicyEnvironment,
    )


@lru_cache(maxsize=100)
def cached_policy_environment(
    policy_date: datetime.date,
    root: Path,
    backend: Literal["numpy", "jax"],
) -> PolicyEnvironment:
    return main(
        main_target="policy_environment",
        policy_date=policy_date,
        orig_policy_objects={"root": root},
        backend=backend,
        include_fail_nodes=True,
        include_warn_nodes=False,
    )


class PolicyTest:
    """A class for a single policy test."""

    __slots__ = (
        "expected_output_tree",
        "info",
        "input_tree",
        "path",
        "policy_date",
        "test_dir",
        "xnp",
    )

    def __init__(
        self,
        info: NestedData,
        input_tree: NestedData,
        expected_output_tree: NestedData,
        path: Path,
        policy_date: datetime.date,
        test_dir: Path,
        xnp: ModuleType,
    ) -> None:
        self.info = info
        self.input_tree = optree.tree_map(xnp.array, input_tree)
        self.expected_output_tree = expected_output_tree
        self.path = path
        self.policy_date = policy_date
        self.test_dir = test_dir
        self.xnp = xnp

    @property
    def target_structure(self) -> NestedInputStructureDict:
        flat_target_structure = dict.fromkeys(
            dt.flatten_to_tree_paths(self.expected_output_tree),
        )
        return dt.unflatten_from_tree_paths(flat_target_structure)

    @property
    def name(self) -> str:
        return self.path.relative_to(self.test_dir / "test_data").as_posix()


def execute_test(
    test: PolicyTest,
    root: Path,
    backend: Literal["numpy", "jax"],
) -> None:
    environment = cached_policy_environment(
        policy_date=test.policy_date, root=root, backend=backend
    )
    if test.target_structure:
        result_df = main(
            main_target="results__df_with_nested_columns",
            input_data={"tree": test.input_tree},
            policy_environment=environment,
            policy_date=test.policy_date,
            tt_targets={"tree": test.target_structure},
            rounding=True,
            backend=backend,
            include_fail_nodes=False,
            include_warn_nodes=False,
        )

        if test.expected_output_tree:
            expected_df = nested_data_to_df_with_nested_columns(
                nested_data_to_convert=test.expected_output_tree,
                data_with_p_id=test.input_tree,
            )
            try:
                pd.testing.assert_frame_equal(
                    result_df.sort_index(axis="columns"),
                    expected_df.sort_index(axis="columns"),
                    atol=test.info["precision_atol"],
                    check_dtype=False,
                )
            except AssertionError as e:
                assert set(result_df.columns) == set(expected_df.columns)  # noqa: S101
                cols_with_differences = []
                for col in expected_df.columns:
                    try:
                        pd.testing.assert_series_equal(
                            result_df[col],
                            expected_df[col],
                            atol=test.info["precision_atol"],
                            check_dtype=False,
                        )
                    except AssertionError:
                        cols_with_differences.append(col)
                raise AssertionError(
                    f"""actual != expected in columns: {cols_with_differences}.

actual[cols_with_differences]:

{result_df[cols_with_differences]}

expected[cols_with_differences]:

{expected_df[cols_with_differences]}
""",
                ) from e


def load_policy_test_data(
    test_dir: Path,
    policy_name: str,
    xnp: ModuleType,
) -> dict[str, PolicyTest]:
    """Load all tests found by recursively searching

        test_dir / "test_data" / policy_name

    for yaml files.

    If policy_name is empty, all tests found in test_dir / "test_data" are loaded.
    """
    out = {}
    for path_to_yaml in (test_dir / "test_data" / policy_name).glob("**/*.yaml"):
        if _is_skipped(path_to_yaml):
            continue

        with path_to_yaml.open("r", encoding="utf-8") as file:
            raw_test_data: NestedData = yaml.safe_load(file)

            this_test = _get_policy_test_from_raw_test_data(
                test_dir=test_dir,
                raw_test_data=raw_test_data,
                path_to_yaml=path_to_yaml,
                xnp=xnp,
            )
            out[this_test.name] = this_test

    return out


def _is_skipped(test_file: Path) -> bool:
    return "skip" in test_file.stem or "skip" in test_file.parent.name


def _get_policy_test_from_raw_test_data(
    test_dir: Path,
    path_to_yaml: Path,
    raw_test_data: NestedData,
    xnp: ModuleType,
) -> PolicyTest:
    """Get a list of PolicyTest objects from raw test data.

    Args:
        raw_test_data: The raw test data.
        path_to_yaml: The path to the YAML file.

    Returns
    -------
        A list of PolicyTest objects.
    """
    test_info: NestedData = raw_test_data.get("info", {})
    input_tree: NestedData = dt.unflatten_from_tree_paths(
        {
            k: xnp.array(v)
            for k, v in dt.flatten_to_tree_paths(
                merge_trees(
                    left=raw_test_data["inputs"].get("provided", {}),
                    right=raw_test_data["inputs"].get("assumed", {}),
                ),
            ).items()
        },
    )

    expected_output_tree: NestedData = dt.unflatten_from_tree_paths(
        {
            k: xnp.array(v)
            for k, v in dt.flatten_to_tree_paths(
                raw_test_data.get("outputs", {}),
            ).items()
        },
    )

    policy_date: datetime.date = to_datetime(path_to_yaml.parent.name)

    return PolicyTest(
        info=test_info,
        input_tree=input_tree,
        expected_output_tree=expected_output_tree,
        path=path_to_yaml,
        policy_date=policy_date,
        test_dir=test_dir,
        xnp=xnp,
    )


def check_env_completeness(
    name: str,
    policy_date: datetime.date,
    orig_policy_objects: dict[
        str, FlatColumnObjectsParamFunctions | FlatOrigParamSpecs
    ],
) -> None:
    environment = main(
        main_target="policy_environment",
        policy_date=policy_date,
        backend="numpy",
        orig_policy_objects=orig_policy_objects,
    )
    qname_environment = dt.flatten_to_qnames(environment)
    qnames_policy_inputs = [
        k for k, v in qname_environment.items() if isinstance(v, PolicyInput)
    ]
    qname_env_with_derived_functions = main(
        main_target="specialized_environment__without_tree_logic_and_with_derived_functions",
        policy_environment=environment,
        labels={"processed_data_columns": qnames_policy_inputs},
        tt_targets={"qname": list(qname_environment)},
        backend="numpy",
    )
    all_nodes = {
        qn: dummy_callable(n) if not callable(n) else n
        for qn, n in qname_env_with_derived_functions.items()
    }
    f = dags.concatenate_functions(
        functions=all_nodes,
        targets=list(qname_env_with_derived_functions.keys()),
        return_type="dict",
        enforce_signature=False,
        set_annotations=False,
    )
    args = set(inspect.signature(f).parameters) - {
        "backend",
        "xnp",
        "dnp",
        "num_segments",
        "evaluation_year",
        "evaluation_month",
        "evaluation_day",
    }
    if args:
        raise ValueError(
            f"{name}'s full DAG should include all root nodes but the following inputs "
            "are missing in the specialized policy environment:"
            f"\n\n{format_list_linewise(args)}\n\n"
            "Please add corresponding elements. Typically, these will be "
            "`@policy_input()`s or parameters in the yaml files."
        )
