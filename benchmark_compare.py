"""
Script to compare benchmark results from main branch vs PR branch.
This script loads two JSON files from benchmark_stages.py runs and creates
comparison tables showing the impact of optimizations with 3-stage breakdown.

Usage:
    python benchmark_compare.py main_results.json pr_results.json [--save-comparison]
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
    """Print comparison table for JAX backend with 3-stage breakdown."""
    print(f"\n{'='*140}")
    print("JAX BACKEND COMPARISON: Main Branch vs PR Branch - 3-STAGE BREAKDOWN")
    print(f"{'='*140}")
    print(f"{'Households':<12}{'Stage':<18}{'Main (s)':<12}{'PR (s)':<12}{'Speedup':<12}{'Description':<25}{'Hash Match':<12}")
    print("-" * 140)
    
    for N_households in household_sizes:
        # Get timing data for all stages
        main_s1 = main_results.get(f"{N_households}_jax_stage1_time")
        main_s2 = main_results.get(f"{N_households}_jax_stage2_time")
        main_s3 = main_results.get(f"{N_households}_jax_stage3_time")
        main_total = main_results.get(f"{N_households}_jax_time")
        
        pr_s1 = pr_results.get(f"{N_households}_jax_stage1_time")
        pr_s2 = pr_results.get(f"{N_households}_jax_stage2_time")
        pr_s3 = pr_results.get(f"{N_households}_jax_stage3_time")
        pr_total = pr_results.get(f"{N_households}_jax_time")
        
        # Get stage-specific hashes
        main_s1_hash = main_results.get(f"{N_households}_jax_stage1_hash")
        main_s2_hash = main_results.get(f"{N_households}_jax_stage2_hash")
        main_s3_hash = main_results.get(f"{N_households}_jax_stage3_hash")
        
        pr_s1_hash = pr_results.get(f"{N_households}_jax_stage1_hash")
        pr_s2_hash = pr_results.get(f"{N_households}_jax_stage2_hash")
        pr_s3_hash = pr_results.get(f"{N_households}_jax_stage3_hash")
        
        # Check hash matches for each stage
        # Stage 1 hashes are intentionally omitted due to instability, so show empty
        s1_hash_match = ""
        s2_hash_match = "✓" if main_s2_hash == pr_s2_hash else "✗" if main_s2_hash and pr_s2_hash else "N/A"
        s3_hash_match = "✓" if main_s3_hash == pr_s3_hash else "✗" if main_s3_hash and pr_s3_hash else "N/A"
        
        # Check if we have valid data
        if all(x is not None for x in [main_s1, main_s2, main_s3, pr_s1, pr_s2, pr_s3]):
            # Stage 1 row
            s1_speedup = main_s1 / pr_s1
            s1_speedup_str = f"{s1_speedup:.2f}x" if s1_speedup >= 1 else f"1/{pr_s1/main_s1:.2f}x"
            print(f"{N_households:<12,}{'pre-processing':<18}{main_s1:<12.4f}{pr_s1:<12.4f}{s1_speedup_str:<12}{'Data preprocessing':<25}{s1_hash_match:<12}")
            
            # Stage 2 row
            s2_speedup = main_s2 / pr_s2  
            s2_speedup_str = f"{s2_speedup:.2f}x" if s2_speedup >= 1 else f"1/{pr_s2/main_s2:.2f}x"
            print(f"{'':>12}{'computation':<18}{main_s2:<12.4f}{pr_s2:<12.4f}{s2_speedup_str:<12}{'Core computation':<25}{s2_hash_match:<12}")
            
            # Stage 3 row
            s3_speedup = main_s3 / pr_s3
            s3_speedup_str = f"{s3_speedup:.2f}x" if s3_speedup >= 1 else f"1/{pr_s3/main_s3:.2f}x"
            print(f"{'':>12}{'post-processing':<18}{main_s3:<12.4f}{pr_s3:<12.4f}{s3_speedup_str:<12}{'DataFrame formatting':<25}{s3_hash_match:<12}")
            
            # Total row
            if main_total and pr_total:
                total_speedup = main_total / pr_total
                total_speedup_str = f"{total_speedup:.2f}x" if total_speedup >= 1 else f"1/{pr_total/main_total:.2f}x"
                print(f"{'':>12}{'total time':<18}{main_total:<12.4f}{pr_total:<12.4f}{total_speedup_str:<12}{'Complete execution':<25}{'':<12}")
            
            print("-" * 140)
        else:
            # Handle failed cases
            main_time_str = f"{main_total:.4f}" if main_total is not None else "FAILED"
            pr_time_str = f"{pr_total:.4f}" if pr_total is not None else "FAILED"
            print(f"{N_households:<12,}{'FAILED':<18}{main_time_str:<12}{pr_time_str:<12}{'N/A':<12}{'Benchmark failed':<25}{'N/A':<12}")
            print("-" * 140)

def print_numpy_comparison_table(main_results, pr_results, household_sizes):
    """Print comparison table for NumPy backend with 3-stage breakdown."""
    print(f"\n{'='*140}")
    print("NUMPY BACKEND COMPARISON: Main Branch vs PR Branch - 3-STAGE BREAKDOWN")
    print(f"{'='*140}")
    print(f"{'Households':<12}{'Stage':<18}{'Main (s)':<12}{'PR (s)':<12}{'Speedup':<12}{'Description':<25}{'Hash Match':<12}")
    print("-" * 140)
    
    for N_households in household_sizes:
        # Get timing data for all stages
        main_s1 = main_results.get(f"{N_households}_numpy_stage1_time")
        main_s2 = main_results.get(f"{N_households}_numpy_stage2_time")
        main_s3 = main_results.get(f"{N_households}_numpy_stage3_time")
        main_total = main_results.get(f"{N_households}_numpy_time")
        
        pr_s1 = pr_results.get(f"{N_households}_numpy_stage1_time")
        pr_s2 = pr_results.get(f"{N_households}_numpy_stage2_time")
        pr_s3 = pr_results.get(f"{N_households}_numpy_stage3_time")
        pr_total = pr_results.get(f"{N_households}_numpy_time")
        
        # Get stage-specific hashes
        main_s1_hash = main_results.get(f"{N_households}_numpy_stage1_hash")
        main_s2_hash = main_results.get(f"{N_households}_numpy_stage2_hash")
        main_s3_hash = main_results.get(f"{N_households}_numpy_stage3_hash")
        
        pr_s1_hash = pr_results.get(f"{N_households}_numpy_stage1_hash")
        pr_s2_hash = pr_results.get(f"{N_households}_numpy_stage2_hash")
        pr_s3_hash = pr_results.get(f"{N_households}_numpy_stage3_hash")
        
        # Check hash matches for each stage
        # Stage 1 hashes are intentionally omitted due to instability, so show empty
        s1_hash_match = ""
        s2_hash_match = "✓" if main_s2_hash == pr_s2_hash else "✗" if main_s2_hash and pr_s2_hash else "N/A"
        s3_hash_match = "✓" if main_s3_hash == pr_s3_hash else "✗" if main_s3_hash and pr_s3_hash else "N/A"
        
        # Check if we have valid data
        if all(x is not None for x in [main_s1, main_s2, main_s3, pr_s1, pr_s2, pr_s3]):
            # Stage 1 row
            s1_speedup = main_s1 / pr_s1
            s1_speedup_str = f"{s1_speedup:.2f}x" if s1_speedup >= 1 else f"1/{pr_s1/main_s1:.2f}x"
            print(f"{N_households:<12,}{'pre-processing':<18}{main_s1:<12.4f}{pr_s1:<12.4f}{s1_speedup_str:<12}{'Data preprocessing':<25}{s1_hash_match:<12}")
            
            # Stage 2 row
            s2_speedup = main_s2 / pr_s2  
            s2_speedup_str = f"{s2_speedup:.2f}x" if s2_speedup >= 1 else f"1/{pr_s2/main_s2:.2f}x"
            print(f"{'':>12}{'computation':<18}{main_s2:<12.4f}{pr_s2:<12.4f}{s2_speedup_str:<12}{'Core computation':<25}{s2_hash_match:<12}")
            
            # Stage 3 row
            s3_speedup = main_s3 / pr_s3
            s3_speedup_str = f"{s3_speedup:.2f}x" if s3_speedup >= 1 else f"1/{pr_s3/main_s3:.2f}x"
            print(f"{'':>12}{'post-processing':<18}{main_s3:<12.4f}{pr_s3:<12.4f}{s3_speedup_str:<12}{'DataFrame formatting':<25}{s3_hash_match:<12}")
            
            # Total row
            if main_total and pr_total:
                total_speedup = main_total / pr_total
                total_speedup_str = f"{total_speedup:.2f}x" if total_speedup >= 1 else f"1/{pr_total/main_total:.2f}x"
                print(f"{'':>12}{'total time':<18}{main_total:<12.4f}{pr_total:<12.4f}{total_speedup_str:<12}{'Complete execution':<25}{'':<12}")
            
            print("-" * 140)
        else:
            # Handle failed cases
            main_time_str = f"{main_total:.4f}" if main_total is not None else "FAILED"
            pr_time_str = f"{pr_total:.4f}" if pr_total is not None else "FAILED"
            print(f"{N_households:<12,}{'FAILED':<18}{main_time_str:<12}{pr_time_str:<12}{'N/A':<12}{'Benchmark failed':<25}{'N/A':<12}")
            print("-" * 140)

def print_summary_statistics(main_results, pr_results, household_sizes):
    """Print summary statistics comparing main vs PR performance with 3-stage breakdown."""
    print(f"\n{'='*100}")
    print("SUMMARY STATISTICS - 3-STAGE BREAKDOWN")
    print(f"{'='*100}")
    
    backends = ["numpy", "jax"]
    stages = ["stage1", "stage2", "stage3", "total"]
    stage_names = {
        "stage1": "Stage 1 (preprocessing)",
        "stage2": "Stage 2 (computation)",
        "stage3": "Stage 3 (formatting)",
        "total": "Total execution"
    }
    
    for backend in backends:
        print(f"\n{backend.upper()} Backend:")
        print("-" * 40)
        
        for stage in stages:
            if stage == "total":
                time_suffix = "_time"
            else:
                time_suffix = f"_{stage}_time"
            
            valid_speedups = []
            successful_runs = 0
            total_runs = len(household_sizes)
            
            for N_households in household_sizes:
                main_time = main_results.get(f"{N_households}_{backend}{time_suffix}")
                pr_time = pr_results.get(f"{N_households}_{backend}{time_suffix}")
                
                if main_time is not None and pr_time is not None:
                    successful_runs += 1
                    speedup = main_time / pr_time
                    valid_speedups.append(speedup)
            
            if valid_speedups:
                avg_speedup = sum(valid_speedups) / len(valid_speedups)
                max_speedup = max(valid_speedups)
                min_speedup = min(valid_speedups)
                
                print(f"  {stage_names[stage]}:")
                print(f"    Average speedup: {avg_speedup:.2f}x")
                print(f"    Maximum speedup: {max_speedup:.2f}x")
                print(f"    Minimum speedup: {min_speedup:.2f}x")
                print(f"    Successful runs: {successful_runs}/{total_runs}")
            else:
                print(f"  {stage_names[stage]}: No valid comparisons available")
        
        # Check hash consistency for all stages
        stage_hash_results = {}
        for stage_num in [1, 2, 3]:
            hash_mismatches = 0
            total_comparisons = 0
            
            for N_households in household_sizes:
                main_hash = main_results.get(f"{N_households}_{backend}_stage{stage_num}_hash")
                pr_hash = pr_results.get(f"{N_households}_{backend}_stage{stage_num}_hash")
                
                if main_hash and pr_hash:
                    total_comparisons += 1
                    if main_hash != pr_hash:
                        hash_mismatches += 1
            
            stage_hash_results[stage_num] = (hash_mismatches, total_comparisons)
        
        # Print hash verification results
        all_stages_perfect = True
        for stage_num in [1, 2, 3]:
            hash_mismatches, total_comparisons = stage_hash_results[stage_num]
            stage_name = {1: "Stage 1", 2: "Stage 2", 3: "Stage 3"}[stage_num]
            
            if total_comparisons > 0:
                print(f"  {stage_name} hash verification: {hash_mismatches}/{total_comparisons} mismatches")
                if hash_mismatches > 0:
                    all_stages_perfect = False
            else:
                print(f"  {stage_name} hash verification: No valid comparisons available")
                all_stages_perfect = False
        
        if all_stages_perfect and any(total for _, total in stage_hash_results.values()):
            print(f"  ✓ All stage results are numerically identical")
        elif any(mismatches for mismatches, _ in stage_hash_results.values()):
            print(f"  ⚠ Some stage results differ between main and PR")
        else:
            print(f"  No valid hash comparisons available")
    
    # Overall comparison
    print(f"\n{'='*100}")
    print("OVERALL PERFORMANCE IMPACT")
    print(f"{'='*100}")
    
    for backend in backends:
        total_speedups = []
        for N_households in household_sizes:
            main_total = main_results.get(f"{N_households}_{backend}_time")
            pr_total = pr_results.get(f"{N_households}_{backend}_time")
            
            if main_total and pr_total:
                total_speedups.append(main_total / pr_total)
        
        if total_speedups:
            avg_speedup = sum(total_speedups) / len(total_speedups)
            if avg_speedup > 1.05:
                impact = f"PR is {avg_speedup:.1f}x faster (significant improvement)"
            elif avg_speedup < 0.95:
                impact = f"PR is {1/avg_speedup:.1f}x slower (performance regression)"
            else:
                impact = "PR has minimal performance impact (±5%)"
            
            print(f"{backend.upper()}: {impact}")
        else:
            print(f"{backend.upper()}: No valid performance comparisons available")

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
