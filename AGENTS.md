@.ai-instructions/profiles/tier-a.md @.ai-instructions/modules/jax.md
@.ai-instructions/modules/pandas.md @.ai-instructions/modules/dags.md

# GETTSIM

## Project Overview

GETTSIM (German Taxes and Transfers SIMulator) is a Python microsimulation model for the
German tax and transfer system. It enables research applications from dynamic
programming models to detailed microsimulation studies.

The core computation engine is provided by `ttsim-backend`. GETTSIM contains the policy
definitions, parameters, and tests specific to Germany.

Never work around limitations in `ttsim-backend`; any such changes should be made there.

## Common Commands

```bash
# Run all tests
pixi run -e py314-jax tests -n 7

# Run a single test file
pixi run -e py314-jax tests src/gettsim/tests_germany/test_policy_cases.py

# Run tests for a specific policy area (by test ID pattern)
pixi run -e py314-jax tests -k "kindergeld"

# Type checking
pixi run ty
pixi run ty-jax

# Quality checks (linting, formatting)
pixi run prek run --all-files

# Build documentation
pixi run docs
```

Before finishing any task that modifies code, always run these three verification steps
in order:

1. `pixi run ty` and `pixi run ty-jax` (type checker)
1. `pixi run prek run --all-files` (quality checks: linting, formatting, yaml, etc.)
1. `pixi run -e py314-jax tests -n 7` (full test suite)

## Architecture

### Source Layout

- `src/gettsim/germany/` - Policy implementations organized by area (einkommensteuer,
  kindergeld, bürgergeld, etc.)
- `src/gettsim/tests_germany/policy_cases/` - Test cases organized by policy area and
  date
- `src/gettsim/tt/` - Re-exports from ttsim-backend (decorators, types)

### Two-Level DAG System (GEP 4, 7)

1. **Interface DAG**: High-level orchestration connecting inputs to outputs via
   `main()`. Key concepts:

   - `policy_date`: Date for which the policy environment is set up
   - `policy_environment`: Functions/parameters relevant at the policy date
   - `input_data`: User-provided data (via DataFrame + mapper or direct pytree)
   - `tt_targets`: Which outputs to compute
   - `results`: Final outputs in user-requested format

1. **TT DAG**: The core computation layer. Contains policy functions that operate on
   data columns.

### Entry Point (GEP 7)

`gettsim.main()` is the single entry point. Users specify:

- `main_target` or `main_targets`: What to compute (use `MainTarget` for autocompletion)
- `policy_date_str`: Date for the policy environment (ISO format `YYYY-MM-DD`)
- `input_data`: User data (via `InputData` helper classes)
- `tt_targets`: Which tax/transfer outputs to compute (via `TTTargets`)

```python
from gettsim import InputData, MainTarget, TTTargets, main

outputs_df = main(
    main_target=MainTarget.results.df_with_mapper,
    policy_date_str="2025-01-01",
    input_data=InputData.df_and_mapper(df=inputs_df, mapper=inputs_map),
    tt_targets=TTTargets(tree=targets_tree),
)
```

### Policy Functions (GEP 4, 6)

Policy functions use decorators from `gettsim.tt`:

```python
@policy_function(start_date="2023-01-01", leaf_name="betrag_m")
def betrag_ohne_staffelung_m(anzahl_ansprüche: int, satz: float) -> float:
    return satz * anzahl_ansprüche
```

Key decorators:

- `@policy_function` - Main policy calculation functions with date ranges (`start_date`,
  `end_date`, `leaf_name`)
- `@policy_input` - Input column definitions (no implementation body)
- `@param_function` - Functions that transform raw parameters into usable forms
- `@agg_by_p_id_function` - Aggregation functions by person ID (e.g., summing children's
  claims to parent)
- `@agg_by_group_function` - Aggregation functions by group (e.g., sum to household
  level)
- `@group_creation_function` - Functions that create group IDs (e.g., fg_id, bg_id)

Additional `@policy_function` parameters:

- `vectorization_strategy="not_required"` - For functions that operate on full columns
  using `xnp`
- `rounding_spec=RoundingSpec(...)` - Optional rounding (GEP 5)
- `fail_msg_if_included="..."` - Error message if function is included in DAG (for
  unimplemented periods)

### Automatic DAG Features (GEP 4)

**Auto-aggregation**: If `my_col` exists and `my_col_hh` is requested, a sum aggregation
is auto-generated.

**Time conversion**: Automatic conversion between `_y`, `_q`, `_m`, `_w`, `_d` suffixes
using these factors relative to year: 1, 4, 12, 365.25/7, 365.25.

### Parameters (GEP 3)

Policy parameters are in YAML files alongside the Python code. Each parameter has:

- Date-keyed values (e.g., `2023-01-01:`)
- Metadata: `name` (de/en), `description` (de/en), `unit`, `reference_period`, `type`
- Legal references in each date entry
- Schema: `docs/geps/params-schema.json`

Parameter types:

- `scalar` - Single value (accessed via `value` key)
- `dict` - Homogeneous dictionary with string/int keys
- `piecewise_constant`, `piecewise_linear`, `piecewise_quadratic`, `piecewise_cubic` -
  For `piecewise_polynomial` function
- `birth_year_based_phase_inout`, `birth_month_based_phase_inout` - Age threshold
  lookups by birth cohort
- `require_converter` - Complex structures needing a `@param_function` converter

### Rounding (GEP 5)

```python
@policy_function(
    rounding_spec=RoundingSpec(
        base=0.0001,
        direction="nearest",  # or "up", "down"
        reference="§76g SGB VI Abs. 4 Nr. 4",
    ),
    start_date="2021-01-01",
)
def höchstbetrag_m(...) -> float: ...
```

## Naming Conventions (GEP 1, 6)

### Language

- **German** for policy-specific code (law names: Kindergeld, Bürgergeld,
  Einkommensteuer)
- **English** for infrastructure code
- **UTF-8** characters allowed (ä, ö, ü, ß)

### Namespaces and Qualified Names (GEP 6)

- Directory structure defines namespaces (e.g., `germany/kindergeld/` → namespace
  `kindergeld`)
- Within a namespace, use local names: `betrag_m`, `satz`
- Cross-namespace references use qualified names with double underscores:
  `arbeitslosengeld_2__einkommen_m_bg`
- `betrag` is the convention for monetary amounts of a tax/transfer

### Column/Function Name Suffixes (GEP 1)

**Time units** (appear before aggregation):

- `_y` (year), `_q` (quarter), `_m` (month), `_w` (week), `_d` (day)

**Aggregation levels**:

- `_sn` (Steuernummer - tax unit)
- `_hh` (Haushalt - household)
- `_fg` (Familiengemeinschaft)
- `_bg` (Bedarfsgemeinschaft)
- `_eg` (Einstandsgemeinschaft)
- `_ehe` (Ehegemeinschaft)

Example: `arbeitslosengeld_2__betrag_m_bg` = monthly ALG2 amount at Bedarfsgemeinschaft
level

### Special Column Types (GEP 2)

- `p_id` - Primary person identifier (required)
- `[x]_id` - Group identifiers (e.g., `hh_id`, `bg_id`) - same value for all group
  members
- `p_id_[y]` - Person-to-person pointers (e.g., `p_id_elternteil_1`, `p_id_empfänger`).
  Value -1 = no link.

## Test Cases

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

1. **If-else blocks**: Only one operation per branch, no return inside single if (must
   have else)
1. **Function calls**: `sum`, `any`, `all` require iterable arguments; `min`, `max` take
   exactly 2 args or 1 iterable
1. **No elif after else**: Use nested if-else instead

## Useful Imports from gettsim.tt

```python
from gettsim.tt import (
    # Decorators
    policy_function,
    policy_input,
    param_function,
    agg_by_group_function,
    agg_by_p_id_function,
    group_creation_function,
    # Types
    AggType,  # SUM, COUNT, MEAN, MAX, MIN, ANY, ALL
    RoundingSpec,
    ConsecutiveIntLookupTableParamValue,
    PiecewisePolynomialParamValue,
    # Functions
    piecewise_polynomial,
    join,  # For person-to-person lookups
    get_consecutive_int_lookup_table_param_value,
    get_piecewise_parameters,
    intervals_to_thresholds,
    merge_piecewise_intervals,
    PiecewisePolynomialInterval,
)
```

## Relevant GEPs

The [GETTSIM Enhancement Protocols](docs/geps/) define conventions:

- **GEP 0**: Purpose and process for GEPs
- **GEP 1**: Naming conventions (identifiers, German names, time/unit suffixes)
- **GEP 2**: Internal data representation (1-d arrays, group identifiers, person
  pointers)
- **GEP 3**: Parameters of the taxes and transfers system (YAML structure, types)
- **GEP 4**: DAG-based computational backend (core architecture)
- **GEP 5**: Optional rounding via `RoundingSpec`
- **GEP 6**: Unified architecture (namespaces, qualified names, `start_date`/`end_date`)
- **GEP 7**: User interface (`main()` function, `MainTarget`, input/output handling)
