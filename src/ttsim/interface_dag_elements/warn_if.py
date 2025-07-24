from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

import dags.tree as dt

from ttsim.interface_dag_elements.fail_if import (
    format_errors_and_warnings,
    format_list_linewise,
)
from ttsim.interface_dag_elements.interface_node_objects import warn_function
from ttsim.tt_dag_elements.column_objects_param_function import PolicyInput

if TYPE_CHECKING:
    import datetime

    from ttsim.interface_dag_elements.typing import (
        PolicyEnvironment,
        QNameData,
        UnorderedQNames,
    )


@warn_function()
def functions_and_data_columns_overlap(
    policy_environment: PolicyEnvironment,
    labels__processed_data_columns: UnorderedQNames,
) -> None:
    """Warn if functions are overridden by data."""
    flat_policy_environment = dt.flatten_to_qnames(policy_environment)
    overridden_elements = sorted(
        {
            col
            for col in labels__processed_data_columns
            if col in flat_policy_environment
            and not isinstance(flat_policy_environment.get(col), PolicyInput)
        },
    )
    if n_cols := len(overridden_elements) > 0:
        if n_cols == 1:
            intro = format_errors_and_warnings("Your data provides the column:")
            explanation = format_errors_and_warnings(
                """
                This is already present among the hard-coded functions of the taxes and
                transfers system. If you want this data column to be used instead of
                calculating it within TTSIM you need not do anything. If you want this
                data column to be calculated by hard-coded functions, remove it from the
                *data* you pass to TTSIM. You need to pick one option for each column
                that appears in the list above.

                Turn off warnings by setting `include_warn_nodes=False` in `main`.
                If you want to be selective about warnings, include these among the
                `main_targets`.
                """,
            )
        else:
            intro = format_errors_and_warnings("Your data provides the columns:")
            explanation = format_errors_and_warnings(
                """
                These are already present among the hard-coded functions of the taxes
                and transfers system. If you want a data column to be used instead of
                calculating it within TTSIM you do not need to do anything. If you
                want data columns to be calculated by hard-coded functions, remove them
                from the *data* you pass to TTSIM. You need to pick one option for
                each column that appears in the list above.

                Turn off warnings by setting `include_warn_nodes=False` in `main`.
                If you want to be selective about warnings, include these among the
                `main_targets`.
                """,
            )
        msg = f"{intro}\n{format_list_linewise(overridden_elements)}\n{explanation}"
        warnings.warn(UserWarning(msg), stacklevel=2)


@warn_function(
    include_if_all_elements_present=[
        "specialized_environment__with_processed_params_and_scalars"
    ]
)
def evaluation_date_set_in_multiple_places(
    policy_environment: PolicyEnvironment,
    processed_data: QNameData,
    evaluation_date: datetime.date | None,
) -> None:
    """Warn if more than one of the following hold true:
    - `evaluation_date` is passed as an argument to `main`
    - `evaluation_year` is present in the policy environment and it is not a PolicyInput
    - `evaluation_year` is part of the data

    """
    conditions = {
        "`evaluation_date` passed as argument to `main`": evaluation_date is not None,
        "`evaluation_year` is set in the policy environment": (
            "evaluation_year" in policy_environment
            and not isinstance(policy_environment["evaluation_year"], PolicyInput)
        ),
        "`evaluation_year` is present in the data": "evaluation_year" in processed_data,
    }
    if sum(conditions.values()) > 1:
        nicely_formatted_conditions = "\n".join(
            [f"- {k}" for k, v in conditions.items() if v]
        )
        msg = f"""
You have specified the evaluation date in more than one way:

{nicely_formatted_conditions}

The last of these will be used.

Note that this warnings function does not check for `evaluation_month`
and `evaluation_day`, never set them anywhere without also setting
`evaluation_year`.
"""
        warnings.warn(UserWarning(msg), stacklevel=2)
