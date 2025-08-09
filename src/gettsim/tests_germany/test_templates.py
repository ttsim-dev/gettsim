from __future__ import annotations

import dags.tree as dt
from ttsim.interface_dag_elements.automatically_added_functions import TIME_UNIT_LABELS
from ttsim.interface_dag_elements.shared import (
    get_re_pattern_for_all_time_units_and_groupings,
)

from gettsim import MainTarget, main


def test_template_all_outputs_no_inputs(backend):
    res = main(
        main_targets=[
            MainTarget.labels.grouping_levels,
            MainTarget.templates.input_data_dtypes.tree,
        ],
        rounding=True,
        policy_date_str="2025-01-01",
        backend=backend,
    )

    paths_with_unspecified_dtypes = []
    flat_res = dt.flatten_to_tree_paths(res["templates"]["input_data_dtypes"]["tree"])
    for p, dtype in flat_res.items():
        if "|" in dtype:
            paths_with_unspecified_dtypes.append(p)
    if paths_with_unspecified_dtypes:
        formatted = "\n".join([str(p) for p in paths_with_unspecified_dtypes])
        msg = (
            "The following paths have a generic union type (indicated by '|' in dtype):"
            f"\n{formatted}"
            "\n\n"
            "To fix this, make sure you specified all input variables as PolicyInput "
            "with the correct type hints."
        )
        raise AssertionError(msg)

    pattern_all = get_re_pattern_for_all_time_units_and_groupings(
        time_units=list(TIME_UNIT_LABELS),
        grouping_levels=res["labels"]["grouping_levels"],
    )
    bn_to_variations = {}
    for qname in dt.qnames(res["templates"]["input_data_dtypes"]["tree"]):
        match = pattern_all.fullmatch(qname)
        # We must not find multiple time units for the same base name and group.
        base_name = match.group("base_name")
        if base_name not in bn_to_variations:
            bn_to_variations[base_name] = [qname]
        else:
            bn_to_variations[base_name].append(qname)
    dups = {bn: v for bn, v in bn_to_variations.items() if len(v) > 1}
    if dups:
        formatted = ""
        for base_name, variations in dups.items():
            formatted += f"\n{base_name}:\n    "
            formatted += "\n    ".join(variations)
            formatted += "\n"
        raise AssertionError(f"More than one variation for base names:\n{formatted}")
