"""Public pension benefits for retirement due to reduced earnings potential."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import policy_function

if TYPE_CHECKING:
    from gettsim.tt import ConsecutiveIntLookupTableParamValue


@policy_function(start_date="2001-01-01", end_date="2023-06-30", leaf_name="betrag_m")
def betrag_m_nach_wohnort(
    zugangsfaktor: float,
    entgeltpunkte_west: float,
    entgeltpunkte_ost: float,
    rentenartfaktor: float,
    grundsätzlich_anspruchsberechtigt: bool,
    sozialversicherung__rente__parameter_rentenwert_nach_wohnort: dict[
        str,
        float,
    ],
) -> float:
    """Erwerbsminderungsrente (public disability insurance).

    Legal reference: SGB VI § 64: Rentenformel für Monatsbetrag der Rente
    """
    if grundsätzlich_anspruchsberechtigt:
        out = (
            (
                entgeltpunkte_west
                * sozialversicherung__rente__parameter_rentenwert_nach_wohnort["west"]
                + entgeltpunkte_ost
                * sozialversicherung__rente__parameter_rentenwert_nach_wohnort["ost"]
            )
            * zugangsfaktor
            * rentenartfaktor
        )
    else:
        out = 0.0
    return out


@policy_function(start_date="2023-07-01", leaf_name="betrag_m")
def betrag_m_einheitlich(
    zugangsfaktor: float,
    entgeltpunkte: float,
    rentenartfaktor: float,
    grundsätzlich_anspruchsberechtigt: bool,
    sozialversicherung__rente__rentenwert: float,
) -> float:
    """Erwerbsminderungsrente (public disability insurance).

    Legal reference: SGB VI § 64: Rentenformel für Monatsbetrag der Rente
    """
    if grundsätzlich_anspruchsberechtigt:
        out = (
            entgeltpunkte
            * zugangsfaktor
            * sozialversicherung__rente__rentenwert
            * rentenartfaktor
        )
    else:
        out = 0.0
    return out


@policy_function(start_date="2001-01-01")
def grundsätzlich_anspruchsberechtigt(
    voll_erwerbsgemindert: bool,
    teilweise_erwerbsgemindert: bool,
    sozialversicherung__rente__pflichtbeitragsmonate: float,
    sozialversicherung__rente__mindestwartezeit_erfüllt: bool,
    mindestpflichtbeitragszeiten_monate: int,
) -> bool:
    """
    Eligibility for Erwerbsminderungsrente.

    Legal reference: § 43 Abs. 1  SGB VI.
    """
    anspruch_erwerbsm_rente = (
        (voll_erwerbsgemindert or teilweise_erwerbsgemindert)
        and sozialversicherung__rente__mindestwartezeit_erfüllt
        and sozialversicherung__rente__pflichtbeitragsmonate
        >= mindestpflichtbeitragszeiten_monate
    )

    return anspruch_erwerbsm_rente


@policy_function(start_date="2001-01-01", end_date="2023-06-30")
def entgeltpunkte_west(
    sozialversicherung__rente__entgeltpunkte_west: float,
    zusätzliche_entgeltpunkte_durch_zurechnungszeit: float,
    anteil_entgeltpunkte_ost: float,
) -> float:
    """Entgeltpunkte from West German Beitrags- and Zurechnungszeiten.

    In the case of the public disability insurance, pensioners are credited with
    additional earning points. They receive their average earned income points for each
    year between their age of retirement and the "Zurechnungszeitgrenze".
    """
    return sozialversicherung__rente__entgeltpunkte_west + (
        zusätzliche_entgeltpunkte_durch_zurechnungszeit * (1 - anteil_entgeltpunkte_ost)
    )


@policy_function(start_date="2001-01-01", end_date="2023-06-30")
def entgeltpunkte_ost(
    sozialversicherung__rente__entgeltpunkte_ost: float,
    zusätzliche_entgeltpunkte_durch_zurechnungszeit: float,
    anteil_entgeltpunkte_ost: float,
) -> float:
    """Entgeltpunkte from East German Beitrags- and Zurechnungszeiten.

    Provides the Entgeltpunkt-basis for calculation of the Erwerbsminderungsrente.

    In the case of the public disability insurance, pensioners are credited with
    additional earning points. They receive their average earned income points for each
    year between their age of retirement and the "Zurechnungszeitgrenze".
    """
    return sozialversicherung__rente__entgeltpunkte_ost + (
        zusätzliche_entgeltpunkte_durch_zurechnungszeit * anteil_entgeltpunkte_ost
    )


@policy_function(start_date="2023-07-01")
def entgeltpunkte(
    sozialversicherung__rente__entgeltpunkte: float,
    zusätzliche_entgeltpunkte_durch_zurechnungszeit: float,
) -> float:
    """Entgeltpunkte from Beitrags- and Zurechnungszeiten.

    Provides the Entgeltpunkt-basis for calculation of the Erwerbsminderungsrente.

    In the case of the public disability insurance, pensioners are credited with
    additional earning points. They receive their average earned income points for each
    year between their age of retirement and the "Zurechnungszeitgrenze".
    """
    return (
        sozialversicherung__rente__entgeltpunkte
        + zusätzliche_entgeltpunkte_durch_zurechnungszeit
    )


@policy_function(
    start_date="2000-12-23",
    end_date="2014-06-30",
    leaf_name="zusätzliche_entgeltpunkte_durch_zurechnungszeit",
)
def zusätzliche_entgeltpunkte_durch_zurechnungszeit_mit_gestaffelter_altersgrenze_bis_06_2014(
    mean_entgeltpunkte_pro_bewertungsmonat: float,
    sozialversicherung__rente__alter_bei_renteneintritt: float,
    sozialversicherung__rente__jahr_renteneintritt: int,
    sozialversicherung__rente__monat_renteneintritt: int,
    zurechnungszeitgrenze_gestaffelt: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Additional Entgeltpunkte accumulated through "Zurechnungszeit".

    Provides the Entgeltpunkt-basis for calculation of the Erwerbsminderungsrente.

    In the case of the public disability insurance, pensioners are credited with
    additional earning points. They receive their average earned income points for each
    year between their age of retirement and the "Zurechnungszeitgrenze".
    """
    claiming_month_since_ad = (
        sozialversicherung__rente__jahr_renteneintritt * 12
        + sozialversicherung__rente__monat_renteneintritt
    )
    altersgrenze_zurechnungszeit = zurechnungszeitgrenze_gestaffelt.look_up(
        claiming_month_since_ad
    )
    return (
        altersgrenze_zurechnungszeit
        - (sozialversicherung__rente__alter_bei_renteneintritt)
    ) * mean_entgeltpunkte_pro_bewertungsmonat


@policy_function(
    start_date="2014-07-01",
    end_date="2017-07-16",
    leaf_name="zusätzliche_entgeltpunkte_durch_zurechnungszeit",
)
def zusätzliche_entgeltpunkte_durch_zurechnungszeit_mit_einheitlicher_altersgrenze(
    mean_entgeltpunkte_pro_bewertungsmonat: float,
    sozialversicherung__rente__alter_bei_renteneintritt: float,
    zurechnungszeitgrenze: float,
) -> float:
    """Additional Entgeltpunkte accumulated through "Zurechnungszeit".

    Provides the Entgeltpunkt-basis for calculation of the Erwerbsminderungsrente.

    In the case of the public disability insurance, pensioners are credited with
    additional earning points. They receive their average earned income points for each
    year between their age of retirement and the "Zurechnungszeitgrenze".
    """
    return (
        zurechnungszeitgrenze - (sozialversicherung__rente__alter_bei_renteneintritt)
    ) * mean_entgeltpunkte_pro_bewertungsmonat


@policy_function(
    start_date="2017-07-17", leaf_name="zusätzliche_entgeltpunkte_durch_zurechnungszeit"
)
def zusätzliche_entgeltpunkte_durch_zurechnungszeit_mit_gestaffelter_altersgrenze_ab_07_2017(
    mean_entgeltpunkte_pro_bewertungsmonat: float,
    sozialversicherung__rente__alter_bei_renteneintritt: float,
    sozialversicherung__rente__jahr_renteneintritt: int,
    sozialversicherung__rente__monat_renteneintritt: int,
    zurechnungszeitgrenze_gestaffelt: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Additional Entgeltpunkte accumulated through "Zurechnungszeit".

    Provides the Entgeltpunkt-basis for calculation of the Erwerbsminderungsrente.

    In the case of the public disability insurance, pensioners are credited with
    additional earning points. They receive their average earned income points for each
    year between their age of retirement and the "Zurechnungszeitgrenze".
    """
    claiming_month_since_ad = (
        sozialversicherung__rente__jahr_renteneintritt * 12
        + sozialversicherung__rente__monat_renteneintritt
    )
    altersgrenze_zurechnungszeit = zurechnungszeitgrenze_gestaffelt.look_up(
        claiming_month_since_ad
    )
    return (
        altersgrenze_zurechnungszeit
        - (sozialversicherung__rente__alter_bei_renteneintritt)
    ) * mean_entgeltpunkte_pro_bewertungsmonat


@policy_function(start_date="2001-01-01")
def rentenartfaktor(
    teilweise_erwerbsgemindert: bool,
    parameter_rentenartfaktor: dict[str, float],
) -> float:
    """Rentenartfaktor.

    Legal reference: SGB VI § 67: rentenartfaktor
    """
    if teilweise_erwerbsgemindert:
        return parameter_rentenartfaktor["teilweise"]
    else:
        return parameter_rentenartfaktor["voll"]


@policy_function(end_date="2011-12-31", leaf_name="zugangsfaktor")
def zugangsfaktor_ohne_gestaffelte_altersgrenze(
    sozialversicherung__rente__alter_bei_renteneintritt: float,
    altersgrenze: float,
    min_zugangsfaktor: float,
    sozialversicherung__rente__zugangsfaktor_veränderung_pro_jahr: dict[
        str,
        float,
    ],
) -> float:
    """Zugangsfaktor.

    For each month that a pensioner retires before the age limit, a fraction of the
    pension is deducted. The maximum deduction is capped. This max deduction is the norm
    for the public disability insurance.

    Legal reference: § 77 Abs. 2-4  SGB VI
    """
    zugangsfaktor = (
        1
        + (sozialversicherung__rente__alter_bei_renteneintritt - altersgrenze)
        * (
            sozialversicherung__rente__zugangsfaktor_veränderung_pro_jahr[
                "vorzeitiger_renteneintritt"
            ]
        )
    )
    return max(zugangsfaktor, min_zugangsfaktor)


@policy_function(start_date="2012-01-01", leaf_name="zugangsfaktor")
def zugangsfaktor_mit_gestaffelter_altersgrenze(
    sozialversicherung__rente__alter_bei_renteneintritt: float,
    wartezeit_langjährig_versichert_erfüllt: bool,
    altersgrenze_gestaffelt: ConsecutiveIntLookupTableParamValue,
    sozialversicherung__rente__jahr_renteneintritt: int,
    sozialversicherung__rente__monat_renteneintritt: int,
    altersgrenze_langjährig_versichert: float,
    min_zugangsfaktor: float,
    sozialversicherung__rente__zugangsfaktor_veränderung_pro_jahr: dict[
        str,
        float,
    ],
) -> float:
    """Zugangsfaktor.

    For each month that a pensioner retires before the age limit, a fraction of the
    pension is deducted. The maximum deduction is capped. This max deduction is the norm
    for the public disability insurance.

    Legal reference: § 77 Abs. 2-4  SGB VI

    Paragraph 4 regulates an exceptional case in which pensioners can already retire at
    63 without deductions if they can prove 40 years of (Pflichtbeiträge,
    Berücksichtigungszeiten and certain Anrechnungszeiten or Ersatzzeiten).
    """
    claiming_month_since_ad = (
        sozialversicherung__rente__jahr_renteneintritt * 12
        + sozialversicherung__rente__monat_renteneintritt
    )

    if wartezeit_langjährig_versichert_erfüllt:
        grenze_abschlagsfrei = altersgrenze_langjährig_versichert
    else:
        grenze_abschlagsfrei = altersgrenze_gestaffelt.look_up(claiming_month_since_ad)

    zugangsfaktor = (
        1
        + (sozialversicherung__rente__alter_bei_renteneintritt - grenze_abschlagsfrei)
        * (
            sozialversicherung__rente__zugangsfaktor_veränderung_pro_jahr[
                "vorzeitiger_renteneintritt"
            ]
        )
    )
    return max(zugangsfaktor, min_zugangsfaktor)


# TODO(@MImmesberger): Reuse Altersrente Wartezeiten for Erwerbsminderungsrente
# https://github.com/ttsim-dev/gettsim/issues/838
@policy_function(start_date="2001-01-01")
def wartezeit_langjährig_versichert_erfüllt(
    sozialversicherung__rente__pflichtbeitragsmonate: float,
    sozialversicherung__rente__freiwillige_beitragsmonate: float,
    sozialversicherung__rente__anrechnungsmonate_45_jahre_wartezeit: float,
    sozialversicherung__rente__ersatzzeiten_monate: float,
    sozialversicherung__rente__kinderberücksichtigungszeiten_monate: float,
    sozialversicherung__rente__pflegeberücksichtigungszeiten_monate: float,
    sozialversicherung__rente__mindestpflichtbeitragsjahre_für_anrechenbarkeit_freiwilliger_beitragszeiten: float,
    wartezeitgrenze_langjährig_versicherte: float,
) -> bool:
    """Wartezeit for Rente für langjährige Versicherte (Erwerbsminderung) is fulfilled.

    Eligibility criteria differ in comparison to Altersrente für langjährige
    Versicherte. In particular, freiwillige Beitragszeiten are not always considered (§
    51 Abs. 3a SGB VI).

    This pathway makes it possible to claim pension benefits without deductions at the
    age of 63.
    """
    if (
        sozialversicherung__rente__pflichtbeitragsmonate / 12
        >= sozialversicherung__rente__mindestpflichtbeitragsjahre_für_anrechenbarkeit_freiwilliger_beitragszeiten
    ):
        freiwillige_beitragszeiten = (
            sozialversicherung__rente__freiwillige_beitragsmonate
        )
    else:
        freiwillige_beitragszeiten = 0

    return (
        sozialversicherung__rente__pflichtbeitragsmonate
        + freiwillige_beitragszeiten
        + sozialversicherung__rente__anrechnungsmonate_45_jahre_wartezeit
        + sozialversicherung__rente__ersatzzeiten_monate
        + sozialversicherung__rente__pflegeberücksichtigungszeiten_monate
        + sozialversicherung__rente__kinderberücksichtigungszeiten_monate
    ) / 12 >= wartezeitgrenze_langjährig_versicherte


@policy_function(end_date="2023-06-30")
def anteil_entgeltpunkte_ost(
    sozialversicherung__rente__entgeltpunkte_west: float,
    sozialversicherung__rente__entgeltpunkte_ost: float,
) -> float:
    """Proportion of Entgeltpunkte accumulated in East Germany."""
    if (
        sozialversicherung__rente__entgeltpunkte_west == 0
        and sozialversicherung__rente__entgeltpunkte_ost == 0
    ):
        out = 0.0
    else:
        out = sozialversicherung__rente__entgeltpunkte_ost / (
            sozialversicherung__rente__entgeltpunkte_west
            + sozialversicherung__rente__entgeltpunkte_ost
        )

    return out


@policy_function(
    end_date="2023-06-30", leaf_name="mean_entgeltpunkte_pro_bewertungsmonat"
)
def mean_entgeltpunkte_pro_bewertungsmonat_nach_wohnort(
    sozialversicherung__rente__entgeltpunkte_west: float,
    sozialversicherung__rente__entgeltpunkte_ost: float,
    sozialversicherung__rente__alter_bei_renteneintritt: float,
    altersgrenze_grundbewertung: float,
) -> float:
    """Average earning points per Bewertungsmonat (as part of the "Grundbewertung").

    Earnings points are divided by "belegungsfähige Gesamtzeitraum" which is the period
    from the age of 17 until the start of the pension.

    Legal reference: SGB VI § 72: Grundbewertung
    """
    belegungsfähiger_gesamtzeitraum = (
        sozialversicherung__rente__alter_bei_renteneintritt
        - altersgrenze_grundbewertung
    )

    return (
        sozialversicherung__rente__entgeltpunkte_west
        + sozialversicherung__rente__entgeltpunkte_ost
    ) / belegungsfähiger_gesamtzeitraum


@policy_function(
    start_date="2023-07-01", leaf_name="mean_entgeltpunkte_pro_bewertungsmonat"
)
def mean_entgeltpunkte_pro_bewertungsmonat_einheitlich(
    sozialversicherung__rente__entgeltpunkte: float,
    sozialversicherung__rente__alter_bei_renteneintritt: float,
    altersgrenze_grundbewertung: float,
) -> float:
    """Average earning points per Bewertungsmonat (as part of the "Grundbewertung").

    Earnings points are divided by "belegungsfähige Gesamtzeitraum" which is the period
    from the age of 17 until the start of the pension.

    Legal reference: SGB VI § 72: Grundbewertung
    """
    belegungsfähiger_gesamtzeitraum = (
        sozialversicherung__rente__alter_bei_renteneintritt
        - altersgrenze_grundbewertung
    )

    return sozialversicherung__rente__entgeltpunkte / belegungsfähiger_gesamtzeitraum
