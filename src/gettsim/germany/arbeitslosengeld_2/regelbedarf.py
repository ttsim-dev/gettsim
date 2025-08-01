"""Regelbedarf for Arbeitslosengeld II."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from gettsim.tt import (
    ConsecutiveIntLookupTableParamValue,
    get_consecutive_int_lookup_table_param_value,
    param_function,
    policy_function,
)

if TYPE_CHECKING:
    from types import ModuleType

    from gettsim.germany.grundsicherung.bedarfe import Regelbedarfsstufen
    from gettsim.tt import RawParam


@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def regelbedarf_m(
    regelsatz_m: float,
    kosten_der_unterkunft_m: float,
) -> float:
    """Basic monthly subsistence level on individual level.

    This includes cost of dwelling.
    """
    return regelsatz_m + kosten_der_unterkunft_m


@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def mehrbedarf_alleinerziehend_m(
    familie__alleinerziehend: bool,
    familie__anzahl_kinder_bis_17_fg: int,
    familie__anzahl_kinder_bis_6_fg: int,
    familie__anzahl_kinder_bis_15_fg: int,
    parameter_mehrbedarf_alleinerziehend: dict[str, float],
) -> float:
    """Mehrbedarf (additional need) for single parents as a share of the Regelsatz.

    Mehrbedarf for single parents is capped at 60% of the Regelsatz. There are special
    rules for parents of one child up to 6 years old and two or three children up to 15
    years old.

    Reference: §21 SGB II
    """
    basis_mehrbedarf = (
        parameter_mehrbedarf_alleinerziehend["basis_je_kind_bis_17"]
        * familie__anzahl_kinder_bis_17_fg
    )

    if (
        familie__anzahl_kinder_bis_6_fg == 1
        or familie__anzahl_kinder_bis_15_fg == 2  # noqa: PLR2004
        or familie__anzahl_kinder_bis_15_fg == 3  # noqa: PLR2004
    ):
        mehrbedarf = max(
            parameter_mehrbedarf_alleinerziehend["kind_bis_6_oder_2_3_kinder_bis_15"],
            basis_mehrbedarf,
        )
    else:
        mehrbedarf = basis_mehrbedarf

    if familie__alleinerziehend:
        return min(mehrbedarf, parameter_mehrbedarf_alleinerziehend["max"])
    else:
        return 0.0


@policy_function(
    start_date="2005-01-01",
    end_date="2010-12-31",
    leaf_name="kindersatz_m",
)
def kindersatz_m_anteilsbasiert(
    alter: int,
    kindergeld__gleiche_fg_wie_empfänger: bool,
    regelsatz_anteilsbasiert: RegelsatzAnteilsbasiert,
) -> float:
    """Basic monthly subsistence / SGB II needs of children until 2010."""
    basissatz = regelsatz_anteilsbasiert.basissatz

    if (
        alter
        >= regelsatz_anteilsbasiert.kind.jugendliche_und_junge_erwachsene.min_alter
        and alter
        <= regelsatz_anteilsbasiert.kind.jugendliche_und_junge_erwachsene.max_alter
        and kindergeld__gleiche_fg_wie_empfänger
    ):
        out = (
            basissatz
            * regelsatz_anteilsbasiert.kind.jugendliche_und_junge_erwachsene.anteil
        )
    elif (
        alter >= regelsatz_anteilsbasiert.kind.schulkind.min_alter
        and alter <= regelsatz_anteilsbasiert.kind.schulkind.max_alter
        and kindergeld__gleiche_fg_wie_empfänger
    ):
        out = basissatz * regelsatz_anteilsbasiert.kind.schulkind.anteil
    elif (
        alter >= regelsatz_anteilsbasiert.kind.kleinkind.min_alter
        and alter <= regelsatz_anteilsbasiert.kind.kleinkind.max_alter
        and kindergeld__gleiche_fg_wie_empfänger
    ):
        out = basissatz * regelsatz_anteilsbasiert.kind.kleinkind.anteil
    else:
        out = 0.0

    return out


@policy_function(
    start_date="2011-01-01",
    end_date="2022-06-30",
    leaf_name="kindersatz_m",
)
def kindersatz_m_nach_regelbedarfsstufen_ohne_sofortzuschlag(
    alter: int,
    kindergeld__gleiche_fg_wie_empfänger: bool,
    grundsicherung__regelbedarfsstufen: Regelbedarfsstufen,
) -> float:
    """Basic monthly subsistence / SGB II needs of children since 2011.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.
    """
    if (
        alter >= grundsicherung__regelbedarfsstufen.rbs_6.altersgrenzen.min_alter
        and alter <= grundsicherung__regelbedarfsstufen.rbs_6.altersgrenzen.max_alter
        and kindergeld__gleiche_fg_wie_empfänger
    ):
        out = grundsicherung__regelbedarfsstufen.rbs_6.satz
    elif (
        alter >= grundsicherung__regelbedarfsstufen.rbs_5.altersgrenzen.min_alter
        and alter <= grundsicherung__regelbedarfsstufen.rbs_5.altersgrenzen.max_alter
        and kindergeld__gleiche_fg_wie_empfänger
    ):
        out = grundsicherung__regelbedarfsstufen.rbs_5.satz
    elif (
        alter >= grundsicherung__regelbedarfsstufen.rbs_4.altersgrenzen.min_alter
        and alter <= grundsicherung__regelbedarfsstufen.rbs_4.altersgrenzen.max_alter
        and kindergeld__gleiche_fg_wie_empfänger
    ):
        out = grundsicherung__regelbedarfsstufen.rbs_4.satz
    elif kindergeld__gleiche_fg_wie_empfänger:  # adult children with parents in FG
        out = grundsicherung__regelbedarfsstufen.rbs_3
    else:
        out = 0.0

    return out


@policy_function(
    start_date="2022-07-01",
    end_date="2022-12-31",
    leaf_name="kindersatz_m",
)
def kindersatz_m_nach_regelbedarfsstufen_mit_sofortzuschlag(
    alter: int,
    kindergeld__gleiche_fg_wie_empfänger: bool,
    grundsicherung__regelbedarfsstufen: Regelbedarfsstufen,
    kindersofortzuschlag: float,
) -> float:
    """Basic monthly subsistence / SGB II needs of children since 2011."""
    if (
        alter >= grundsicherung__regelbedarfsstufen.rbs_6.altersgrenzen.min_alter
        and alter <= grundsicherung__regelbedarfsstufen.rbs_6.altersgrenzen.max_alter
        and kindergeld__gleiche_fg_wie_empfänger
    ):
        out = kindersofortzuschlag + grundsicherung__regelbedarfsstufen.rbs_6.satz
    elif (
        alter >= grundsicherung__regelbedarfsstufen.rbs_5.altersgrenzen.min_alter
        and alter <= grundsicherung__regelbedarfsstufen.rbs_5.altersgrenzen.max_alter
        and kindergeld__gleiche_fg_wie_empfänger
    ):
        out = kindersofortzuschlag + grundsicherung__regelbedarfsstufen.rbs_5.satz
    elif (
        alter >= grundsicherung__regelbedarfsstufen.rbs_4.altersgrenzen.min_alter
        and alter <= grundsicherung__regelbedarfsstufen.rbs_4.altersgrenzen.max_alter
        and kindergeld__gleiche_fg_wie_empfänger
    ):
        out = kindersofortzuschlag + grundsicherung__regelbedarfsstufen.rbs_4.satz
    elif kindergeld__gleiche_fg_wie_empfänger:  # adult children with parents in FG
        out = kindersofortzuschlag + grundsicherung__regelbedarfsstufen.rbs_3
    else:
        out = 0.0

    return out


@policy_function(
    start_date="2005-01-01",
    end_date="2010-12-31",
    leaf_name="erwachsenensatz_m",
)
def erwachsenensatz_m_bis_2010(
    mehrbedarf_alleinerziehend_m: float,
    kindersatz_m: float,
    p_id_einstandspartner: int,
    regelsatz_anteilsbasiert: RegelsatzAnteilsbasiert,
) -> float:
    """Basic monthly subsistence / SGB II needs for adults without dwelling."""
    # BG has 2 adults
    if p_id_einstandspartner >= 0:
        out = regelsatz_anteilsbasiert.basissatz * (
            regelsatz_anteilsbasiert.erwachsen.je_erwachsener_bei_zwei_erwachsenen
        )
    # This observation is not a child, so BG has 1 adult
    elif kindersatz_m == 0.0:
        out = regelsatz_anteilsbasiert.basissatz
    else:
        out = 0.0

    return out * (1 + mehrbedarf_alleinerziehend_m)


@policy_function(
    start_date="2011-01-01",
    end_date="2022-12-31",
    leaf_name="erwachsenensatz_m",
)
def erwachsenensatz_m_ab_2011(
    mehrbedarf_alleinerziehend_m: float,
    kindersatz_m: float,
    p_id_einstandspartner: int,
    grundsicherung__regelbedarfsstufen: Regelbedarfsstufen,
) -> float:
    """Basic monthly subsistence / SGB II needs for adults without dwelling since 2011."""
    # BG has 2 adults
    if p_id_einstandspartner >= 0:
        out = grundsicherung__regelbedarfsstufen.rbs_2
    # This observation is not a child, so BG has 1 adult
    elif kindersatz_m == 0.0:
        out = grundsicherung__regelbedarfsstufen.rbs_1
    else:
        out = 0.0

    return out * (1 + mehrbedarf_alleinerziehend_m)


@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def regelsatz_m(
    erwachsenensatz_m: float,
    kindersatz_m: float,
) -> float:
    """Basic monthly subsistence without dwelling."""
    return erwachsenensatz_m + kindersatz_m


@policy_function(
    start_date="2005-01-01",
    end_date="2022-12-31",
    leaf_name="kosten_der_unterkunft_m",
)
def kosten_der_unterkunft_m_bis_2022(
    berechtigte_wohnfläche: float,
    anerkannte_warmmiete_je_qm_m: float,
) -> float:
    """Costs of living eligible to claim."""
    return berechtigte_wohnfläche * anerkannte_warmmiete_je_qm_m


@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def anerkannte_warmmiete_je_qm_m(
    bruttokaltmiete_m: float,
    heizkosten_m: float,
    wohnfläche: float,
    mietobergrenze_pro_qm: float,
) -> float:
    """Rent per square meter."""
    out = (bruttokaltmiete_m + heizkosten_m) / wohnfläche
    return min(out, mietobergrenze_pro_qm)


@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def berechtigte_wohnfläche(
    wohnfläche: float,
    wohnen__bewohnt_eigentum_hh: bool,
    anzahl_personen_hh: int,
    berechtigte_wohnfläche_miete: dict[str, float],
    berechtigte_wohnfläche_eigentum: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Size of dwelling eligible to claim."""
    if wohnen__bewohnt_eigentum_hh:
        maximum = berechtigte_wohnfläche_eigentum.look_up(anzahl_personen_hh)
    else:
        maximum = (
            berechtigte_wohnfläche_miete["single"]
            + max(anzahl_personen_hh - 1, 0)
            * berechtigte_wohnfläche_miete["je_weitere_person"]
        )
    return min(wohnfläche, maximum / anzahl_personen_hh)


@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def bruttokaltmiete_m(
    wohnen__bruttokaltmiete_m_hh: float,
    anzahl_personen_hh: int,
) -> float:
    """Monthly rent attributed to a single person.

    Reference:
    BSG Urteil v. 09.03.2016 - B 14 KG 1/15 R.
    BSG Urteil vom 15.04.2008 - B 14/7b AS 58/06 R.
    """
    return wohnen__bruttokaltmiete_m_hh / anzahl_personen_hh


@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def heizkosten_m(
    wohnen__heizkosten_m_hh: float,
    anzahl_personen_hh: int,
) -> float:
    """Monthly heating expenses attributed to a single person.

    Reference:
    BSG Urteil v. 09.03.2016 - B 14 KG 1/15 R.
    BSG Urteil vom 15.04.2008 - B 14/7b AS 58/06 R.
    """
    return wohnen__heizkosten_m_hh / anzahl_personen_hh


@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def wohnfläche(
    wohnen__wohnfläche_hh: float,
    anzahl_personen_hh: int,
) -> float:
    """Share of household's dwelling size attributed to a single person."""
    return wohnen__wohnfläche_hh / anzahl_personen_hh


@dataclass(frozen=True)
class RegelsatzAnteilErwachsen:
    je_erwachsener_bei_zwei_erwachsenen: float
    je_erwachsener_ab_drei_erwachsene: float


@dataclass(frozen=True)
class RegelsatzAnteilKind:
    anteil: float
    min_alter: int
    max_alter: int


@dataclass(frozen=True)
class RegelsatzAnteilKindNachAlter:
    kleinkind: RegelsatzAnteilKind
    schulkind: RegelsatzAnteilKind
    jugendliche_und_junge_erwachsene: RegelsatzAnteilKind


@dataclass(frozen=True)
class RegelsatzAnteilsbasiert:
    basissatz: float
    erwachsen: RegelsatzAnteilErwachsen
    kind: RegelsatzAnteilKindNachAlter


@param_function(start_date="2005-01-01", end_date="2010-12-31")
def regelsatz_anteilsbasiert(
    parameter_regelsatz_anteilsbasiert: RawParam,
) -> RegelsatzAnteilsbasiert:
    """Regelsatz as a fraction of the Basissatz."""
    anteilssätze_kinder = parameter_regelsatz_anteilsbasiert[
        "anteil_vom_basissatz_für_kinder"
    ]
    kind_kleinkind = RegelsatzAnteilKind(
        anteil=anteilssätze_kinder["kleinkind"]["anteil"],
        min_alter=anteilssätze_kinder["kleinkind"]["min_alter"],
        max_alter=anteilssätze_kinder["kleinkind"]["max_alter"],
    )
    kind_schulkind = RegelsatzAnteilKind(
        anteil=anteilssätze_kinder["schulkind"]["anteil"],
        min_alter=anteilssätze_kinder["schulkind"]["min_alter"],
        max_alter=anteilssätze_kinder["schulkind"]["max_alter"],
    )
    kind_jugendliche_und_junge_erwachsene = RegelsatzAnteilKind(
        anteil=anteilssätze_kinder["jugendliche_und_junge_erwachsene"]["anteil"],
        min_alter=anteilssätze_kinder["jugendliche_und_junge_erwachsene"]["min_alter"],
        max_alter=anteilssätze_kinder["jugendliche_und_junge_erwachsene"]["max_alter"],
    )
    erwachsen = RegelsatzAnteilErwachsen(
        je_erwachsener_bei_zwei_erwachsenen=parameter_regelsatz_anteilsbasiert[
            "anteil_vom_basissatz_bei_zwei_erwachsenen"
        ],
        je_erwachsener_ab_drei_erwachsene=parameter_regelsatz_anteilsbasiert[
            "anteil_vom_basissatz_bei_weiteren_erwachsenen"
        ],
    )
    return RegelsatzAnteilsbasiert(
        basissatz=parameter_regelsatz_anteilsbasiert["basissatz"],
        erwachsen=erwachsen,
        kind=RegelsatzAnteilKindNachAlter(
            kleinkind=kind_kleinkind,
            schulkind=kind_schulkind,
            jugendliche_und_junge_erwachsene=kind_jugendliche_und_junge_erwachsene,
        ),
    )


@param_function(start_date="2005-01-01", end_date="2022-12-31")
def berechtigte_wohnfläche_eigentum(
    parameter_berechtigte_wohnfläche_eigentum: RawParam,
    wohngeld__max_anzahl_personen: dict[str, int],
    xnp: ModuleType,
) -> ConsecutiveIntLookupTableParamValue:
    """Berechtigte Wohnfläche für Eigenheim."""
    tmp = parameter_berechtigte_wohnfläche_eigentum.copy()
    je_weitere_person = tmp.pop("je_weitere_person")
    max_anzahl_direkt = tmp.pop("max_anzahl_direkt")
    for i in range(wohngeld__max_anzahl_personen["indizierung"] - max_anzahl_direkt):
        tmp[i] = tmp[max_anzahl_direkt] + i * je_weitere_person
    return get_consecutive_int_lookup_table_param_value(raw=tmp, xnp=xnp)
