from __future__ import annotations

from gettsim.tt import RoundingSpec, policy_function


@policy_function(
    end_date="2017-06-30",
    rounding_spec=RoundingSpec(
        base=0.01,
        direction="nearest",
        reference="§ 123 SGB VI Abs. 1",
    ),
    leaf_name="bruttorente_m",
)
def bruttorente_m_mit_harter_hinzuverdienstgrenze(
    alter: int,
    regelaltersrente__altersgrenze: float,
    einnahmen__bruttolohn_m: float,
    bruttorente_basisbetrag_m: float,
    hinzuverdienstgrenze_m: float,
) -> float:
    """Pension benefits after earnings test for early retirees.

    If earnings are above an earnings limit, the pension is fully deducted.
    """
    # TODO (@MImmesberger): Use age with monthly precision.
    # https://github.com/ttsim-dev/gettsim/issues/781
    if (alter >= regelaltersrente__altersgrenze) or (
        einnahmen__bruttolohn_m <= hinzuverdienstgrenze_m
    ):
        out = bruttorente_basisbetrag_m
    else:
        out = 0.0

    return out


@policy_function(
    start_date="2017-07-01",
    end_date="2022-12-31",
    leaf_name="bruttorente_m",
    rounding_spec=RoundingSpec(
        base=0.01,
        direction="nearest",
        reference="§ 123 SGB VI Abs. 1",
    ),
)
def bruttorente_m_mit_hinzuverdienstdeckel(
    alter: int,
    regelaltersrente__altersgrenze: float,
    einnahmen__bruttolohn_y: float,
    differenz_bruttolohn_hinzuverdienstdeckel_m: float,
    zahlbetrag_ohne_deckel_m: float,
) -> float:
    """Pension benefits after earnings test for early retirees.

    If sum of earnings and pension is larger than the highest income in the last 15
    years, the pension is fully deducted (Hinzuverdienstdeckel).
    """
    # TODO (@MImmesberger): Use age with monthly precision.
    # https://github.com/ttsim-dev/gettsim/issues/781
    if (
        differenz_bruttolohn_hinzuverdienstdeckel_m > 0
        and alter <= regelaltersrente__altersgrenze
        and einnahmen__bruttolohn_y > 0
    ):
        out = max(
            zahlbetrag_ohne_deckel_m - differenz_bruttolohn_hinzuverdienstdeckel_m,
            0.0,
        )
    else:
        out = zahlbetrag_ohne_deckel_m

    return out


@policy_function(
    start_date="2017-07-01",
    end_date="2022-12-31",
)
def zahlbetrag_ohne_deckel_m(
    einnahmen__bruttolohn_m: float,
    alter: int,
    regelaltersrente__altersgrenze: float,
    bruttorente_basisbetrag_m: float,
    differenz_bruttolohn_hinzuverdienstgrenze_m: float,
    hinzuverdienstgrenze_m: float,
    abzugsrate_hinzuverdienst: float,
) -> float:
    """Pension benefits after earnings test without accounting for the earnings cap
    (Hinzuverdienstdeckel).
    """
    # TODO (@MImmesberger): Use age with monthly precision.
    # https://github.com/ttsim-dev/gettsim/issues/781
    # No deduction because of age or low earnings
    if (alter >= regelaltersrente__altersgrenze) or (
        einnahmen__bruttolohn_m <= hinzuverdienstgrenze_m
    ):
        out = bruttorente_basisbetrag_m
    else:
        out = max(
            bruttorente_basisbetrag_m
            - abzugsrate_hinzuverdienst * differenz_bruttolohn_hinzuverdienstgrenze_m,
            0.0,
        )

    return out


@policy_function(
    start_date="2017-07-01",
    end_date="2022-12-31",
)
def differenz_bruttolohn_hinzuverdienstgrenze_m(
    einnahmen__bruttolohn_m: float,
    hinzuverdienstgrenze_m: float,
) -> float:
    """Earnings that are subject to pension deductions."""
    return max(
        einnahmen__bruttolohn_m - hinzuverdienstgrenze_m,
        0.0,
    )


@policy_function(
    start_date="2017-07-01",
    end_date="2022-12-31",
)
def differenz_bruttolohn_hinzuverdienstdeckel_m(
    einnahmen__bruttolohn_m: float,
    zahlbetrag_ohne_deckel_m: float,
    höchster_bruttolohn_letzte_15_jahre_vor_rente_m: float,
) -> float:
    """Income above the earnings cap (Hinzuverdienstdeckel)."""
    return max(
        zahlbetrag_ohne_deckel_m
        + einnahmen__bruttolohn_m
        - höchster_bruttolohn_letzte_15_jahre_vor_rente_m,
        0.0,
    )


@policy_function(
    start_date="2023-01-01",
    leaf_name="bruttorente_m",
    rounding_spec=RoundingSpec(
        base=0.01,
        direction="nearest",
        reference="§ 123 SGB VI Abs. 1",
    ),
)
def bruttorente_m_ohne_einkommensanrechnung(
    bruttorente_basisbetrag_m: float,
) -> float:
    """Public pension claim before Grundrentenzuschlag."""
    return bruttorente_basisbetrag_m
