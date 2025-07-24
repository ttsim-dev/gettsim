"""Public pension benefits for retirement due to age."""

from __future__ import annotations

from gettsim.tt import RoundingSpec, policy_function


@policy_function(
    end_date="2020-12-31",
    rounding_spec=RoundingSpec(
        base=0.01,
        direction="nearest",
        reference="§ 123 SGB VI Abs. 1",
    ),
    leaf_name="betrag_m",
)
def betrag_m(
    bruttorente_m: float,
    sozialversicherung__rente__bezieht_rente: bool,
) -> float:
    return bruttorente_m if sozialversicherung__rente__bezieht_rente else 0.0


@policy_function(
    start_date="2021-01-01",
    rounding_spec=RoundingSpec(
        base=0.01,
        direction="nearest",
        reference="§ 123 SGB VI Abs. 1",
    ),
    leaf_name="betrag_m",
)
def betrag_m_mit_grundrente(
    bruttorente_m: float,
    sozialversicherung__rente__grundrente__betrag_m: float,
    sozialversicherung__rente__bezieht_rente: bool,
) -> float:
    """Calculate total individual public pension including Grundrentenzuschlag."""
    return (
        bruttorente_m + sozialversicherung__rente__grundrente__betrag_m
        if sozialversicherung__rente__bezieht_rente
        else 0.0
    )


@policy_function(
    start_date="1992-01-01",
    end_date="2023-06-30",
    leaf_name="bruttorente_basisbetrag_m",
)
def bruttorente_basisbetrag_m_nach_wohnort(
    zugangsfaktor: float,
    sozialversicherung__rente__entgeltpunkte_ost: float,
    sozialversicherung__rente__entgeltpunkte_west: float,
    sozialversicherung__rente__bezieht_rente: bool,
    sozialversicherung__rente__parameter_rentenwert_nach_wohnort: dict[str, float],
) -> float:
    """Old-Age Pensions claim. The function follows the following equation:

    .. math::

        Rente = Entgeltpunkte * Zugangsfaktor * Rentenwert

    See:
    - https://de.wikipedia.org/wiki/Rentenformel
    - https://de.wikipedia.org/wiki/Rentenanpassungsformel
    """
    if sozialversicherung__rente__bezieht_rente:
        out = (
            sozialversicherung__rente__entgeltpunkte_west
            * sozialversicherung__rente__parameter_rentenwert_nach_wohnort["west"]
            + sozialversicherung__rente__entgeltpunkte_ost
            * sozialversicherung__rente__parameter_rentenwert_nach_wohnort["ost"]
        ) * zugangsfaktor
    else:
        out = 0.0

    return out


@policy_function(start_date="2023-07-01")
def bruttorente_basisbetrag_m(
    zugangsfaktor: float,
    sozialversicherung__rente__entgeltpunkte: float,
    sozialversicherung__rente__bezieht_rente: bool,
    sozialversicherung__rente__rentenwert: float,
) -> float:
    """Old-Age Pensions claim. The function follows the following equation:

    .. math::

        Rente = Entgeltpunkte * Zugangsfaktor * Rentenwert

    See:
    - https://de.wikipedia.org/wiki/Rentenformel
    - https://de.wikipedia.org/wiki/Rentenanpassungsformel
    """
    if sozialversicherung__rente__bezieht_rente:
        out = (
            sozialversicherung__rente__entgeltpunkte
            * sozialversicherung__rente__rentenwert
            * zugangsfaktor
        )
    else:
        out = 0.0

    return out


@policy_function()
def zugangsfaktor(
    sozialversicherung__rente__alter_bei_renteneintritt: float,
    regelaltersrente__altersgrenze: float,
    referenzalter_abschlag: float,
    altersgrenze: float,
    altersgrenze_vorzeitig: float,
    vorzeitig_grundsätzlich_anspruchsberechtigt: bool,
    regelaltersrente__grundsätzlich_anspruchsberechtigt: bool,
    sozialversicherung__rente__zugangsfaktor_veränderung_pro_jahr: dict[str, float],
) -> float:
    """Zugangsfaktor (pension adjustment factor).

    Factor by which the pension claim is multiplied to calculate the pension payment.
    The Zugangsfaktor is larger than 1 if the agent retires after the normal retirement
    age (NRA) and smaller than 1 if the agent retires earlier than the full retirement
    age (FRA).

    At the regelaltersgrenze - normal retirement age (NRA), the agent is allowed to get
    pensions with his full claim. In general, if the agent retires earlier or later, the
    Zugangsfaktor and therefore the pension claim is higher or lower. The Zugangsfaktor
    is 1.0 in [FRA, NRA].

    Legal reference: § 77 Abs. 2 Nr. 2 SGB VI

    Since pension payments of the GRV always start at 1st day of month, day of birth
    within month does not matter. The eligibility always starts in the month after
    reaching the required age.

    Returns 0 if the person is not eligible for receiving pension benefits because
    either i) the person is younger than the earliest possible retirement age or ii) the
    person is not eligible for pension benefits because
    `regelaltersrente__grundsätzlich_anspruchsberechtigt`
    is False.
    """
    if regelaltersrente__grundsätzlich_anspruchsberechtigt:
        # Early retirement (before full retirement age): Zugangsfaktor < 1
        if (
            sozialversicherung__rente__alter_bei_renteneintritt < altersgrenze
        ):  # [ERA,FRA)
            if vorzeitig_grundsätzlich_anspruchsberechtigt and (
                sozialversicherung__rente__alter_bei_renteneintritt
                >= altersgrenze_vorzeitig
            ):
                # Calc difference to FRA of pensions with early retirement options
                # (Altersgrenze langjährig Versicherte, Altersrente für Frauen
                # /Arbeitslose).
                # checks whether older than possible era
                out = (
                    1
                    + (
                        sozialversicherung__rente__alter_bei_renteneintritt
                        - referenzalter_abschlag
                    )
                    * sozialversicherung__rente__zugangsfaktor_veränderung_pro_jahr[
                        "vorzeitiger_renteneintritt"
                    ]
                )
            else:
                # Early retirement although not eligible to do so.
                out = 0.0

        # Late retirement (after normal retirement age/Regelaltersgrenze):
        # Zugangsfaktor > 1
        elif (
            sozialversicherung__rente__alter_bei_renteneintritt
            > regelaltersrente__altersgrenze
        ):
            out = (
                1
                + (
                    sozialversicherung__rente__alter_bei_renteneintritt
                    - regelaltersrente__altersgrenze
                )
                * sozialversicherung__rente__zugangsfaktor_veränderung_pro_jahr[
                    "späterer_renteneintritt"
                ]
            )

        # Retirement between full retirement age and normal retirement age:
        else:  # [FRA,NRA]
            out = 1.0

    # Claiming pension is not possible if
    # regelaltersrente__grundsätzlich_anspruchsberechtigt is
    # 'False'. Return 0 in this case. Then, the pension payment is 0 as well.
    else:
        out = 0.0

    return max(out, 0.0)
