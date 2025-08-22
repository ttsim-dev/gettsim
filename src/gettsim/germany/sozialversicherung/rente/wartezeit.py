"""Pension-relevant periods."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function()
def mindestwartezeit_erfüllt(
    pflichtbeitragsmonate: float,
    freiwillige_beitragsmonate: float,
    ersatzzeiten_monate: float,
    wartezeitgrenzen: dict[str, float],
) -> bool:
    """Minimal Wartezeit has been completed."""
    return (
        pflichtbeitragsmonate + freiwillige_beitragsmonate + ersatzzeiten_monate
    ) / 12 >= wartezeitgrenzen["wartezeit_5"]


@policy_function(end_date="2017-12-31")
def wartezeit_15_jahre_erfüllt(
    pflichtbeitragsmonate: float,
    freiwillige_beitragsmonate: float,
    ersatzzeiten_monate: float,
    wartezeitgrenzen: dict[str, float],
) -> bool:
    """Wartezeit of 15 years completed."""
    return (
        pflichtbeitragsmonate + freiwillige_beitragsmonate + ersatzzeiten_monate
    ) / 12 >= wartezeitgrenzen["wartezeit_15"]


@policy_function()
def wartezeit_35_jahre_erfüllt(
    pflichtbeitragsmonate: float,
    freiwillige_beitragsmonate: float,
    anrechnungsmonate_35_jahre_wartezeit: float,
    ersatzzeiten_monate: float,
    kinderberücksichtigungszeiten_monate: float,
    pflegeberücksichtigungszeiten_monate: float,
    wartezeitgrenzen: dict[str, float],
) -> bool:
    """Wartezeit of 35 years completed.

    All "rentenrechtliche Zeiten" are considered.
    """
    return (
        pflichtbeitragsmonate
        + freiwillige_beitragsmonate
        + anrechnungsmonate_35_jahre_wartezeit
        + ersatzzeiten_monate
        + kinderberücksichtigungszeiten_monate
        + pflegeberücksichtigungszeiten_monate
    ) / 12 >= wartezeitgrenzen["wartezeit_35"]


@policy_function(start_date="2012-01-01")
def wartezeit_45_jahre_erfüllt(
    pflichtbeitragsmonate: float,
    freiwillige_beitragsmonate: float,
    anrechnungsmonate_45_jahre_wartezeit: float,
    ersatzzeiten_monate: float,
    kinderberücksichtigungszeiten_monate: float,
    pflegeberücksichtigungszeiten_monate: float,
    wartezeitgrenzen: dict[str, float],
    mindestpflichtbeitragsjahre_für_anrechenbarkeit_freiwilliger_beitragszeiten: float,
) -> bool:
    """Wartezeit of 45 years completed.

    Not all "rentenrechtliche Zeiten" are considered. Years with voluntary contributions
    are only considered if at least 18 years of mandatory contributions
    (pflichtbeitragsmonate). Not all anrechnungszeiten are considered, but only specific
    ones (e.g. ALG I, Kurzarbeit but not ALG II).
    """
    if (
        pflichtbeitragsmonate / 12
        >= mindestpflichtbeitragsjahre_für_anrechenbarkeit_freiwilliger_beitragszeiten
    ):
        freiwillige_beitragszeiten = freiwillige_beitragsmonate
    else:
        freiwillige_beitragszeiten = 0

    return (
        pflichtbeitragsmonate
        + freiwillige_beitragszeiten
        + anrechnungsmonate_45_jahre_wartezeit
        + ersatzzeiten_monate
        + pflegeberücksichtigungszeiten_monate
        + kinderberücksichtigungszeiten_monate
    ) / 12 >= wartezeitgrenzen["wartezeit_45"]


@policy_function()
def anrechnungsmonate_35_jahre_wartezeit(
    monate_in_arbeitsunfähigkeit: float,
    krankheitszeiten_ab_16_bis_24_monate: float,
    monate_in_mutterschutz: float,
    monate_in_arbeitslosigkeit: float,
    monate_in_ausbildungssuche: float,
    monate_in_schulausbildung: float,
) -> float:
    """Anrechnungszeit for 35 years of Wartezeit.

    Reference: Studientext der Deutschen Rentenversicherung, Nr. 19,
    Wartezeiten, Ausgabe 2021, S. 24.
    """
    return (
        monate_in_arbeitsunfähigkeit
        + krankheitszeiten_ab_16_bis_24_monate
        + monate_in_mutterschutz
        + monate_in_arbeitslosigkeit
        + monate_in_ausbildungssuche
        + monate_in_schulausbildung
    )


@policy_function(start_date="2012-01-01")
def anrechnungsmonate_45_jahre_wartezeit(
    monate_in_arbeitsunfähigkeit: float,
    monate_mit_bezug_entgeltersatzleistungen_wegen_arbeitslosigkeit: float,
    monate_geringfügiger_beschäftigung: float,
) -> float:
    """Anrechnungszeit relevant for 45 years of Wartezeit.

    Reference: Studientext der Deutschen Rentenversicherung, Nr. 19, Wartezeiten,
    Ausgabe 2021, S. 24.
    > "nur Anrechnungszeiten mit Bezug von Entgeltersatzleistungen der Arbeitsförderung,
    > Leistungen bei Krankheit und Übergangsgeld".
    """
    return (
        monate_in_arbeitsunfähigkeit
        + monate_mit_bezug_entgeltersatzleistungen_wegen_arbeitslosigkeit
        + monate_geringfügiger_beschäftigung
    )
