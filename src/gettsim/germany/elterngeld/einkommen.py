"""Relevant income for parental leave benefits."""

from __future__ import annotations

from gettsim.tt import RoundingSpec, policy_function


@policy_function(start_date="2007-01-01")
def anzurechnendes_nettoeinkommen_m(
    einnahmen__bruttolohn_m: float,
    lohnsteuer__betrag_m: float,
    lohnsteuer__betrag_soli_m: float,
) -> float:
    """Income that reduces the Elterngeld claim."""
    # TODO(@MImmesberger): In this case, lohnsteuer__betrag_m should be calculated
    # without taking into account adaptions to the standard care insurance rate.
    # https://github.com/ttsim-dev/gettsim/issues/792
    return einnahmen__bruttolohn_m - lohnsteuer__betrag_m - lohnsteuer__betrag_soli_m


@policy_function(
    start_date="2007-01-01",
    rounding_spec=RoundingSpec(base=2, direction="down", reference="§ 2 (2) BEEG"),
)
def lohnersatzanteil_einkommen_untere_grenze(
    mean_nettoeinkommen_in_12_monaten_vor_geburt_m: float,
    nettoeinkommensstufen_für_lohnersatzrate: dict[str, float],
) -> float:
    """Lower threshold for replacement rate adjustment minus net income."""
    return (
        nettoeinkommensstufen_für_lohnersatzrate["lower_threshold"]
        - mean_nettoeinkommen_in_12_monaten_vor_geburt_m
    )


@policy_function(
    start_date="2007-01-01",
    rounding_spec=RoundingSpec(base=2, direction="down", reference="§ 2 (2) BEEG"),
)
def lohnersatzanteil_einkommen_obere_grenze(
    mean_nettoeinkommen_in_12_monaten_vor_geburt_m: float,
    nettoeinkommensstufen_für_lohnersatzrate: dict[str, float],
) -> float:
    """Net income minus upper threshold for replacement rate adjustment."""
    return (
        mean_nettoeinkommen_in_12_monaten_vor_geburt_m
        - nettoeinkommensstufen_für_lohnersatzrate["upper_threshold"]
    )


@policy_function(
    start_date="2011-01-01",
    end_date="2024-03-31",
    leaf_name="einkommen_vorjahr_unter_bezugsgrenze",
)
def einkommen_vorjahr_unter_bezugsgrenze_mit_unterscheidung_single_paar(
    familie__alleinerziehend: bool,
    zu_versteuerndes_einkommen_vorjahr_y_sn: float,
    max_zu_versteuerndes_einkommen_vorjahr_nach_alleinerziehendenstatus: dict[
        str,
        float,
    ],
) -> bool:
    """Income before birth is below income threshold for Elterngeld."""
    if familie__alleinerziehend:
        out = (
            zu_versteuerndes_einkommen_vorjahr_y_sn
            <= max_zu_versteuerndes_einkommen_vorjahr_nach_alleinerziehendenstatus[
                "alleinerziehend"
            ]
        )
    else:
        out = (
            zu_versteuerndes_einkommen_vorjahr_y_sn
            <= max_zu_versteuerndes_einkommen_vorjahr_nach_alleinerziehendenstatus[
                "paar"
            ]
        )
    return out


@policy_function(
    start_date="2024-04-01",
    leaf_name="einkommen_vorjahr_unter_bezugsgrenze",
)
def einkommen_vorjahr_unter_bezugsgrenze_ohne_unterscheidung_single_paar(
    zu_versteuerndes_einkommen_vorjahr_y_sn: float,
    max_zu_versteuerndes_einkommen_vorjahr_pauschal: float,
) -> bool:
    """Income before birth is below income threshold for Elterngeld."""
    return (
        zu_versteuerndes_einkommen_vorjahr_y_sn
        <= max_zu_versteuerndes_einkommen_vorjahr_pauschal
    )


@policy_function(
    start_date="2012-09-18",
    rounding_spec=RoundingSpec(base=0.01, direction="down"),
)
def mean_nettoeinkommen_für_bemessungsgrundlage_nach_geburt_m(
    einnahmen__bruttolohn_m: float,
    lohnsteuer__betrag_m: float,
    lohnsteuer__betrag_soli_m: float,
    sozialversicherungspauschale: float,
) -> float:
    """Approximation of net wage used to calculate Elterngeld.

    This target can be used as an input in another GETTSIM call to compute Elterngeld.
    In principle, the relevant gross wage for this target is the sum of the gross wages
    in the 12 months before the birth of the child. For most datasets, except those with
    monthly income date (IAB, DRV data), the best approximation will likely be the gross
    wage in the calendar year before the birth of the child.
    """
    prox_ssc = sozialversicherungspauschale * einnahmen__bruttolohn_m
    return (
        einnahmen__bruttolohn_m
        - prox_ssc
        - lohnsteuer__betrag_m
        - lohnsteuer__betrag_soli_m
    )
