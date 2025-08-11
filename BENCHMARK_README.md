# Benchmark Comparison Workflow

This document explains how to compare performance between the main branch and a PR branch with optimizations.

## Scripts Overview

1. **`benchmark.py`** - Runs performance benchmarks and saves results to JSON
2. **`compare_benchmark_results.py`** - Compares results from two benchmark runs

## Workflow

### Step 1: Run benchmark on main branch

```bash
# Switch to main branch (ttsim)
git checkout main

# Run benchmark
python benchmark.py

# This creates a file like: benchmark_results_20250806_143022.json
```

### Step 2: Run benchmark on PR branch 

```bash
# Switch to PR branch (ttsim)
git checkout JW/dev/speedup-JAX

# Run benchmark 
python benchmark.py

# This creates another file like: benchmark_results_20250806_145133.json
```

### Step 3: Compare results

```bash
# Compare the two result files (e.g. first file=main branch results, second file=PR branch results)
python benchmark_compare_stages.py benchmark_results_20250806_143022.json benchmark_results_20250806_145133.json

# Optional: Save comparison to file
python benchmark_compare_stages.py benchmark_results_20250806_143022.json benchmark_results_20250806_145133.json --save-comparison
```

## Interpreting Results

- **Speedup > 1.0**: PR branch is faster than main branch
- **Identical Hashes**: Optimizations maintain numerical accuracy
- **Hash Mismatches**: Potential numerical differences (investigate!)

## Dataset Sizes Tested

- 32,767 households (2^15 - 1)
- 32,768 households (2^15)
- 65,536 households (2^16)
- 131,072 households (2^17)
- 262,144 households (2^18)
- 524,288 households (2^19)
- 1,048,576 households (2^20)
- 2,097,152 households (2^21)
