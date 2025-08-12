"""
GETTSIM Profiling Script

This script profiles GETTSIM/TTSIM with synthetic data.
It supports both JAX and NumPy backends.

Usage:
    python gettsim_profile.py -N 32768 -b numpy (without profile)
    py-spy record -o profile.svg -- python gettsim_profile.py -N 32768 -b numpy (with profile)

"""


# %%
import pandas as pd
import time
import argparse
import hashlib
from gettsim import InputData, MainTarget, TTTargets, Labels, SpecializedEnvironment, RawResults

# Hack: Override GETTSIM main to make alls TTSIM parameters of main available in GETTSIM.
# Necessary because of GETTSIM issue #1075. 
# When resolved, this can be removed and gettsim.main can be used directly.
from gettsim import germany
import ttsim
from ttsim.main_args import OrigPolicyObjects

def main(**kwargs):
    """Wrapper around ttsim.main that automatically sets the German root path and supports tt_function."""
    # Set German tax system as default if no orig_policy_objects provided
    if kwargs.get('orig_policy_objects') is None:
        kwargs['orig_policy_objects'] = OrigPolicyObjects(root=germany.ROOT_PATH)
    
    return ttsim.main(**kwargs)

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
    "kindergeld": {"betrag_m": "betrag_m"},
    "bürgergeld": {"betrag_m_bg": "betrag_m_bg"},
    "wohngeld": {"betrag_m_wthh": "betrag_m_wthh"},
    "kinderzuschlag": {"betrag_m_bg": "betrag_m_bg"},
}


# %%
MAPPER = {
    "alter": "age",
    "arbeitsstunden_w": "working_hours",
    "behinderungsgrad": "disability_grade",
    "geburtsjahr": "birth_year",
    "hh_id": "hh_id",
    "p_id": "p_id",
    "wohnort_ost_hh": "east_germany",
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
            "bezieht_rente": False,
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
    "wohnen": {
        "bewohnt_eigentum_hh": False,
        "bruttokaltmiete_m_hh": 900.0,
        "heizkosten_m_hh": 150.0,
        "wohnfläche_hh": 80.0,
    },
    "kindergeld": {
        "in_ausbildung": "in_training",
        "p_id_empfänger": "id_recipient_child_allowance",
    },
    "vermögen": 0.0,
    "unterhalt": {
        "tatsächlich_erhaltener_betrag_m": 0.0,
    },
    "elterngeld": {
        "betrag_m": 0.0,
        "anrechenbarer_betrag_m": 0.0,
    },
    "bürgergeld": {
        "betrag_m_bg": 0.0,
        "p_id_einstandspartner": "bürgergeld__p_id_einstandspartner",
        "bezug_im_vorjahr": False,
    },
    "wohngeld": {
        # "betrag_m_wthh": 0.0,
        "mietstufe_hh": 3,
    },
    "kinderzuschlag": {
        # "betrag_m_bg": 0.0,
    },
}

def sync_jax_if_needed(backend):
    """Force JAX synchronization to ensure all operations are complete."""
    if backend == "jax":
        try:
            import jax
            # Force synchronization of all JAX operations
            jax.block_until_ready(jax.numpy.array([1.0]))
            print("  JAX operations synchronized")
        except ImportError:
            pass
        except Exception as e:
            print(f"  Warning: JAX sync failed: {e}")


def safe_hash_results(results):
    """Create a hash that doesn't trigger JAX array materialization.
    
    This function safely creates hashes of results by examining structure
    and types rather than materializing large arrays, preventing memory
    explosions with JAX backends.
    """
    if isinstance(results, dict):
        return {k: safe_hash_results(v) for k, v in results.items()}
    elif hasattr(results, 'shape') and hasattr(results, 'dtype'):
        # For arrays, hash shape and dtype instead of data
        return f"{type(results).__name__}(shape={results.shape}, dtype={results.dtype})"
    else:
        return str(type(results).__name__)


def run_profile(N, backend):
    """Run GETTSIM profiling with specified parameters."""
    print(f"Generating dataset with {N:,} households...")
    data = make_data(N)
    print(f"Dataset created successfully. Shape: {data.shape}")
    
    print(f"Running GETTSIM with backend: {backend}")
    
    # First stage - preprocessing and DAG creation
    print("\n=== STAGE 1: Data preprocessing and DAG creation ===")
    stage1_start = time.time()

    tmp = main(
        policy_date_str="2025-01-01",
        input_data=InputData.df_and_mapper(
            df=data,
            mapper=MAPPER,
        ),
        main_targets=[
            MainTarget.specialized_environment.tt_dag,
            MainTarget.processed_data,
            MainTarget.labels.root_nodes,
            MainTarget.input_data.flat,  # Need this for stage 3
            MainTarget.tt_function, # Use compiled tt_function in stage 2 with JAX backend
        ],
        tt_targets=TTTargets(
            tree=TT_TARGETS,
        ),
        include_fail_nodes=True,
        include_warn_nodes=False,
        backend=backend,
    )    

    # Force JAX synchronization before recording end time
    sync_jax_if_needed(backend)
    
    stage1_end = time.time()
    stage1_time = stage1_end - stage1_start
    
    # Generate hash for Stage 1 output (tmp) - avoid memory issues with large arrays
    stage1_hash = hashlib.md5(str(safe_hash_results(tmp)).encode('utf-8')).hexdigest()
    
    print(f"Stage 1 completed in: {stage1_time:.4f} seconds")
    print(f"Processed data keys: {len(tmp['processed_data'])}")
    print(f"DAG nodes: {len(tmp['specialized_environment']['tt_dag'])}")
    print(f"Stage 1 hash: {stage1_hash[:16]}...")

    # Second stage - computation only (no data preprocessing)
    print("\n=== STAGE 2: Computation only (no preprocessing) ===")
    print(f"Wall clock time: {time.strftime('%H:%M:%S')} - Starting Stage 2")
    stage2_start = time.time()

    raw_results__columns = main(
        policy_date_str="2025-01-01",
        main_target=MainTarget.raw_results.columns,
        tt_targets=TTTargets(
            tree=TT_TARGETS,
        ),
        processed_data=tmp["processed_data"],
        labels=Labels(root_nodes=tmp["labels"]["root_nodes"]),
        tt_function=tmp["tt_function"],  # Reuse pre-compiled JAX function
        include_fail_nodes=True,
        include_warn_nodes=False,
        backend=backend,
    )

    # Force JAX synchronization before recording end time
    sync_jax_if_needed(backend)

    stage2_end = time.time()
    print(f"Wall clock time: {time.strftime('%H:%M:%S')} - Completed Stage 2")
    stage2_time = stage2_end - stage2_start
    
    # Generate hash for Stage 2 output - avoid memory issues with large JAX arrays
    stage2_hash = hashlib.md5(str(safe_hash_results(raw_results__columns)).encode('utf-8')).hexdigest()
    
    print(f"Stage 2 completed in: {stage2_time:.4f} seconds")
    print(f"Raw results keys: {len(raw_results__columns)}")
    print(f"Stage 2 hash: {stage2_hash[:16]}...")

    # Third stage - convert raw results to DataFrame (no computation, just formatting)
    print("\n=== STAGE 3: Convert raw results to DataFrame ===")
    print(f"Wall clock time: {time.strftime('%H:%M:%S')} - Starting Stage 3")
    stage3_start = time.time()

    final_results = main(
        policy_date_str="2025-01-01",
        main_target=MainTarget.results.df_with_mapper,
        tt_targets=TTTargets(
            tree=TT_TARGETS,
        ),
        raw_results=RawResults.columns(raw_results__columns),
        input_data=InputData.flat(tmp["input_data"]["flat"]),  # Provide the flat input data from stage 1
        processed_data=tmp["processed_data"],
        labels=Labels(root_nodes=tmp["labels"]["root_nodes"]),
        specialized_environment=SpecializedEnvironment(
            tt_dag=tmp["specialized_environment"]["tt_dag"]
        ),
        include_fail_nodes=True,
        include_warn_nodes=False,
        backend=backend,
    )

    # Force JAX synchronization before recording end time
    sync_jax_if_needed(backend)

    stage3_end = time.time()
    print(f"Wall clock time: {time.strftime('%H:%M:%S')} - Completed Stage 3")
    stage3_time = stage3_end - stage3_start
    total_time = stage1_time + stage2_time + stage3_time
    
    # Generate hash for Stage 3 output - avoid memory issues
    stage3_hash = hashlib.md5(str(safe_hash_results(final_results)).encode('utf-8')).hexdigest()
    
    print(f"Stage 3 completed in: {stage3_time:.4f} seconds")
    print(f"Final DataFrame shape: {final_results.shape if hasattr(final_results, 'shape') else 'N/A'}")
    print(f"Final DataFrame type: {type(final_results)}")
    print(f"Stage 3 hash: {stage3_hash[:16]}...")
    print(f"Total execution time: {total_time:.4f} seconds")
    print(f"Stage 1 (preprocessing): {stage1_time:.4f}s ({stage1_time/total_time*100:.1f}%)")
    print(f"Stage 2 (computation): {stage2_time:.4f}s ({stage2_time/total_time*100:.1f}%)")
    print(f"Stage 3 (formatting): {stage3_time:.4f}s ({stage3_time/total_time*100:.1f}%)")
    print(f"Backend: {backend}")
    print(f"Households: {N:,}")
    print(f"People: {len(data):,}")
    print(f"Performance: {N / total_time:.0f} households/second")
    print("\n=== STAGE HASHES ===")
    print(f"Stage 1 hash: {stage1_hash[:16]}...")
    print(f"Stage 2 hash: {stage2_hash[:16]}...")
    print(f"Stage 3 hash: {stage3_hash[:16]}...")
    
    return final_results, total_time


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
