"""Performance comparison script for numpy vs jax backends."""
import pandas as pd
from gettsim import InputData, MainTarget, TTTargets, main
import time
import hashlib
import json
import os
import psutil
import gc
import threading
from datetime import datetime
from make_data import make_data

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

def run_benchmark(N_households, backend):
    print(f"Generating dataset with {N_households:,} households...")
    # Force garbage collection before starting
    gc.collect()
    
    # Measure baseline memory
    baseline_memory = get_memory_usage_mb()
    
    # Create dataset but don't include this time in benchmark
    data = make_data(N_households)
    print(f"Dataset shape: {data.shape}")
    
    # Memory after data creation
    after_data_memory = get_memory_usage_mb()
    data_size_mb = after_data_memory - baseline_memory
    
    # Calculate theoretical data size for comparison
    theoretical_size_mb = (data.memory_usage(deep=True).sum()) / (1024 * 1024)
    
    print(f"Running with {backend} backend...")
    print(f"  Baseline memory: {baseline_memory:.1f} MB")
    print(f"  After data creation: {after_data_memory:.1f} MB (+{data_size_mb:.1f} MB)")
    print(f"  Theoretical DataFrame size: {theoretical_size_mb:.1f} MB")
    print(f"  Data creation efficiency: {theoretical_size_mb/data_size_mb:.2f}x" if data_size_mb > 0 else "  Data creation efficiency: N/A")
    
    # Force another GC and measure again before execution
    gc.collect()
    pre_execution_memory = get_memory_usage_mb()
    
    start_time = time.time()
    start_memory = pre_execution_memory
    
    # Initialize memory tracker with continuous monitoring
    memory_tracker = MemoryTracker()
    memory_tracker.start_monitoring()
    
    try:
        result = main(
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
            include_warn_nodes=False,
        )
        
        end_time = time.time()
        end_memory = memory_tracker.update()  # Update and get current memory
        execution_time = end_time - start_time
        
        # Stop monitoring and get peak memory
        memory_tracker.stop_monitoring()
        peak_memory = memory_tracker.get_peak()
        memory_increase = peak_memory - start_memory
        memory_increase_ratio = memory_increase / data_size_mb if data_size_mb > 0 else 0
        memory_increase_ratio_theoretical = memory_increase / theoretical_size_mb if theoretical_size_mb > 0 else 0
        
        # Calculate hash to verify result correctness
        result_hash = hashlib.md5(str(result).encode()).hexdigest()[:8]
        
        print(f"  Pre-execution memory (after GC): {pre_execution_memory:.1f} MB")
        print(f"  Start execution memory: {start_memory:.1f} MB")
        print(f"  End execution memory: {end_memory:.1f} MB")
        print(f"  Peak memory during execution: {peak_memory:.1f} MB")
        print(f"  Memory increase during execution: {memory_increase:.1f} MB")
        print(f"  Ratio vs measured data size: {memory_increase_ratio:.1f}x")
        print(f"  Ratio vs theoretical data size: {memory_increase_ratio_theoretical:.1f}x")
        print(f"✓ Success: {execution_time:.4f} seconds with {backend} (hash: {result_hash})")
        
        return {
            'execution_time': execution_time,
            'result_hash': result_hash,
            'baseline_memory': baseline_memory,
            'data_size_mb': data_size_mb,
            'theoretical_size_mb': theoretical_size_mb,
            'pre_execution_memory': pre_execution_memory,
            'start_memory': start_memory,
            'end_memory': end_memory,
            'peak_memory': peak_memory,
            'memory_increase': memory_increase,
            'memory_increase_ratio': memory_increase_ratio,
            'memory_increase_ratio_theoretical': memory_increase_ratio_theoretical
        }
        
    except Exception as e:
        # Make sure monitoring stops even if there's an error
        memory_tracker.stop_monitoring()
        print(f"✗ Error with {backend}: {e}")
        return None

if __name__ == "__main__":
    # Dataset sizes (number of households)
    household_sizes = [2**15-1, 2**15, 2**16, 2**17, 2**18, 2**19, 2**20, 2**21]
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
        
        for N_households in household_sizes:
            result = run_benchmark(N_households, backend)
            if result:
                results[f"{N_households}_{backend}_time"] = result['execution_time']
                results[f"{N_households}_{backend}_hash"] = result['result_hash']
                results[f"{N_households}_{backend}_baseline_memory"] = result['baseline_memory']
                results[f"{N_households}_{backend}_data_size"] = result['data_size_mb']
                results[f"{N_households}_{backend}_theoretical_size"] = result['theoretical_size_mb']
                results[f"{N_households}_{backend}_pre_execution_memory"] = result['pre_execution_memory']
                results[f"{N_households}_{backend}_start_memory"] = result['start_memory']
                results[f"{N_households}_{backend}_end_memory"] = result['end_memory']
                results[f"{N_households}_{backend}_peak_memory"] = result['peak_memory']
                results[f"{N_households}_{backend}_memory_increase"] = result['memory_increase']
                results[f"{N_households}_{backend}_memory_increase_ratio"] = result['memory_increase_ratio']
                results[f"{N_households}_{backend}_memory_increase_ratio_theoretical"] = result['memory_increase_ratio_theoretical']
            else:
                results[f"{N_households}_{backend}_time"] = None
                results[f"{N_households}_{backend}_hash"] = None
                results[f"{N_households}_{backend}_baseline_memory"] = None
                results[f"{N_households}_{backend}_data_size"] = None
                results[f"{N_households}_{backend}_theoretical_size"] = None
                results[f"{N_households}_{backend}_pre_execution_memory"] = None
                results[f"{N_households}_{backend}_start_memory"] = None
                results[f"{N_households}_{backend}_end_memory"] = None
                results[f"{N_households}_{backend}_peak_memory"] = None
                results[f"{N_households}_{backend}_memory_increase"] = None
                results[f"{N_households}_{backend}_memory_increase_ratio"] = None
                results[f"{N_households}_{backend}_memory_increase_ratio_theoretical"] = None
            print()
    
    # Save results to JSON file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"benchmark_results_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {filename}")
    
    print(f"\n{'='*80}")
    print("SUMMARY TABLE")
    print(f"{'='*80}")
    
    # Print header
    print(f"{'Households':<12}", end="")
    for backend in backends:
        print(f"{backend + '_time':<12}{backend + '_hash':<12}", end="")
    print()
    
    print("-" * (12 + len(backends) * 24))
    
    # Print data rows
    for N_households in household_sizes:
        print(f"{N_households:<12,}", end="")
        for backend in backends:
            time_key = f"{N_households}_{backend}_time"
            hash_key = f"{N_households}_{backend}_hash"
            
            time_val = results.get(time_key)
            hash_val = results.get(hash_key)
            
            if time_val is not None:
                print(f"{time_val:<12.4f}{hash_val:<12}", end="")
            else:
                print(f"{'FAILED':<12}{'N/A':<12}", end="")
        print()
    
    # Print performance comparison
    print(f"\n{'='*80}")
    print("PERFORMANCE COMPARISON")
    print(f"{'='*80}")
    print(f"{'Households':<12}{'NumPy (s)':<12}{'JAX (s)':<12}{'NumPy Hash':<12}{'JAX Hash':<12}{'Speedup':<12}")
    print("-" * 80)
    
    for N_households in household_sizes:
        numpy_time = results.get(f"{N_households}_numpy_time")
        jax_time = results.get(f"{N_households}_jax_time")
        numpy_hash = results.get(f"{N_households}_numpy_hash")
        jax_hash = results.get(f"{N_households}_jax_hash")
        
        if numpy_time is not None and jax_time is not None:
            speedup = numpy_time / jax_time
            speedup_str = f"{speedup:.2f}x" if speedup >= 1 else f"1/{jax_time/numpy_time:.2f}x"
            print(f"{N_households:<12,}{numpy_time:<12.4f}{jax_time:<12.4f}{numpy_hash or 'N/A':<12}{jax_hash or 'N/A':<12}{speedup_str:<12}")
        else:
            print(f"{N_households:<12,}{'FAILED':<12}{'FAILED':<12}{'N/A':<12}{'N/A':<12}{'N/A':<12}")
    
    # Print memory comparison
    print(f"\n{'='*135}")
    print("MEMORY USAGE COMPARISON")
    print(f"{'='*135}")
    print(f"{'Households':<12}{'Baseline':<12}{'Data Size':<12}{'NumPy Peak':<12}{'JAX Peak':<12}{'NumPy Inc':<12}{'JAX Inc':<12}{'NumPy Ratio':<12}{'JAX Ratio':<12}{'Peak Ratio':<12}")
    print(f"{'(MB)':<12}{'(MB)':<12}{'(MB)':<12}{'(MB)':<12}{'(MB)':<12}{'(MB)':<12}{'(MB)':<12}{'(Inc/Data)':<12}{'(Inc/Data)':<12}{'(JAX/NumPy)':<12}")
    print("-" * 135)
    
    for N_households in household_sizes:
        baseline = results.get(f"{N_households}_numpy_baseline_memory") or results.get(f"{N_households}_jax_baseline_memory")
        data_size = results.get(f"{N_households}_numpy_data_size") or results.get(f"{N_households}_jax_data_size")
        numpy_peak = results.get(f"{N_households}_numpy_peak_memory")
        jax_peak = results.get(f"{N_households}_jax_peak_memory")
        numpy_inc = results.get(f"{N_households}_numpy_memory_increase")
        jax_inc = results.get(f"{N_households}_jax_memory_increase")
        numpy_ratio = results.get(f"{N_households}_numpy_memory_increase_ratio")
        jax_ratio = results.get(f"{N_households}_jax_memory_increase_ratio")
        
        if numpy_peak is not None and jax_peak is not None:
            peak_ratio = jax_peak / numpy_peak if numpy_peak > 0 else float('inf')
            peak_ratio_str = f"{peak_ratio:.2f}x"
            numpy_ratio_str = f"{numpy_ratio:.1f}x" if numpy_ratio is not None else "N/A"
            jax_ratio_str = f"{jax_ratio:.1f}x" if jax_ratio is not None else "N/A"
            baseline_str = f"{baseline:.1f}" if baseline is not None else "N/A"
            print(f"{N_households:<12,}{baseline_str:<12}{data_size:<12.1f}{numpy_peak:<12.1f}{jax_peak:<12.1f}{numpy_inc:<12.1f}{jax_inc:<12.1f}{numpy_ratio_str:<12}{jax_ratio_str:<12}{peak_ratio_str:<12}")
        else:
            baseline_str = f"{baseline:.1f}" if baseline is not None else "N/A"
            print(f"{N_households:<12,}{baseline_str:<12}{'N/A':<12}{'FAILED':<12}{'FAILED':<12}{'N/A':<12}{'N/A':<12}{'N/A':<12}{'N/A':<12}{'N/A':<12}")
    
    print("\nNote: Speedup > 1.0 means JAX is faster than NumPy")
    print("Note: Peak Ratio > 1.0 means JAX uses more peak memory than NumPy")
    print("Note: 'Inc' = Memory increase during execution (peak - start)")
    print("Note: 'Ratio' = Memory increase relative to input data size")
    print("Note: Higher ratios indicate more memory overhead relative to input data")
    print("Note: Identical hashes across backends confirm numerical consistency")
