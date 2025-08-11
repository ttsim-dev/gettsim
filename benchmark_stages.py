"""Performance comparison script for numpy vs jax backends."""
import pandas as pd
from gettsim import InputData, MainTarget, TTTargets, main, Labels, SpecializedEnvironment, RawResults
import time
import hashlib
import json
import os
import psutil
import gc
import threading
from datetime import datetime
from make_data import make_data

# JAX-specific imports for cache management
try:
    import jax
    JAX_AVAILABLE = True
except ImportError:
    JAX_AVAILABLE = False

# Use the same mapper as in the main script
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

def sync_jax_if_needed(backend):
    """Force JAX synchronization to ensure all operations are complete."""
    if backend == "jax":
        try:
            import jax
            # Force synchronization of all JAX operations
            jax.block_until_ready(jax.numpy.array([1.0]))
            print("    JAX operations synchronized")
        except ImportError:
            pass  # JAX not available, skip synchronization

def clear_jax_cache():
    """Clear JAX compilation cache to ensure clean state."""
    if JAX_AVAILABLE:
        try:
            # Import jax locally to avoid issues
            import jax as jax_local
            # Clear all JAX caches
            jax_local.clear_caches()
            print("  JAX compilation cache cleared")
        except Exception as e:
            print(f"  Warning: Could not clear JAX cache: {e}")

def force_garbage_collection():
    """Force aggressive garbage collection between runs."""
    gc.collect()
    gc.collect()  # Run twice for good measure
    gc.collect()
    print("  Garbage collection completed")

def reset_session_state(backend):
    """Reset session state between different backend runs."""
    print(f"  Resetting session state for {backend} backend...")
    
    # Force garbage collection
    force_garbage_collection()
    
    # Clear JAX-specific state if switching to/from JAX
    if backend == "jax" or JAX_AVAILABLE:
        clear_jax_cache()
    
    # Add a small delay to let system settle
    time.sleep(0.5)

def get_memory_usage_mb():
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

class MemoryTracker:
    """Track peak memory usage during execution with continuous monitoring."""
    def __init__(self):
        self.peak_memory = 0
        self.process = psutil.Process(os.getpid())
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start continuous memory monitoring in background thread."""
        self.monitoring = True
        self.peak_memory = self.get_current_memory()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop continuous memory monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.monitoring:
            current = self.get_current_memory()
            if current > self.peak_memory:
                self.peak_memory = current
            time.sleep(0.01)  # Check every 10ms
    
    def get_current_memory(self):
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024
    
    def update(self):
        """Update peak memory if current usage is higher."""
        current = self.get_current_memory()
        if current > self.peak_memory:
            self.peak_memory = current
        return current
    
    def get_peak(self):
        """Get peak memory usage in MB."""
        return self.peak_memory


def run_benchmark(
        N_households, backend,
        save_memory_profile=False,
        reset_session=False,
        sync_jax=False,
    ):
    """Run a single benchmark with 3-stage timing as in gettsim_profile_stages.py."""
    print(f"Running benchmark: {N_households:,} households, {backend} backend")
    
    # Reset session state to ensure clean environment
    if reset_session:
        reset_session_state(backend)
    
    # Generate data
    print("  Generating data...")
    data = make_data(N_households)
    
    # Memory tracking setup
    tracker = MemoryTracker() if save_memory_profile else None
    
    # Initial memory reading
    initial_memory = get_memory_usage_mb()
    if tracker:
        tracker.start_monitoring()
    
    try:
        # STAGE 1: Data preprocessing and DAG creation
        print("  Stage 1: Data preprocessing and DAG creation...")
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
            ],
            tt_targets=TTTargets(
                tree=TT_TARGETS,
            ),
            include_fail_nodes=False,
            include_warn_nodes=False,
            backend=backend,
        )    

        # Force JAX synchronization before recording end time
        if sync_jax:
            sync_jax_if_needed(backend)

        stage1_end = time.time()
        stage1_time = stage1_end - stage1_start

        # Generate hash for Stage 1 output (tmp)
        stage1_hash = hashlib.md5(str(tmp).encode('utf-8')).hexdigest()

        # STAGE 2: Computation only (no data preprocessing)
        print("  Stage 2: Computation only...")
        
        stage2_start = time.time()

        raw_results__columns = main(
            policy_date_str="2025-01-01",
            main_target=MainTarget.raw_results.columns,
            tt_targets=TTTargets(
                tree=TT_TARGETS,
            ),
            processed_data=tmp["processed_data"],
            labels=Labels(root_nodes=tmp["labels"]["root_nodes"]),
            specialized_environment=SpecializedEnvironment(
                tt_dag=tmp["specialized_environment"]["tt_dag"]
            ),
            include_fail_nodes=False,
            include_warn_nodes=False,
            backend=backend,
        )

        # Force JAX synchronization before recording end time
        if sync_jax:
            sync_jax_if_needed(backend)

        stage2_end = time.time()
        stage2_time = stage2_end - stage2_start

        # Generate hash for Stage 2 output (raw_results__columns)
        stage2_hash = hashlib.md5(str(raw_results__columns).encode('utf-8')).hexdigest()

        # STAGE 3: Convert raw results to DataFrame (no computation, just formatting)
        print("  Stage 3: Convert raw results to DataFrame...")
        stage3_start = time.time()

        result = main(
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
            include_fail_nodes=False,
            include_warn_nodes=False,
            backend=backend,
        )

        # Force JAX synchronization before recording end time
        if sync_jax:
            sync_jax_if_needed(backend)

        stage3_end = time.time()
        stage3_time = stage3_end - stage3_start
        total_time = stage1_time + stage2_time + stage3_time
        
        # Generate hash for Stage 3 output (result)
        stage3_hash = hashlib.md5(str(result).encode('utf-8')).hexdigest()
        
        # Final memory reading
        final_memory = get_memory_usage_mb()
        if tracker:
            tracker.stop_monitoring()
        
        # Determine result shape and type
        if hasattr(result, 'shape'):
            result_shape = result.shape
        else:
            result_shape = getattr(result, 'shape', None)
        
        print(f"  ✓ Stage 1 (pre-processing): {stage1_time:.4f}s ({stage1_time/total_time*100:.1f}%)")
        print(f"  ✓ Stage 2 (computation): {stage2_time:.4f}s ({stage2_time/total_time*100:.1f}%)")
        print(f"  ✓ Stage 3 (post-processing): {stage3_time:.4f}s ({stage3_time/total_time*100:.1f}%)")
        print(f"  ✓ Total time: {total_time:.4f} seconds")
        if result_shape:
            print(f"  Result shape: {result_shape}")
        else:
            print(f"  Result type: {type(result)}")
        print(f"  Memory usage: {initial_memory:.1f} MB → {final_memory:.1f} MB (Δ{final_memory-initial_memory:+.1f} MB)")
        print(f"  Stage 1 hash: {stage1_hash[:16]}...")
        print(f"  Stage 2 hash: {stage2_hash[:16]}...")
        print(f"  Stage 3 hash: {stage3_hash[:16]}...")
        
        return {
            'stage1_time': stage1_time,
            'stage2_time': stage2_time,
            'stage3_time': stage3_time,
            'execution_time': total_time,  # Keep for backwards compatibility
            'stage1_hash': stage1_hash,
            'stage2_hash': stage2_hash,
            'stage3_hash': stage3_hash,
            'initial_memory': initial_memory,
            'final_memory': final_memory,
            'memory_delta': final_memory - initial_memory,
            'result_shape': result_shape,
            'memory_tracker': tracker,
            'peak_memory': tracker.get_peak() if tracker else final_memory
        }
        
    except Exception as e:
        print(f"  ✗ Failed: {str(e)}")
        if tracker:
            tracker.stop_monitoring()
        return {
            'stage1_time': None,
            'stage2_time': None,
            'stage3_time': None,
            'execution_time': None,
            'result_hash': None,
            'initial_memory': initial_memory,
            'final_memory': get_memory_usage_mb(),
            'memory_delta': None,
            'result_shape': None,
            'memory_tracker': tracker,
            'peak_memory': tracker.get_peak() if tracker else get_memory_usage_mb(),
            'error': str(e)
        }

if __name__ == "__main__":
    # Dataset sizes (number of households)
    household_sizes = [2**15-1, 2**15, 2**16, 2**17, 2**18, 2**19, 2**20, 2**21]
    # household_sizes = [2**15-1, 2**15] # for testing purposes
    backends = ["numpy", "jax"]
    
    results = {}
    
    # Add metadata
    results["metadata"] = {
        "timestamp": datetime.now().isoformat(),
        "household_sizes": household_sizes,
        "backends": backends
    }
    
    for backend in backends:
        print(f"\n{'='*60}")
        print(f"Testing {backend} backend")
        print(f"{'='*60}")
        
        # Clear all caches and reset session before starting new backend
        print(f"Preparing environment for {backend} backend...")
        reset_session_state(backend)
        
        for N_households in household_sizes:
            # Add extra session reset for larger datasets to ensure clean state
            reset_between_sizes = N_households >= 2**18  # Reset for 256k+ households
            
            result = run_benchmark(
                N_households, 
                backend, 
                reset_session=False, # reset_between_sizes (no impact on results)
                sync_jax=True,  # Set to True if you want to force JAX synchronization
                                # Seems necessary for realistic (reported time = wall clock time) JAX timings
            )
            if result and result.get('execution_time'):
                # Store all stage timing data
                results[f"{N_households}_{backend}_stage1_time"] = result['stage1_time']
                results[f"{N_households}_{backend}_stage2_time"] = result['stage2_time'] 
                results[f"{N_households}_{backend}_stage3_time"] = result['stage3_time']
                results[f"{N_households}_{backend}_time"] = result['execution_time']  # Total time
                results[f"{N_households}_{backend}_stage1_hash"] = result['stage1_hash']
                results[f"{N_households}_{backend}_stage2_hash"] = result['stage2_hash']
                results[f"{N_households}_{backend}_stage3_hash"] = result['stage3_hash']
                results[f"{N_households}_{backend}_initial_memory"] = result['initial_memory']
                results[f"{N_households}_{backend}_final_memory"] = result['final_memory']
                results[f"{N_households}_{backend}_memory_delta"] = result['memory_delta']
                results[f"{N_households}_{backend}_peak_memory"] = result['peak_memory']
                results[f"{N_households}_{backend}_result_shape"] = result['result_shape']
            else:
                # Store None values for failed runs
                results[f"{N_households}_{backend}_stage1_time"] = None
                results[f"{N_households}_{backend}_stage2_time"] = None 
                results[f"{N_households}_{backend}_stage3_time"] = None
                results[f"{N_households}_{backend}_time"] = None
                results[f"{N_households}_{backend}_hash"] = None
                results[f"{N_households}_{backend}_initial_memory"] = None
                results[f"{N_households}_{backend}_final_memory"] = None
                results[f"{N_households}_{backend}_memory_delta"] = None
                results[f"{N_households}_{backend}_peak_memory"] = None
                results[f"{N_households}_{backend}_result_shape"] = None
            print()
        
        # Comprehensive cleanup after completing all sizes for this backend
        print(f"Completing {backend} backend tests...")
        # reset_session_state(backend)
        print(f"{backend} backend tests completed with full cleanup")
    
    # Save results to JSON file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"benchmark_results_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {filename}")
    
    print(f"\n{'='*120}")
    print("3-STAGE TIMING BREAKDOWN")
    print(f"{'='*120}")
    
    # Print comparison table in the requested format
    print(f"\n{'='*101}")
    print("PERFORMANCE COMPARISON NUMPY <-> JAX")
    print(f"{'='*104}")
    print(f"{'Households':<12}{'Stage':<18}{'NUMPY hash':<12}{'JAX hash':<12}{'NUMPY (s)':<12}{'JAX (s)':<12}{'Speedup':<12}")
    print("-" * 104)
    
    for N_households in household_sizes:
        # Get timing data for all stages
        numpy_s1 = results.get(f"{N_households}_numpy_stage1_time")
        numpy_s2 = results.get(f"{N_households}_numpy_stage2_time")
        numpy_s3 = results.get(f"{N_households}_numpy_stage3_time")
        numpy_total = results.get(f"{N_households}_numpy_time")
        
        jax_s1 = results.get(f"{N_households}_jax_stage1_time")
        jax_s2 = results.get(f"{N_households}_jax_stage2_time")
        jax_s3 = results.get(f"{N_households}_jax_stage3_time")
        jax_total = results.get(f"{N_households}_jax_time")
        
        numpy_hash = results.get(f"{N_households}_numpy_hash")
        jax_hash = results.get(f"{N_households}_jax_hash")
        
        # Get stage-specific hashes
        numpy_s1_hash = results.get(f"{N_households}_numpy_stage1_hash")
        numpy_s2_hash = results.get(f"{N_households}_numpy_stage2_hash")
        numpy_s3_hash = results.get(f"{N_households}_numpy_stage3_hash")
        
        jax_s1_hash = results.get(f"{N_households}_jax_stage1_hash")
        jax_s2_hash = results.get(f"{N_households}_jax_stage2_hash")
        jax_s3_hash = results.get(f"{N_households}_jax_stage3_hash")
        
        # Truncate hashes for display
        numpy_s1_hash_display = numpy_s1_hash[:8] if numpy_s1_hash else "N/A"
        numpy_s2_hash_display = numpy_s2_hash[:8] if numpy_s2_hash else "N/A"
        numpy_s3_hash_display = numpy_s3_hash[:8] if numpy_s3_hash else "N/A"
        
        jax_s1_hash_display = jax_s1_hash[:8] if jax_s1_hash else "N/A"
        jax_s2_hash_display = jax_s2_hash[:8] if jax_s2_hash else "N/A"
        jax_s3_hash_display = jax_s3_hash[:8] if jax_s3_hash else "N/A"
        
        # Check if we have valid data
        if all(x is not None for x in [numpy_s1, numpy_s2, numpy_s3, jax_s1, jax_s2, jax_s3]):
            # Pre-processing row (Stage 1 hashes often unstable due to dict return)
            s1_speedup = numpy_s1 / jax_s1 if jax_s1 and jax_s1 > 0 else 0
            s1_speedup_str = f"{s1_speedup:.2f}x" if s1_speedup >= 1 else f"1/{jax_s1/numpy_s1:.2f}x" if numpy_s1 and numpy_s1 > 0 else "N/A"
            print(f"{N_households:<12,}{'pre-processing':<18}{'-':<12}{'-':<12}{numpy_s1:<12.4f}{jax_s1:<12.4f}{s1_speedup_str:<12}")
            
            # Computation row (Stage 2 hashes should be stable)
            s2_speedup = numpy_s2 / jax_s2 if jax_s2 and jax_s2 > 0 else 0
            s2_speedup_str = f"{s2_speedup:.2f}x" if s2_speedup >= 1 else f"1/{jax_s2/numpy_s2:.2f}x" if numpy_s2 and numpy_s2 > 0 else "N/A"
            print(f"{'':>12}{'computation':<18}{numpy_s2_hash_display:<12}{jax_s2_hash_display:<12}{numpy_s2:<12.4f}{jax_s2:<12.4f}{s2_speedup_str:<12}")
            
            # Post-processing row (Stage 3 hashes should be stable)
            s3_speedup = numpy_s3 / jax_s3 if jax_s3 and jax_s3 > 0 else 0
            s3_speedup_str = f"{s3_speedup:.2f}x" if s3_speedup >= 1 else f"1/{jax_s3/numpy_s3:.2f}x" if numpy_s3 and numpy_s3 > 0 else "N/A"
            print(f"{'':>12}{'post-processing':<18}{numpy_s3_hash_display:<12}{jax_s3_hash_display:<12}{numpy_s3:<12.4f}{jax_s3:<12.4f}{s3_speedup_str:<12}")
            
            # Total time row
            if numpy_total and jax_total:
                total_speedup = numpy_total / jax_total if jax_total > 0 else 0
                total_speedup_str = f"{total_speedup:.2f}x" if total_speedup >= 1 else f"1/{jax_total/numpy_total:.2f}x" if numpy_total > 0 else "N/A"
                print(f"{'':>12}{'total time':<18}{'':>12}{'':>12}{numpy_total:<12.4f}{jax_total:<12.4f}{total_speedup_str:<12}")
            
            print("-" * 104)
        else:
            # Handle failed cases - show "N/A" for hashes in failed cases
            numpy_time_str = f"{numpy_total:.4f}" if numpy_total is not None else "FAILED"
            jax_time_str = f"{jax_total:.4f}" if jax_total is not None else "FAILED"
            print(f"{N_households:<12,}{'FAILED':<18}{'N/A':<12}{'N/A':<12}{numpy_time_str:<12}{jax_time_str:<12}{'N/A':<12}")
            print("-" * 104)
    
    # Print memory comparison
    print(f"\n{'='*120}")
    print("MEMORY USAGE COMPARISON")
    print(f"{'='*120}")
    print(f"{'Households':<12}{'NumPy Init':<12}{'NumPy Final':<12}{'JAX Init':<12}{'JAX Final':<12}{'NumPy Δ':<12}{'JAX Δ':<12}")
    print("-" * 120)
    
    for N_households in household_sizes:
        numpy_init = results.get(f"{N_households}_numpy_initial_memory")
        numpy_final = results.get(f"{N_households}_numpy_final_memory")
        jax_init = results.get(f"{N_households}_jax_initial_memory")
        jax_final = results.get(f"{N_households}_jax_final_memory")
        numpy_delta = results.get(f"{N_households}_numpy_memory_delta")
        jax_delta = results.get(f"{N_households}_jax_memory_delta")
        
        if all(x is not None for x in [numpy_init, numpy_final, jax_init, jax_final]):
            print(f"{N_households:<12,}{numpy_init:<12.1f}{numpy_final:<12.1f}{jax_init:<12.1f}{jax_final:<12.1f}{numpy_delta:<12.1f}{jax_delta:<12.1f}")
        else:
            print(f"{N_households:<12,}{'N/A':<12}{'N/A':<12}{'N/A':<12}{'N/A':<12}{'N/A':<12}{'N/A':<12}")
    
    print("-" * 120)
    print("\nLegend:")
    print("  Stage 1: Data preprocessing & DAG creation")
    print("  Stage 2: Core computation (tax/transfer calculations)")
    print("  Stage 3: DataFrame formatting (JAX → pandas conversion)")
    print("  Init/Final: Memory usage before/after execution")
    print("  Δ: Memory increase during execution")
    print("  ✓/✗: Hash verification (results match/differ)")
    
    print(f"\n{'='*120}")
    print("BENCHMARK COMPLETED")
    print(f"{'='*120}")
    print(f"Results saved to: {filename}")
    print(f"Generated at: {datetime.now().isoformat()}")
