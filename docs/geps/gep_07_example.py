import pandas as pd

from gettsim import InputData, MainTarget, TTTargets, main

inputs_df = pd.DataFrame(
    {
        "age": [25, 45, 3, 65],
        "wage": [950, 950, 0, 950],
        "id": [0, 1, 2, 3],
        "hh_id": [0, 1, 1, 2],
        "mother_id": [-1, -1, 1, -1],
        "has_kids": [False, True, False, True],
    }
)

inputs_map = {
    "p_id": "id",
    "hh_id": "hh_id",
    "alter": "age",
    "familie": {
        "p_id_elternteil_1": "mother_id",
        "p_id_elternteil_2": -1,
    },
    "einkommensteuer": {
        "einkünfte": {
            "aus_nichtselbstständiger_arbeit": {"bruttolohn_m": "wage"},
            "ist_hauptberuflich_selbstständig": False,
            "aus_selbstständiger_arbeit": {"betrag_m": 0.0},
        }
    },
    "sozialversicherung": {
        "pflege": {
            "beitrag": {
                "hat_kinder": "has_kids",
            }
        },
        "kranken": {
            "beitrag": {"bemessungsgrundlage_rente_m": 0.0, "privat_versichert": False}
        },
    },
}

targets_tree = {
    "sozialversicherung": {
        "pflege": {
            "beitrag": {
                "betrag_versicherter_m": "ltci_contrib",
            }
        }
    }
}

outputs_df = main(
    main_target=MainTarget.results.df_with_mapper,
    policy_date_str="2025-01-01",
    input_data=InputData.df_and_mapper(
        df=inputs_df,
        mapper=inputs_map,
    ),
    tt_targets=TTTargets(tree=targets_tree),
)

print(outputs_df.round(2).to_markdown())

print(inputs_df.to_markdown())

pe = main(
    main_target=MainTarget.policy_environment,
    policy_date_str="2025-01-01",
)
