# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GETTSIM (German Taxes and Transfers SIMulator) is a Python microsimulation model for the German tax and transfer system. It enables research applications from dynamic programming models to detailed microsimulation studies.

The core computation engine is provided by `ttsim-backend`. GETTSIM contains the policy definitions, parameters, and tests specific to Germany.

## Common Commands

```bash
# Run all tests (numpy backend)
pixi run tests

# Run tests with JAX backend
pixi run tests-jax

# Run a single test file
pixi run pytest src/gettsim/tests_germany/test_policy_cases.py

# Run tests for a specific policy area (by test ID pattern)
pixi run pytest -k "kindergeld"

# Type checking
pixi run ty

# Build documentation
pixi run docs
```

## Architecture

### Source Layout

- `src/gettsim/germany/` - Policy implementations organized by area (einkommensteuer, kindergeld, bürgergeld, etc.)
- `src/gettsim/tests_germany/policy_cases/` - Test cases organized by policy area and date
- `src/gettsim/tt/` - Re-exports from ttsim-backend (decorators, types)

### Policy Functions

Policy functions use decorators from `gettsim.tt`:

```python
@policy_function(start_date="2023-01-01", leaf_name="betrag_m")
def betrag_ohne_staffelung_m(anzahl_ansprüche: int, satz: float) -> float:
    return satz * anzahl_ansprüche
```

Key decorators:
- `@policy_function` - Main policy calculation functions with date ranges
- `@policy_input` - Input column definitions (no implementation body)
- `@param_function` - Functions that transform raw parameters
- `@agg_by_p_id_function` - Aggregation functions by person ID
- `@agg_by_group_function` - Aggregation functions by group
- `@group_creation_function` - Functions that create group IDs (e.g., fg_id, bg_id)

Policy functions can have a `vectorization_strategy="not_required"` parameter for functions that operate on full columns directly (using `xnp` for numpy/jax compatibility).

### Parameters

Policy parameters are in YAML files alongside the Python code. Each parameter has:
- Date-keyed values (e.g., `2023-01-01:`)
- Metadata (name, description in de/en, unit, reference_period, type)
- Legal references

### Test Cases

Tests use YAML files in `tests_germany/policy_cases/{area}/{date}/`:

```yaml
inputs:
  provided:
    alter: [35, 35, 12]
    p_id: [0, 1, 2]
    hh_id: [0, 0, 0]
    # Nested paths use double underscore in code, but nested dicts in YAML
    kindergeld:
      in_ausbildung: [false, false, true]
      p_id_empfänger: [-1, -1, 0]
outputs:
  kindergeld:
    betrag_m: [250, 0, 0]
```

## Code Restrictions for Vectorization

Functions must follow these rules for automatic vectorization:

1. **If-else blocks**: Only one operation per branch, no return inside single if (must have else)
2. **Function calls**: `sum`, `any`, `all` require iterable arguments; `min`, `max` take exactly 2 args or 1 iterable
3. **No elif after else**: Use nested if-else instead

## Conventions

- German names for policy-specific code (reflects actual law names: Kindergeld, Bürgergeld, etc.)
- English for infrastructure code
- Uses pixi for environment management
- Pre-commit hooks for formatting (install with `pixi run pre-commit install`)
