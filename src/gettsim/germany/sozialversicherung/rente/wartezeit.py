"""Pension-relevant periods."""

from __future__ import annotations

from ttsim.time_converters import m_to_y

from gettsim.tt import TTSIMUnit, policy_function


@policy_function(unit=TTSIMUnit.DIMENSIONLESS)
def mindestwartezeit_erfüllt(
    pflichtbeitragsmonate: float,
    freiwillige_beitragsmonate: float,
    ersatzzeiten_monate: float,
    wartezeitgrenzen: dict[str, float],
) -> bool:
    """Minimal Wartezeit has been completed.

    Reference:
        - § 1246 Abs. 3 RVO idF Art. 1 G. v. 23.02.1957 BGBl. I S. 45
        - § 50 Abs. 1 Satz 1 SGB VI idF Art. 1 G. v. 18.12.1989 BGBl. I S. 2261
        - § 51 Abs. 1 SGB VI idF Art. 1 G. v. 18.12.1989 BGBl. I S. 2261
    """
    return (
        m_to_y(pflichtbeitragsmonate + freiwillige_beitragsmonate + ersatzzeiten_monate)
        >= wartezeitgrenzen["wartezeit_5"]
    )


@policy_function(end_date="2017-12-31", unit=TTSIMUnit.DIMENSIONLESS)
def wartezeit_15_jahre_erfüllt(
    pflichtbeitragsmonate: float,
    freiwillige_beitragsmonate: float,
    ersatzzeiten_monate: float,
    wartezeitgrenzen: dict[str, float],
) -> bool:
    """Wartezeit of 15 years completed.

    Reference:
        - § 1248 Abs. 7 Satz 2 RVO idF Art. 1 G. v. 16.10.1972 BGBl. I S. 1965
        - § 50 Abs. 2 SGB VI idF Art. 1 G. v. 18.12.1989 BGBl. I S. 2261
        - § 51 Abs. 1 SGB VI idF Art. 1 G. v. 18.12.1989 BGBl. I S. 2261
        - § 237 Abs. 1 Nr. 5 SGB VI idF Art. 1 G. v. 16.12.1997 BGBl. I S. 2998
        - § 237a Abs. 1 Nr. 4 SGB VI idF Art. 1 G. v. 16.12.1997 BGBl. I S. 2998
    """
    return (
        m_to_y(pflichtbeitragsmonate + freiwillige_beitragsmonate + ersatzzeiten_monate)
        >= wartezeitgrenzen["wartezeit_15"]
    )


@policy_function(unit=TTSIMUnit.DIMENSIONLESS)
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

    Reference:
        - § 1248 Abs. 7 Satz 1 RVO idF Art. 1 G. v. 16.10.1972 BGBl. I S. 1965
        - § 50 Abs. 5 SGB VI idF Art. 1 G. v. 18.12.1989 BGBl. I S. 2261
        - § 51 Abs. 3 SGB VI idF Art. 1 G. v. 18.12.1989 BGBl. I S. 2261
    """
    return (
        m_to_y(
            pflichtbeitragsmonate
            + freiwillige_beitragsmonate
            + anrechnungsmonate_35_jahre_wartezeit
            + ersatzzeiten_monate
            + kinderberücksichtigungszeiten_monate
            + pflegeberücksichtigungszeiten_monate
        )
        >= wartezeitgrenzen["wartezeit_35"]
    )


@policy_function(start_date="2012-01-01", unit=TTSIMUnit.DIMENSIONLESS)
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

    Reference:
        - § 50 Abs. 5 SGB VI idF Art. 1 G. v. 20.04.2007 BGBl. I S. 554
        - § 51 Abs. 3a SGB VI idF Art. 1 G. v. 20.04.2007 BGBl. I S. 554
        - § 51 Abs. 3a SGB VI idF Art. 1 G. v. 23.06.2014 BGBl. I S. 787
    """
    if (
        m_to_y(pflichtbeitragsmonate)
        >= mindestpflichtbeitragsjahre_für_anrechenbarkeit_freiwilliger_beitragszeiten
    ):
        freiwillige_beitragszeiten = freiwillige_beitragsmonate
    else:
        freiwillige_beitragszeiten = 0

    return (
        m_to_y(
            pflichtbeitragsmonate
            + freiwillige_beitragszeiten
            + anrechnungsmonate_45_jahre_wartezeit
            + ersatzzeiten_monate
            + pflegeberücksichtigungszeiten_monate
            + kinderberücksichtigungszeiten_monate
        )
        >= wartezeitgrenzen["wartezeit_45"]
    )


@policy_function(unit=TTSIMUnit.MONTHS)
def anrechnungsmonate_35_jahre_wartezeit(
    monate_in_arbeitsunfähigkeit: float,
    krankheitszeiten_ab_16_bis_24_monate: float,
    monate_in_mutterschutz: float,
    monate_in_arbeitslosigkeit: float,
    monate_in_ausbildungssuche: float,
    monate_in_schulausbildung: float,
) -> float:
    """Anrechnungszeit for 35 years of Wartezeit.

    See Studientext der Deutschen Rentenversicherung, Nr. 19, Wartezeiten, Ausgabe
    2021, S. 24.

    Reference:
        - § 51 Abs. 3 SGB VI idF Art. 1 G. v. 18.12.1989 BGBl. I S. 2261
        - § 58 Abs. 1 Satz 1 SGB VI idF Art. 1 G. v. 18.12.1989 BGBl. I S. 2261
        - § 58 Abs. 1 Satz 1 SGB VI idF Art. 6 G. v. 12.06.2020 BGBl. I S. 1248
    """
    return (
        monate_in_arbeitsunfähigkeit
        + krankheitszeiten_ab_16_bis_24_monate
        + monate_in_mutterschutz
        + monate_in_arbeitslosigkeit
        + monate_in_ausbildungssuche
        + monate_in_schulausbildung
    )


@policy_function(start_date="2012-01-01", unit=TTSIMUnit.MONTHS)
def anrechnungsmonate_45_jahre_wartezeit(
    monate_in_arbeitsunfähigkeit: float,
    monate_mit_bezug_entgeltersatzleistungen_wegen_arbeitslosigkeit: float,
    monate_geringfügiger_beschäftigung: float,
) -> float:
    """Anrechnungszeit relevant for 45 years of Wartezeit.

    Studientext der Deutschen Rentenversicherung, Nr. 19, Wartezeiten, Ausgabe 2021,
    S. 24: "nur Anrechnungszeiten mit Bezug von Entgeltersatzleistungen der
    Arbeitsförderung, Leistungen bei Krankheit und Übergangsgeld".

    Before 1 July 2014, § 51 Abs. 3a SGB VI counted none of these periods.

    Reference:
        - § 51 Abs. 3a SGB VI idF Art. 1 G. v. 20.04.2007 BGBl. I S. 554
        - § 51 Abs. 3a Satz 1 Nr. 3 SGB VI idF Art. 1 G. v. 23.06.2014 BGBl. I S. 787
    """
    return (
        monate_in_arbeitsunfähigkeit
        + monate_mit_bezug_entgeltersatzleistungen_wegen_arbeitslosigkeit
        + monate_geringfügiger_beschäftigung
    )
