# %%
import pandas as pd
import time
import argparse
from gettsim import main, InputData, MainTarget, TTTargets
from make_data import make_data

# %%
TT_TARGETS = {
    "einkommensteuer": {"betrag_m_sn": "income_tax_m"},
    "sozialversicherung": {
        "pflege": {
            "beitrag": {
                "betrag_versicherter_m": "long_term_care_insurance_contribution_m"
            }
        },
        "kranken": {
            "beitrag": {"betrag_versicherter_m": "health_insurance_contribution_m"}
        },
        "rente": {
            "beitrag": {"betrag_versicherter_m": "pension_insurance_contribution_m"}
        },
        "arbeitslosen": {
            "beitrag": {
                "betrag_versicherter_m": "unemployment_insurance_contribution_m"
            }
        },
    },
    "wohngeld": {"betrag_m_wthh": "betrag_m_wthh"},
    "kinderzuschlag": {"betrag_m_bg": "betrag_m_bg"},
    "elterngeld": {"betrag_m": "betrag_m"},
    "arbeitslosengeld_2": {"betrag_m_bg": "betrag_m_bg"},
}


# %%
MAPPER = {
    "alter": "age",
    "arbeitsstunden_w": "working_hours",
    "behinderungsgrad": "disability_grade",
    "geburtsjahr": "birth_year",
    "hh_id": "hh_id",
    "p_id": "p_id",
    "wohnort_ost": "east_germany",
    "einnahmen": {
        "bruttolohn_m": 0.0,
        "kapitalerträge_y": 0.0,
        "renten": {
            "betriebliche_altersvorsorge_m": 0.0,
            "geförderte_private_vorsorge_m": 0.0,
            "gesetzliche_m": 0.0,
            "sonstige_private_vorsorge_m": 0.0,
        },
    },
    "einkommensteuer": {
        "einkünfte": {
            "ist_hauptberuflich_selbstständig": False,
            "ist_selbstständig": "self_employed",
            "aus_gewerbebetrieb": {"betrag_m": "income_from_self_employment"},
            "aus_vermietung_und_verpachtung": {"betrag_m": "income_from_rent"},
            "aus_nichtselbstständiger_arbeit": {
                "bruttolohn_m": "income_from_employment"
            },
            "aus_forst_und_landwirtschaft": {
                "betrag_m": "income_from_forest_and_agriculture"
            },
            "aus_selbstständiger_arbeit": {"betrag_m": "income_from_self_employment"},
            "aus_kapitalvermögen": {"kapitalerträge_m": "income_from_capital"},
            "sonstige": {
                "alle_weiteren_y": 0.0,
                "ohne_renten_m": "income_from_other_sources",
                "rente": {"ertragsanteil": 0.0},
                "renteneinkünfte_m": "pension_income",
            },
        },
        "abzüge": {
            "beitrag_private_rentenversicherung_m": "contribution_to_private_pension_insurance",  # noqa: E501
            "kinderbetreuungskosten_m": "childcare_expenses",
            "p_id_kinderbetreuungskostenträger": "person_that_pays_childcare_expenses",
        },
        "gemeinsam_veranlagt": "joint_taxation",
    },
    "sozialversicherung": {
        "arbeitslosen": {"betrag_m": 0.0},
        "rente": {
            "private_rente_betrag_m": "amount_private_pension_income",
            "altersrente": {
                "betrag_m": 0.0,
            },
        },
        "kranken": {
            "beitrag": {"privat_versichert": "contribution_private_health_insurance"}
        },
        "pflege": {"beitrag": {"hat_kinder": "has_children"}},
    },
    "familie": {
        "alleinerziehend": "single_parent",
        "kind": "is_child",
        "p_id_ehepartner": "spouse_id",
        "p_id_elternteil_1": "parent_id_1",
        "p_id_elternteil_2": "parent_id_2",
    },
    "wohngeld": {
        "betrag_m_wthh": 0.0,
    },
    "kinderzuschlag": {
        "betrag_m_bg": 0.0,
    },
    "elterngeld": {
        "betrag_m": 0.0,
    },
    "arbeitslosengeld_2": {
        "betrag_m_bg": 0.0,
    },
    "kindergeld": {
        "in_ausbildung": "in_training",
        "p_id_empfänger": "id_recipient_child_allowance",
    },
}

def run_profile(N, backend):
    """Run GETTSIM profiling with specified parameters."""
    print(f"Generating dataset with {N:,} households...")
    data = make_data(N)
    print(f"Dataset created successfully. Shape: {data.shape}")
    
    print(f"Running GETTSIM with backend: {backend}")
    start_time = time.time()

    tmp = main(
        policy_date_str="2025-01-01",
        input_data=InputData.df_and_mapper(
            df=data,
            mapper=MAPPER,
        ),
        main_targets=[MainTarget.results.df_with_mapper],
        tt_targets=TTTargets(
            tree=TT_TARGETS,
        ),
        backend=backend,
        include_fail_nodes=False,
        include_warn_nodes=False,
    )

    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"Execution time: {execution_time:.4f} seconds")
    print(f"Backend: {backend}")
    print(f"Households: {N:,}")
    print(f"People: {len(data):,}")
    print(f"Performance: {N / execution_time:.0f} households/second")
    
    return tmp, execution_time


def main_cli():
    """Main function for command line interface."""
    parser = argparse.ArgumentParser(description='Profile GETTSIM with synthetic data')
    parser.add_argument('-N', '--households', type=int, default=32768,
                        help='Number of households to generate (default: 32768)')
    parser.add_argument('-b', '--backend', choices=['numpy', 'jax'], default='numpy',
                        help='Backend to use: numpy or jax (default: numpy)')
    
    args = parser.parse_args()
    
    print("GETTSIM Profiling Tool")
    print("=" * 50)
    
    result, exec_time = run_profile(args.households, args.backend)
    
    print("\n" + "=" * 50)
    print("Profiling completed successfully!")
    
    return result, exec_time


if __name__ == "__main__":
    main_cli()

# %%
# For interactive use - you can also run this directly
# result, exec_time = run_profile(N=32768, backend="numpy")
