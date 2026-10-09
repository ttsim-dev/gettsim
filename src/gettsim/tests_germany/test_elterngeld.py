from __future__ import annotations

import pytest

from gettsim import MainTarget, main
from gettsim.germany.elterngeld.elterngeld import (
    anspruchshöhe_m,
    basisbetrag_m,
    betrag_m,
    lohnersatzanteil,
)


@pytest.fixture(scope="module")
def elterngeld_params():
    return main(
        main_target=MainTarget.policy_environment,
        policy_date_str="2018-01-01",
        backend="numpy",
    )["elterngeld"]


@pytest.mark.parametrize(
    ("income", "expected_rate", "expected_benefit"),
    [
        (250.0, 1.0, 300.0),
        (300.0, 1.0, 300.0),
        (320.0, 1.0, 320.0),
        (330.0, 1.0, 330.0),
        (340.0, 1.0, 340.0),
        (790.0, 0.775, 612.25),
        (1000.0, 0.67, 670.0),
    ],
)
def test_elterngeld_low_income_replacement_rate_cap(
    elterngeld_params, income, expected_rate, expected_benefit
):
    thresholds = elterngeld_params["nettoeinkommensstufen_für_lohnersatzrate"].value
    rate = lohnersatzanteil(
        mean_nettoeinkommen_in_12_monaten_vor_geburt_m=income,
        lohnersatzanteil_einkommen_untere_grenze_m=(
            thresholds["lower_threshold"] - income
        ),
        lohnersatzanteil_einkommen_obere_grenze_m=(
            income - thresholds["upper_threshold"]
        ),
        einkommensschritte_korrektur_m=(
            elterngeld_params["einkommensschritte_korrektur_m"].value
        ),
        satz=elterngeld_params["satz"].value,
        prozent_korrektur=elterngeld_params["prozent_korrektur"].value,
        prozent_minimum=elterngeld_params["prozent_minimum"].value,
        nettoeinkommensstufen_für_lohnersatzrate=thresholds,
    )
    assert rate == pytest.approx(expected_rate, abs=1e-5)

    base = basisbetrag_m(
        mean_nettoeinkommen_in_12_monaten_vor_geburt_m=income,
        lohnersatzanteil=rate,
        anzurechnendes_nettoeinkommen_m=0.0,
        max_zu_berücksichtigendes_einkommen_m=(
            elterngeld_params["max_zu_berücksichtigendes_einkommen_m"].value
        ),
    )
    entitlement = anspruchshöhe_m(
        basisbetrag_m=base,
        geschwisterbonus_m_fg=0.0,
        mehrlingsbonus_m_fg=0.0,
        mindestbetrag_m=elterngeld_params["mindestbetrag_m"].value,
        höchstbetrag_m=elterngeld_params["höchstbetrag_m"].value,
    )
    benefit = betrag_m(
        grundsätzlich_anspruchsberechtigt=True,
        anspruchshöhe_m=entitlement,
    )
    assert benefit == pytest.approx(expected_benefit, abs=1e-2)
