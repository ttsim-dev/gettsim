"""
Script to compare benchmark results from main branch vs PR branch.
This script loads two JSON files from benchmark.py runs and creates
comparison tables showing the impact of optimizations.
"""

import json
import os
import sys
from datetime import datetime
import argparse

def load_benchmark_results(filepath):
    """Load benchmark results from JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{filepath}'.")
        return None

def extract_household_sizes(results):
    """Extract household sizes from results metadata or data keys."""
    if "metadata" in results and "household_sizes" in results["metadata"]:
        return results["metadata"]["household_sizes"]
    
    # Fallback: extract from data keys
    household_sizes = set()
    for key in results.keys():
        if key.endswith("_numpy_time") or key.endswith("_jax_time"):
            try:
                size = int(key.split("_")[0])
                household_sizes.add(size)
            except ValueError:
                continue
    
    return sorted(list(household_sizes))

def print_jax_comparison_table(main_results, pr_results, household_sizes):
    """Print comparison table for JAX backend."""
    print(f"\n{'='*90}")
    print("JAX BACKEND COMPARISON: Main Branch vs PR Branch")
    print(f"{'='*90}")
    print(f"{'Households':<12}{'JAX hash main':<15}{'JAX hash PR':<15}{'JAX main (s)':<15}{'JAX PR (s)':<15}{'Speedup':<12}")
    print("-" * 90)
    
    for N_households in household_sizes:
        main_time = main_results.get(f"{N_households}_jax_time")
        pr_time = pr_results.get(f"{N_households}_jax_time")
        main_hash = main_results.get(f"{N_households}_jax_hash")
        pr_hash = pr_results.get(f"{N_households}_jax_hash")
        
        if main_time is not None and pr_time is not None:
            speedup = main_time / pr_time
            speedup_str = f"{speedup:.2f}x" if speedup >= 1 else f"1/{pr_time/main_time:.2f}x"
            
            # Truncate hashes for display
            main_hash_display = (main_hash[:8] + "...") if main_hash and len(main_hash) > 8 else (main_hash or "N/A")
            pr_hash_display = (pr_hash[:8] + "...") if pr_hash and len(pr_hash) > 8 else (pr_hash or "N/A")
            
            print(f"{N_households:<12,}{main_hash_display:<15}{pr_hash_display:<15}{main_time:<15.4f}{pr_time:<15.4f}{speedup_str:<12}")
        else:
            main_time_str = f"{main_time:.4f}" if main_time is not None else "FAILED"
            pr_time_str = f"{pr_time:.4f}" if pr_time is not None else "FAILED"
            main_hash_display = (main_hash[:8] + "...") if main_hash else "N/A"
            pr_hash_display = (pr_hash[:8] + "...") if pr_hash else "N/A"
            
            print(f"{N_households:<12,}{main_hash_display:<15}{pr_hash_display:<15}{main_time_str:<15}{pr_time_str:<15}{'N/A':<12}")

def print_numpy_comparison_table(main_results, pr_results, household_sizes):
    """Print comparison table for NumPy backend."""
    print(f"\n{'='*90}")
    print("NUMPY BACKEND COMPARISON: Main Branch vs PR Branch")
    print(f"{'='*90}")
    print(f"{'Households':<12}{'NP hash main':<15}{'NP hash PR':<15}{'NP main (s)':<15}{'NP PR (s)':<15}{'Speedup':<12}")
    print("-" * 90)
    
    for N_households in household_sizes:
        main_time = main_results.get(f"{N_households}_numpy_time")
        pr_time = pr_results.get(f"{N_households}_numpy_time")
        main_hash = main_results.get(f"{N_households}_numpy_hash")
        pr_hash = pr_results.get(f"{N_households}_numpy_hash")
        
        if main_time is not None and pr_time is not None:
            speedup = main_time / pr_time
            speedup_str = f"{speedup:.2f}x" if speedup >= 1 else f"1/{pr_time/main_time:.2f}x"
            
            # Truncate hashes for display
            main_hash_display = (main_hash[:8] + "...") if main_hash and len(main_hash) > 8 else (main_hash or "N/A")
            pr_hash_display = (pr_hash[:8] + "...") if pr_hash and len(pr_hash) > 8 else (pr_hash or "N/A")
            
            print(f"{N_households:<12,}{main_hash_display:<15}{pr_hash_display:<15}{main_time:<15.4f}{pr_time:<15.4f}{speedup_str:<12}")
        else:
            main_time_str = f"{main_time:.4f}" if main_time is not None else "FAILED"
            pr_time_str = f"{pr_time:.4f}" if pr_time is not None else "FAILED"
            main_hash_display = (main_hash[:8] + "...") if main_hash else "N/A"
            pr_hash_display = (pr_hash[:8] + "...") if pr_hash else "N/A"
            
            print(f"{N_households:<12,}{main_hash_display:<15}{pr_hash_display:<15}{main_time_str:<15}{pr_time_str:<15}{'N/A':<12}")

def print_summary_statistics(main_results, pr_results, household_sizes):
    """Print summary statistics comparing main vs PR performance."""
    print(f"\n{'='*70}")
    print("SUMMARY STATISTICS")
    print(f"{'='*70}")
    
    backends = ["numpy", "jax"]
    
    for backend in backends:
        print(f"\n{backend.upper()} Backend:")
        print("-" * 20)
        
        valid_speedups = []
        hash_mismatches = 0
        total_comparisons = 0
        
        for N_households in household_sizes:
            main_time = main_results.get(f"{N_households}_{backend}_time")
            pr_time = pr_results.get(f"{N_households}_{backend}_time")
            main_hash = main_results.get(f"{N_households}_{backend}_hash")
            pr_hash = pr_results.get(f"{N_households}_{backend}_hash")
            
            if main_time is not None and pr_time is not None:
                speedup = main_time / pr_time
                valid_speedups.append(speedup)
                
                if main_hash and pr_hash:
                    total_comparisons += 1
                    if main_hash != pr_hash:
                        hash_mismatches += 1
        
        if valid_speedups:
            avg_speedup = sum(valid_speedups) / len(valid_speedups)
            max_speedup = max(valid_speedups)
            min_speedup = min(valid_speedups)
            
            print(f"  Average speedup: {avg_speedup:.2f}x")
            print(f"  Maximum speedup: {max_speedup:.2f}x")
            print(f"  Minimum speedup: {min_speedup:.2f}x")
            print(f"  Successful runs: {len(valid_speedups)}/{len(household_sizes)}")
        else:
            print(f"  No valid comparisons available")
        
        if total_comparisons > 0:
            print(f"  Hash mismatches: {hash_mismatches}/{total_comparisons}")
            if hash_mismatches == 0:
                print(f"  ✓ All results are numerically identical")
            else:
                print(f"  ⚠ Some results differ between main and PR")

def main():
    parser = argparse.ArgumentParser(description="Compare benchmark results from main branch vs PR branch")
    parser.add_argument("main_file", help="Path to benchmark results JSON file from main branch")
    parser.add_argument("pr_file", help="Path to benchmark results JSON file from PR branch")
    parser.add_argument("--save-comparison", help="Save comparison tables to text file", action="store_true")
    
    args = parser.parse_args()
    
    # Load benchmark results
    print("Loading benchmark results...")
    main_results = load_benchmark_results(args.main_file)
    pr_results = load_benchmark_results(args.pr_file)
    
    if main_results is None or pr_results is None:
        sys.exit(1)
    
    # Extract household sizes (use PR results as primary, fallback to main)
    household_sizes = extract_household_sizes(pr_results)
    if not household_sizes:
        household_sizes = extract_household_sizes(main_results)
    
    if not household_sizes:
        print("Error: Could not extract household sizes from either file.")
        sys.exit(1)
    
    print(f"Found data for household sizes: {household_sizes}")
    
    # Print comparison tables
    print_jax_comparison_table(main_results, pr_results, household_sizes)
    print_numpy_comparison_table(main_results, pr_results, household_sizes)
    print_summary_statistics(main_results, pr_results, household_sizes)
    
    # Save to file if requested
    if args.save_comparison:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"benchmark_comparison_{timestamp}.txt"
        
        # Redirect stdout to file
        original_stdout = sys.stdout
        
        try:
            with open(output_file, 'w') as f:
                sys.stdout = f
                print(f"Benchmark Comparison Report")
                print(f"Generated: {datetime.now().isoformat()}")
                print(f"Main branch file: {args.main_file}")
                print(f"PR branch file: {args.pr_file}")
                
                print_jax_comparison_table(main_results, pr_results, household_sizes)
                print_numpy_comparison_table(main_results, pr_results, household_sizes)
                print_summary_statistics(main_results, pr_results, household_sizes)
            
            sys.stdout = original_stdout
            print(f"\nComparison saved to: {output_file}")
            
        except Exception as e:
            sys.stdout = original_stdout
            print(f"Error saving comparison: {e}")

if __name__ == "__main__":
    main()
