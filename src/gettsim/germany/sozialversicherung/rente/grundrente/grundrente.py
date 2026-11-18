from __future__ import annotations

from gettsim.tt import (
    RoundingSpec,
    TTSIMUnit,
    cast_ttsim_unit,
    param_function,
    policy_function,
)


@policy_function(
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_MONTH,
        base=0.01,
        direction="nearest",
        reference="§ 123 SGB VI Abs. 1",
    ),
    start_date="2021-01-01",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_m(basisbetrag_m: float, anzurechnendes_einkommen_m: float) -> float:
    """Additional monthly pensions payments (Grundrentenzuschlag)."""
    out = basisbetrag_m - anzurechnendes_einkommen_m
    return max(out, 0.0)


@policy_function(
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_MONTH,
        base=0.01,
        direction="nearest",
        reference="§ 123 SGB VI Abs. 1",
    ),
    start_date="2021-01-01",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def anzurechnendes_einkommen_m(
    einkommen_vorvorjahr_m_ehe: float,
    untere_einkommensgrenze_m: float,
    obere_einkommensgrenze_m: float,
    anrechnungssätze: dict[str, float],
) -> float:
    """Income which is deducted from Grundrentenzuschlag.

    The income of the Berechtigter and their spouse is added up. Above the lower
    threshold, 60 % of the income up to the upper threshold is credited; above the
    upper threshold, the full excess is credited as well.

    Reference: § 97a Abs. 1, Abs. 4 S. 1-4 SGB VI
    """
    # The couple's income is compared with the thresholds, and the result is credited
    # in full against each spouse's Zuschlag, so the sum loses its group level here.
    einkommen_m = cast_ttsim_unit(
        einkommen_vorvorjahr_m_ehe, unit=TTSIMUnit.CURRENCY.PER_MONTH
    )
    einkommen_zwischen_den_grenzen = min(
        max(einkommen_m - untere_einkommensgrenze_m, 0.0),
        obere_einkommensgrenze_m - untere_einkommensgrenze_m,
    )
    einkommen_über_der_oberen_grenze = max(einkommen_m - obere_einkommensgrenze_m, 0.0)
    return (
        anrechnungssätze["zwischen_den_grenzen"] * einkommen_zwischen_den_grenzen
        + anrechnungssätze["über_der_oberen_grenze"] * einkommen_über_der_oberen_grenze
    )


@policy_function(
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_MONTH,
        base=1,
        direction="up",
        reference="§ 97a Abs. 4 S. 1 SGB VI",
    ),
    start_date="2021-01-01",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def untere_einkommensgrenze_m(
    familie__anzahl_personen_ehe: int,
    rentenwert_für_einkommensgrenzen_m: float,
    einkommensgrenzen_ohne_ehegatte: dict[str, float],
    einkommensgrenzen_mit_ehegatte: dict[str, float],
) -> float:
    """Income up to which nothing is credited against the Grundrentenzuschlag.

    Married Berechtigte get the threshold for couples, also if the spouse has no income
    or lives apart. The statute does not settle this case; GETTSIM follows DRV, GRA zu
    § 97a SGB VI, Version 008.00, Abschnitt 5 ("Der für Ehegatten höhere Freibetrag ist
    auch dann zu berücksichtigen, wenn der Ehegatte des Berechtigten über kein eigenes
    Einkommen verfügt.") and Abschnitt 2 ("Dies gilt auch für dauernd getrenntlebende
    Ehegatten").

    Reference: § 97a Abs. 4 S. 1, 2, 4 SGB VI
    """
    if familie__anzahl_personen_ehe > cast_ttsim_unit(1, unit=TTSIMUnit.COUNT.PER_EHE):
        out = (
            einkommensgrenzen_mit_ehegatte["untere_grenze"]
            * rentenwert_für_einkommensgrenzen_m
        )
    else:
        out = (
            einkommensgrenzen_ohne_ehegatte["untere_grenze"]
            * rentenwert_für_einkommensgrenzen_m
        )
    return out


@policy_function(
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_MONTH,
        base=1,
        direction="up",
        reference="§ 97a Abs. 4 S. 1 SGB VI",
    ),
    start_date="2021-01-01",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def obere_einkommensgrenze_m(
    familie__anzahl_personen_ehe: int,
    rentenwert_für_einkommensgrenzen_m: float,
    einkommensgrenzen_ohne_ehegatte: dict[str, float],
    einkommensgrenzen_mit_ehegatte: dict[str, float],
) -> float:
    """Income above which all income is credited against the Grundrentenzuschlag.

    Married Berechtigte get the threshold for couples, also if the spouse has no income
    or lives apart. The statute does not settle this case; GETTSIM follows DRV, GRA zu
    § 97a SGB VI, Version 008.00, Abschnitte 2 and 5 (see `untere_einkommensgrenze_m`).

    Reference: § 97a Abs. 4 S. 1, 3, 4 SGB VI
    """
    if familie__anzahl_personen_ehe > cast_ttsim_unit(1, unit=TTSIMUnit.COUNT.PER_EHE):
        out = (
            einkommensgrenzen_mit_ehegatte["obere_grenze"]
            * rentenwert_für_einkommensgrenzen_m
        )
    else:
        out = (
            einkommensgrenzen_ohne_ehegatte["obere_grenze"]
            * rentenwert_für_einkommensgrenzen_m
        )
    return out


@param_function(
    start_date="2021-01-01",
    end_date="2023-12-31",
    leaf_name="rentenwert_für_einkommensgrenzen_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def rentenwert_für_einkommensgrenzen_nach_wohnort_m(
    sozialversicherung__rente__parameter_rentenwert_nach_wohnort_jahresanfang: dict[
        str, float
    ],
) -> float:
    """Rentenwert that sets the income thresholds of the calendar year.

    Changes of the thresholds take effect on 1 January, so the Rentenwert in force on
    1 January applies for the whole year.

    Until 30 June 2023 the Rentenwert differed between West and Ost. The thresholds
    are nevertheless uniform across Germany and use the West value, also for
    Berechtigte living in the Beitrittsgebiet (DRV, GRA zu § 97a SGB VI: "Durch die
    Anknüpfung an den aktuellen Rentenwert gelten die Freibeträge einheitlich im
    gesamten Bundesgebiet"; BT-Drs. 19/18473, p. 42: "Die jeweils maßgebenden Beträge
    gelten einheitlich für Berechtigte im gesamten Bundesgebiet."). The 2021 thresholds
    stated there (1 250, 1 600, 1 950 and 2 300 euros) equal the factors times the West
    value of 34.19 euros, rounded up.

    Reference: § 97a Abs. 4 S. 5 i.V.m. Abs. 5 S. 2 SGB VI
    """
    return sozialversicherung__rente__parameter_rentenwert_nach_wohnort_jahresanfang[
        "west"
    ]


@param_function(
    start_date="2024-01-01",
    leaf_name="rentenwert_für_einkommensgrenzen_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def rentenwert_für_einkommensgrenzen_einheitlich_m(
    sozialversicherung__rente__rentenwert_m_jahresanfang: float,
) -> float:
    """Rentenwert that sets the income thresholds of the calendar year.

    Changes of the thresholds take effect on 1 January, so the Rentenwert in force on
    1 January applies for the whole year.

    Reference: § 97a Abs. 4 S. 5 i.V.m. Abs. 5 S. 2 SGB VI
    """
    return sozialversicherung__rente__rentenwert_m_jahresanfang


@policy_function(
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_MONTH,
        base=0.01,
        direction="nearest",
        reference="§ 123 SGB VI Abs. 1",
    ),
    start_date="2021-01-01",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def basisbetrag_m(
    mean_entgeltpunkte_zuschlag_m: float,
    bewertungszeiten_monate: int,
    sozialversicherung__rente__rentenwert_m: float,
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
        mean_entgeltpunkte_zuschlag_m
        * bewertungszeiten
        * sozialversicherung__rente__rentenwert_m
        * zugangsfaktor
    )


@policy_function(start_date="2021-01-01", unit=TTSIMUnit.DIMENSIONLESS.PER_MONTH)
def mean_entgeltpunkte_pro_bewertungsmonat_m(
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
        reference="§ 76g Abs. 4 S. 4 SGB VI",
    ),
    start_date="2021-01-01",
    unit=TTSIMUnit.DIMENSIONLESS.PER_MONTH,
)
def höchstbetrag_m(
    grundrentenzeiten_monate: int,
    berücksichtigte_wartezeit_monate: dict[str, int],
    höchstwert_der_entgeltpunkte: dict[str, float],
) -> float:
    """Maximum allowed number of average Entgeltpunkte."""
    # The number of increment-steps above the threshold — a plain count multiplying
    # the per-month increment.
    months_above_thresh = cast_ttsim_unit(
        min(
            grundrentenzeiten_monate,
            berücksichtigte_wartezeit_monate["max"],
        )
        - berücksichtigte_wartezeit_monate["min"],
        unit=TTSIMUnit.DIMENSIONLESS,
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
    unit=TTSIMUnit.DIMENSIONLESS.PER_MONTH,
)
def mean_entgeltpunkte_zuschlag_m(
    mean_entgeltpunkte_pro_bewertungsmonat_m: float,
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
    # A per-month zero for the "no additional Entgeltpunkte" branches, so every branch
    # yields the declared `1 / month` (a bare 0.0 would infer dimensionless here).
    kein_zuschlag_m = cast_ttsim_unit(0.0, unit=TTSIMUnit.DIMENSIONLESS.PER_MONTH)

    out = kein_zuschlag_m
    # Return 0 if Grundrentenzeiten below minimum
    if grundrentenzeiten_monate < berücksichtigte_wartezeit_monate["min"]:
        out = kein_zuschlag_m
    else:
        # Case 1: Entgeltpunkte less than half of Höchstwert
        if mean_entgeltpunkte_pro_bewertungsmonat_m <= (0.5 * höchstbetrag_m):
            out = mean_entgeltpunkte_pro_bewertungsmonat_m

        # Case 2: Entgeltpunkte more than half of Höchstwert, but below Höchstwert
        elif mean_entgeltpunkte_pro_bewertungsmonat_m < höchstbetrag_m:
            out = höchstbetrag_m - mean_entgeltpunkte_pro_bewertungsmonat_m

        # Case 3: Entgeltpunkte above Höchstwert
        elif mean_entgeltpunkte_pro_bewertungsmonat_m > höchstbetrag_m:
            out = kein_zuschlag_m

    # Multiply additional Engeltpunkte by factor
    return out * bonusfaktor


@policy_function(start_date="2021-01-01", unit=TTSIMUnit.DIMENSIONLESS)
def grundsätzlich_anspruchsberechtigt(
    grundrentenzeiten_monate: int,
    berücksichtigte_wartezeit_monate: dict[str, int],
) -> bool:
    """Has accumulated enough insured years to be eligible."""
    return grundrentenzeiten_monate >= berücksichtigte_wartezeit_monate["min"]


@policy_function(start_date="2021-01-01", unit=TTSIMUnit.CURRENCY.PER_YEAR)
def einkommen_für_einkommensanrechnung_im_übernächsten_jahr_y(
    einkommensteuer__zu_versteuerndes_einkommen_y_sn: float,
    einkommensteuer__einkünfte__aus_kapitalvermögen__betrag_y_sn: float,
    einkommensteuer__einkünfte__sonstige__rente__renten_aus_basisversorgung_y: float,
    einkommensteuer__einkünfte__sonstige__rente__steuerpflichtiger_anteil_der_renteneinnahmen_y: float,
    familie__anzahl_personen_sn: int,
) -> float:
    """Income of this calendar year relevant for the Grundrentenzuschlag.

    The Grundrentenzuschlag of a calendar year is reduced by the income of the year
    before the previous one (vorvergangenes Kalenderjahr, § 97a Abs. 2 S. 2 SGB VI), or
    of the year before that if no tax assessment exists (S. 3). Its sum over the
    spouses can be used as the input `einkommen_vorvorjahr_m_ehe` in a GETTSIM call for
    the year after next. It is the sum of

    - the zu versteuerndes Einkommen,
    - the steuerfreier Teil of pensions taxed at the Besteuerungsanteil, and
    - the capital income subject to the Abgeltungsteuer.

    The zu versteuerndes Einkommen and the capital income are split equally among the
    members of the Steuernummer, so that the sum over the spouses is the couple's
    income both under joint and under separate assessment.

    The share of the pension resting on the Grundrentenzuschlag is tax-free (§ 3 Nr. 14a
    EStG), so it is contained in neither the zu versteuerndes Einkommen nor the
    steuerfreier Teil of pensions computed here (cf. § 97a Abs. 2 S. 7 SGB VI).

    A negative zu versteuerndes Einkommen (possible only if supplied as data) is added
    as is and offsets the other components. Neither the statute nor the GRA addresses
    negative amounts; this follows the wording of § 97a Abs. 2 S. 1 SGB VI, which sums
    the components.

    Reference: § 97a Abs. 2 S. 1 SGB VI
    """
    zu_versteuerndes_einkommen_y = (
        einkommensteuer__zu_versteuerndes_einkommen_y_sn / familie__anzahl_personen_sn
    )
    kapitaleinkünfte_y = (
        einkommensteuer__einkünfte__aus_kapitalvermögen__betrag_y_sn
        / familie__anzahl_personen_sn
    )
    steuerfreier_teil_der_renten_y = (
        einkommensteuer__einkünfte__sonstige__rente__renten_aus_basisversorgung_y
        - einkommensteuer__einkünfte__sonstige__rente__steuerpflichtiger_anteil_der_renteneinnahmen_y
    )
    return (
        zu_versteuerndes_einkommen_y
        + steuerfreier_teil_der_renten_y
        + kapitaleinkünfte_y
    )
