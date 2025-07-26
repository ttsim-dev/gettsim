from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import (
    PiecewisePolynomialParamValue,
    RoundingSpec,
    piecewise_polynomial,
    policy_function,
)

if TYPE_CHECKING:
    from types import ModuleType


@policy_function(
    rounding_spec=RoundingSpec(
        base=0.01,
        direction="nearest",
        reference="§ 123 SGB VI Abs. 1",
    ),
    start_date="2021-01-01",
)
def betrag_m(basisbetrag_m: float, anzurechnendes_einkommen_m: float) -> float:
    """Additional monthly pensions payments (Grundrentenzuschlag)."""
    out = basisbetrag_m - anzurechnendes_einkommen_m
    return max(out, 0.0)


@policy_function(start_date="2021-01-01")
def einkommen_m(
    gesamteinnahmen_aus_renten_vorjahr_m: float,
    bruttolohn_vorjahr_m: float,
    einnahmen_aus_selbstständiger_arbeit_vorvorjahr_m: float,
    einnahmen_aus_vermietung_und_verpachtung_vorvorjahr_m: float,
    einnahmen_aus_kapitalvermögen_vorvorjahr_m: float,
) -> float:
    """Income relevant for Grundrentenzuschlag before deductions.

    Some notes:

    - The Grundrentenzuschlag (in previous years) is not part of the relevant income and
      does not lower the Grundrentenzuschlag (reference: § 97a Abs. 2 S. 7 SGB VI).
    - The Deutsche Rentenversicherung uses the income of the year two to three years ago
      to be able to use administrative data on this income for the calculation: "It can
      be assumed that the tax office regularly has the data two years after the end of
      the assessment period, which can be retrieved from the pension insurance."
    - Warning: Freibeträge for income are currently not considered as `freibeträge_y`
      depends on pension income through
      `sozialversicherung__kranken__beitrag__betrag_versicherter_m` ->
      `vorsorgeaufw` -> `freibeträge`

    Reference: § 97a Abs. 2 S. 1 SGB VI
    """
    # Sum income over different income sources.
    return (
        gesamteinnahmen_aus_renten_vorjahr_m
        + bruttolohn_vorjahr_m
        + einnahmen_aus_selbstständiger_arbeit_vorvorjahr_m
        + einnahmen_aus_vermietung_und_verpachtung_vorvorjahr_m
        + einnahmen_aus_kapitalvermögen_vorvorjahr_m
    )


def _anzurechnendes_einkommen_m(
    einkommen_m_ehe: float,
    rentenwert: float,
    parameter_anzurechnendes_einkommen: PiecewisePolynomialParamValue,
    xnp: ModuleType,
) -> float:
    """The isolated function for the relevant income for the Grundrentezuschlag."""
    return rentenwert * piecewise_polynomial(
        x=einkommen_m_ehe / rentenwert,
        parameters=parameter_anzurechnendes_einkommen,
        xnp=xnp,
    )


@policy_function(
    rounding_spec=RoundingSpec(
        base=0.01,
        direction="nearest",
        reference="§ 123 SGB VI Abs. 1",
    ),
    start_date="2021-01-01",
)
def anzurechnendes_einkommen_m(
    einkommen_m_ehe: float,
    familie__anzahl_personen_ehe: int,
    sozialversicherung__rente__rentenwert: float,
    anzurechnendes_einkommen_ohne_partner: PiecewisePolynomialParamValue,
    anzurechnendes_einkommen_mit_partner: PiecewisePolynomialParamValue,
    xnp: ModuleType,
) -> float:
    """Income which is deducted from Grundrentenzuschlag.

    Apply allowances. There are upper and lower thresholds for singles and
    couples. 60% of income between the upper and lower threshold is credited against
    the Grundrentenzuschlag. All the income above the upper threshold is credited
    against the Grundrentenzuschlag.

    Reference: § 97a Abs. 4 S. 2, 4 SGB VI
    """
    # Calculate relevant income following the crediting rules using the values for
    # singles and those for married subjects
    # Note: Thresholds are defined relativ to rentenwert which is implemented by
    # dividing the income by rentenwert and multiply rentenwert to the result.
    if familie__anzahl_personen_ehe == 1:
        out = _anzurechnendes_einkommen_m(
            einkommen_m_ehe=einkommen_m_ehe,
            rentenwert=sozialversicherung__rente__rentenwert,
            parameter_anzurechnendes_einkommen=anzurechnendes_einkommen_ohne_partner,
            xnp=xnp,
        )
    else:
        out = _anzurechnendes_einkommen_m(
            einkommen_m_ehe=einkommen_m_ehe,
            rentenwert=sozialversicherung__rente__rentenwert,
            parameter_anzurechnendes_einkommen=anzurechnendes_einkommen_mit_partner,
            xnp=xnp,
        )
    return out


@policy_function(
    rounding_spec=RoundingSpec(
        base=0.01,
        direction="nearest",
        reference="§ 123 SGB VI Abs. 1",
    ),
    start_date="2021-01-01",
)
def basisbetrag_m(
    mean_entgeltpunkte_zuschlag: float,
    bewertungszeiten_monate: int,
    sozialversicherung__rente__rentenwert: float,
    sozialversicherung__rente__altersrente__zugangsfaktor: float,
    maximaler_zugangsfaktor: float,
    berücksichtigte_wartezeit_monate: dict[str, int],
) -> float:
    """Grundrente without taking into account income crediting rules.

    The Zugangsfaktor is limited to 1 and considered Grundrentezeiten are limited to
    35 years (420 months).
    """
    bewertungszeiten = min(
        bewertungszeiten_monate,
        berücksichtigte_wartezeit_monate["max"],
    )
    zugangsfaktor = min(
        sozialversicherung__rente__altersrente__zugangsfaktor,
        maximaler_zugangsfaktor,
    )

    return (
        mean_entgeltpunkte_zuschlag
        * bewertungszeiten
        * sozialversicherung__rente__rentenwert
        * zugangsfaktor
    )


@policy_function(start_date="2021-01-01")
def mean_entgeltpunkte_pro_bewertungsmonat(
    mean_entgeltpunkte: float,
    bewertungszeiten_monate: int,
) -> float:
    """Average number of Entgeltpunkte earned per month of Grundrentenbewertungszeiten."""
    if bewertungszeiten_monate > 0:
        out = mean_entgeltpunkte / bewertungszeiten_monate

    # Return 0 if bewertungszeiten_monate is 0. Then, mean_entgeltpunkte should be 0, too.
    else:
        out = 0

    return out


@policy_function(
    rounding_spec=RoundingSpec(
        base=0.0001,
        direction="nearest",
        reference="§76g SGB VI Abs. 4 Nr. 4",
    ),
    start_date="2021-01-01",
)
def höchstbetrag_m(
    grundrentenzeiten_monate: int,
    berücksichtigte_wartezeit_monate: dict[str, int],
    höchstwert_der_entgeltpunkte: dict[str, float],
) -> float:
    """Maximum allowed number of average Entgeltpunkte."""
    months_above_thresh = (
        min(
            grundrentenzeiten_monate,
            berücksichtigte_wartezeit_monate["max"],
        )
        - berücksichtigte_wartezeit_monate["min"]
    )

    return (
        höchstwert_der_entgeltpunkte["base"]
        + höchstwert_der_entgeltpunkte["increment"] * months_above_thresh
    )


@policy_function(
    rounding_spec=RoundingSpec(
        base=0.0001,
        direction="nearest",
        reference="§ 123 SGB VI Abs. 1",
    ),
    start_date="2021-01-01",
)
def mean_entgeltpunkte_zuschlag(
    mean_entgeltpunkte_pro_bewertungsmonat: float,
    höchstbetrag_m: float,
    grundrentenzeiten_monate: int,
    berücksichtigte_wartezeit_monate: dict[str, int],
    bonusfaktor: float,
) -> float:
    """Additional Entgeltpunkte.

    In general, the average of monthly Entgeltpunkte earnd in Grundrentenzeiten is
    doubled, or extended to the individual Höchstwert if doubling would exceed the
    Höchstwert. Then, the value is multiplied by 0.875.

    Legal reference: § 76g SGB VI
    """
    out = 0.0
    # Return 0 if Grundrentenzeiten below minimum
    if grundrentenzeiten_monate < berücksichtigte_wartezeit_monate["min"]:
        out = 0.0
    else:
        # Case 1: Entgeltpunkte less than half of Höchstwert
        if mean_entgeltpunkte_pro_bewertungsmonat <= (0.5 * höchstbetrag_m):
            out = mean_entgeltpunkte_pro_bewertungsmonat

        # Case 2: Entgeltpunkte more than half of Höchstwert, but below Höchstwert
        elif mean_entgeltpunkte_pro_bewertungsmonat < höchstbetrag_m:
            out = höchstbetrag_m - mean_entgeltpunkte_pro_bewertungsmonat

        # Case 3: Entgeltpunkte above Höchstwert
        elif mean_entgeltpunkte_pro_bewertungsmonat > höchstbetrag_m:
            out = 0.0

    # Multiply additional Engeltpunkte by factor
    return out * bonusfaktor


@policy_function(start_date="2021-01-01")
def grundsätzlich_anspruchsberechtigt(
    grundrentenzeiten_monate: int,
    berücksichtigte_wartezeit_monate: dict[str, int],
) -> bool:
    """Has accumulated enough insured years to be eligible."""
    return grundrentenzeiten_monate >= berücksichtigte_wartezeit_monate["min"]


@policy_function(start_date="2021-01-01")
def gesamteinnahmen_aus_renten_für_einkommensberechnung_im_folgejahr_m(
    einnahmen__renten__gesetzliche_m: float,
    einnahmen__renten__geförderte_private_vorsorge_m: float,
    einnahmen__renten__sonstige_private_vorsorge_m: float,
    einnahmen__renten__betriebliche_altersvorsorge_m: float,
) -> float:
    """Income from private and public pensions in the previous calendar year.

    This target can be used as an input in another GETTSIM call to compute Grundrente.
    """
    return (
        einnahmen__renten__gesetzliche_m
        + einnahmen__renten__geförderte_private_vorsorge_m
        + einnahmen__renten__sonstige_private_vorsorge_m
        + einnahmen__renten__betriebliche_altersvorsorge_m
    )
