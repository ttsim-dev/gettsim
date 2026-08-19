from __future__ import annotations

import datetime
import os
from datetime import timedelta
from typing import TYPE_CHECKING, Literal, cast

import dags.tree as dt
import numpy
import pytest
from dags.tree.validation import fail_if_top_level_elements_repeated_in_paths
from ttsim.interface_dag_elements.backend import xnp as get_xnp
from ttsim.testing_utils import (
    PolicyTest,
    check_env_completeness,
    check_policy_environment_unit_history,
    execute_test,
    get_policy_date_partition,
    load_policy_cases,
)

from gettsim import InputData, MainTarget, TTTargets, germany, main

if TYPE_CHECKING:
    from ttsim.typing import FlatColumnObjectsParamFunctions, FlatOrigParamSpecs
    from ttsim.unit_validation import UnitValidationReport

    OrigPolicyObjects = dict[str, FlatColumnObjectsParamFunctions | FlatOrigParamSpecs]

ON_CI_WITHOUT_COVERAGE = (
    os.environ.get("GITHUB_ACTIONS") == "true"
    and os.environ.get("COV_CORE_SOURCE") is None
)

POLICY_TEST_IDS_AND_CASES = load_policy_cases(
    policy_cases_root=germany.ROOT_PATH.parent / "tests_germany" / "policy_cases",
    policy_name="",
    xnp=numpy,
)

EXPECTED_UNIT_CHECK_LOCAL_CASTS = (
    "alter_bis_24",
    "arbeitslosengeld_2__anspruchshöhe_m",
    "arbeitslosengeld_2__berechtigte_wohnfläche",
    "arbeitslosengeld_2__differenz_kindergeld_kindbedarf_m",
    "arbeitslosengeld_2__erwachsenensatz_m",
    "arbeitslosengeld_2__mehrbedarfsanteil_alleinerziehend",
    "bürgergeld__anspruchshöhe_m",
    "bürgergeld__berechtigte_wohnfläche",
    "bürgergeld__differenz_kindergeld_kindbedarf_m",
    "bürgergeld__erwachsenensatz_m",
    "bürgergeld__mehrbedarfsanteil_alleinerziehend",
    "bürgergeld__vermögensfreibetrag_in_karenzzeit_bg",
    "einkommensteuer__abzüge__alleinerziehend_betrag_y",
    "einkommensteuer__abzüge__vorwegabzug_lohnsteuer_y_sn",
    "elterngeld__anrechenbarer_betrag_m",
    "elterngeld__anspruchshöhe_m",
    "elterngeld__anzahl_mehrlinge_fg",
    "elterngeld__bezugsmonate_unter_grenze_fg",
    "elterngeld__geschwisterbonus_m_fg",
    "elterngeld__ist_leistungsbegründendes_kind",
    "elterngeld__jüngstes_kind_oder_mehrling",
    "erziehungsgeld__anspruchshöhe_kind_m",
    "erziehungsgeld__einkommensgrenze_y_fg",
    "familie__hat_kind_in_gleicher_bedarfsgemeinschaft",
    "familie__ist_kind_bis_15_in_familiengemeinschaft",
    "familie__ist_kind_bis_17_in_bedarfsgemeinschaft",
    "familie__ist_kind_bis_17_in_familiengemeinschaft",
    "familie__ist_kind_bis_2_in_familiengemeinschaft",
    "familie__ist_kind_bis_5_in_familiengemeinschaft",
    "familie__ist_kind_bis_6_in_familiengemeinschaft",
    "familie__volljährig",
    "grundsicherung__im_alter__anspruchshöhe_m",
    "grundsicherung__im_alter__hat_gesamteinkommen_über_kindeseinkommensgrenze",
    "grundsicherung__im_alter__mehrbedarf_schwerbehinderung_g_m",
    "kindergeld__kind_bis_10_mit_kindergeld",
    "kinderzuschlag__anspruchshöhe_m_bg",
    "kinderzuschlag__basisbetrag_m_bg",
    "kinderzuschlag__wohnbedarf_anteil_eltern_bg",
    "sozialversicherung__rente__alter_bei_renteneintritt",
    "sozialversicherung__rente__altersrente__älter_als_regelaltersgrenze",
    "sozialversicherung__rente__grundrente__höchstbetrag_m",
    "sozialversicherung__rente__grundrente__mean_entgeltpunkte_zuschlag_m",
    "sozialversicherung__rente__neue_entgeltpunkte_y",
    "vorrangprüfungen__wohngeld_kinderzuschlag_vorrangig_oder_günstiger",
    "wohngeld__basisbetrag_m_wthh",
    "wohngeld__maximale_haushaltsgröße_mindesteinkommen_wthh",
    "wohngeld__miete_m_wthh",
    "wohngeld__vermögensgrenze_unterschritten_wthh",
)


EXPECTED_UNIT_CHECK_BODY_OPT_OUTS = (
    "arbeitslosengeld_2__berechtigte_wohnfläche_eigentum",
    "bürgergeld__berechtigte_wohnfläche_eigentum",
    "einkommensteuer__abzüge__altersentlastungsquote_gestaffelt_nach_geburtsjahr",
    "einkommensteuer__abzüge__maximaler_altersentlastungsbetrag_y_gestaffelt_nach_geburtsjahr",
    "einkommensteuer__abzüge__vorsorgeaufwendungen_regime_bis_2004_y_sn",
    "einkommensteuer__parameter_einkommensteuertarif",
    "kindergeld__satz_nach_anzahl_kinder",
    "lohnsteuer__parameter_max_lohnsteuer_klasse_5_6",
    "lohnsteuer__tarif_klassen_5_und_6_mit_kinderfreibetrag_y",
    "lohnsteuer__tarif_klassen_5_und_6_y",
    "solidaritätszuschlag__betrag_y_sn",
    "sozialversicherung__rente__altersrente__für_frauen__altersgrenze",
    "sozialversicherung__rente__altersrente__für_frauen__altersgrenze_vorzeitig",
    "sozialversicherung__rente__altersrente__langjährig__altersgrenze",
    "sozialversicherung__rente__altersrente__wegen_arbeitslosigkeit__altersgrenze",
    "sozialversicherung__rente__altersrente__wegen_arbeitslosigkeit__altersgrenze_mit_vertrauensschutz",
    "sozialversicherung__rente__altersrente__wegen_arbeitslosigkeit__altersgrenze_ohne_vertrauensschutz",
    "sozialversicherung__rente__altersrente__wegen_arbeitslosigkeit__altersgrenze_vorzeitig",
    "sozialversicherung__rente__altersrente__wegen_arbeitslosigkeit__altersgrenze_vorzeitig_ohne_vertrauensschutz",
    "sozialversicherung__rente__erwerbsminderung__zugangsfaktor",
    "sozialversicherung__rente__erwerbsminderung__zusätzliche_entgeltpunkte_durch_zurechnungszeit",
    "sozialversicherung__rente__grundrente__anzurechnendes_einkommen_m",
    "wohngeld__dauerhafte_heizkostenkomponente_m_lookup",
    "wohngeld__heizkostenentlastung_m_lookup",
    "wohngeld__klimakomponente_m_lookup",
    "wohngeld__max_miete_m_lookup",
    "wohngeld__miete_m_hh",
    "wohngeld__min_miete_lookup",
    "wohngeld__mindesteinkommen_nach_haushaltsgröße_m_wthh_lookup_table",
)


def get_orig_gettsim_objects() -> OrigPolicyObjects:
    return main(
        main_targets=[
            MainTarget.orig_policy_objects.column_objects_and_param_functions,
            MainTarget.orig_policy_objects.param_specs,
        ],
    )["orig_policy_objects"]


def dates_in_orig_gettsim_objects() -> list[datetime.date]:
    orig_objects = get_orig_gettsim_objects()
    column_objects = cast(
        "FlatColumnObjectsParamFunctions",
        orig_objects["column_objects_and_param_functions"],
    )
    start_dates = {v.start_date for v in column_objects.values()}
    end_dates = {v.end_date + timedelta(days=1) for v in column_objects.values()}
    # Skip first date (1900-01-01), which is just used to initialize many functions.
    return sorted(start_dates | end_dates)[1:]


def unit_check_dates_in_orig_gettsim_objects() -> list[datetime.date]:
    """Every function, parameter, rounding, and currency regime (GEP 10)."""
    return get_policy_date_partition(
        orig_policy_objects=get_orig_gettsim_objects(),
        unit_system=germany.UNIT_SYSTEM,
    )


@pytest.fixture
def orig_gettsim_objects() -> OrigPolicyObjects:
    return get_orig_gettsim_objects()


@pytest.fixture(scope="module")
def gettsim_unit_validation_report() -> UnitValidationReport:
    """Compute the exhaustive report once for all unit-history assertions."""
    return check_policy_environment_unit_history(
        orig_policy_objects=get_orig_gettsim_objects(),
        unit_system=germany.UNIT_SYSTEM,
    )


@pytest.mark.parametrize(
    "test",
    POLICY_TEST_IDS_AND_CASES.values(),
    ids=POLICY_TEST_IDS_AND_CASES.keys(),
)
def test_policy_cases(test: PolicyTest, backend: Literal["numpy", "jax"]):
    execute_test(
        test=test,
        root=germany.ROOT_PATH,
        backend=backend,
        unit_system=germany.UNIT_SYSTEM,
    )


@pytest.mark.skipif(
    ON_CI_WITHOUT_COVERAGE,
    reason="Test unaffected by Python version / OS. Only run once on CI.",
)
@pytest.mark.parametrize(
    "date",
    dates_in_orig_gettsim_objects(),
    ids=lambda x: x.isoformat(),
)
def test_gettsim_policy_environment_is_complete(orig_gettsim_objects, date):
    """Test that GETTSIM's policy environment contains all root nodes of its DAG."""
    if date.year < 2015:  # noqa: PLR2004
        pytest.skip(
            "Policy environment for dates before 2015 are not complete. See issue #962."
        )

    check_env_completeness(
        name="GETTSIM",
        policy_date=date,
        orig_policy_objects=orig_gettsim_objects,
        unit_system=germany.UNIT_SYSTEM,
    )


def test_gettsim_units_are_complete_and_consistent(gettsim_unit_validation_report):
    """Validate declarations and body coverage in every GEP 10 date regime."""
    assert gettsim_unit_validation_report.policy_date_regimes == tuple(
        unit_check_dates_in_orig_gettsim_objects()
    )


@pytest.mark.parametrize(
    ("attribute", "expected"),
    [
        ("local_casts", EXPECTED_UNIT_CHECK_LOCAL_CASTS),
        ("body_opt_outs", EXPECTED_UNIT_CHECK_BODY_OPT_OUTS),
        ("unsupported_bodies", ()),
    ],
)
def test_unit_check_exceptions_match_reviewed_baseline(
    gettsim_unit_validation_report,
    attribute,
    expected,
):
    """Require an explicit review for every change to casts and opt-outs."""
    assert getattr(gettsim_unit_validation_report, attribute) == expected


def _create_fake_input_data_from_template(template_tree: dict, xnp, n: int = 3) -> dict:
    """Create fake input data from a template tree of dtype strings."""
    flat_template = dt.flatten_to_qnames(template_tree)

    dtype_map = {
        "IntColumn": xnp.int32,
        "FloatColumn": xnp.float32,
        "BoolColumn": bool,
    }

    fake_flat = {}
    for qname, dtype_str in flat_template.items():
        dtype = dtype_map.get(dtype_str, xnp.float32)
        if dtype is bool:
            fake_flat[qname] = xnp.zeros(n, dtype=bool)
        else:
            fake_flat[qname] = xnp.zeros(n, dtype=dtype)

    # Add p_id (always required)
    fake_flat["p_id"] = xnp.arange(n, dtype=xnp.int32)

    return dt.unflatten_from_qnames(fake_flat)


@pytest.mark.skipif(
    ON_CI_WITHOUT_COVERAGE,
    reason="Test unaffected by Python version / OS. Only run once on CI.",
)
@pytest.mark.parametrize(
    "date",
    dates_in_orig_gettsim_objects(),
    ids=lambda x: x.isoformat(),
)
def test_top_level_elements_not_repeated_in_paths(
    date, backend: Literal["numpy", "jax"]
):
    xnp = get_xnp(backend)

    # Step 1: Get template for input data (without providing input_data)
    template = main(
        main_target=MainTarget.templates.input_data_dtypes.tree,
        policy_date=date,
        rounding=False,
    )

    # Step 2: Get tt_targets (without providing input_data)
    tt_targets_qname = main(
        main_target=MainTarget.tt_targets.qname,
        policy_date=date,
        rounding=False,
    )

    # Step 3: Create fake input data from template
    fake_input = _create_fake_input_data_from_template(template_tree=template, xnp=xnp)

    # Step 4: Call main with fake input data
    gettsim_objects = main(
        main_targets=[
            "specialized_environment__with_partialled_params_and_scalars",
            "labels__top_level_namespace",
        ],
        backend=backend,
        policy_date=date,
        input_data=InputData.tree(fake_input),
        tt_targets=TTTargets.qname(tt_targets_qname),
        rounding=False,
    )

    fail_if_top_level_elements_repeated_in_paths(
        all_tree_paths=set(
            dt.flatten_to_tree_paths(
                dt.unflatten_from_qnames(
                    gettsim_objects["specialized_environment"][
                        "with_partialled_params_and_scalars"
                    ]
                )
            )
        ),
        top_level_namespace=gettsim_objects["labels"]["top_level_namespace"],
    )
