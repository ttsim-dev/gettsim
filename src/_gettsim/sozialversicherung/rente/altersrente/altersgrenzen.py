"""Age thresholds for public pension eligibility."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import policy_function

if TYPE_CHECKING:
    from types import ModuleType


@policy_function(
    end_date="2011-12-31",
    leaf_name="altersgrenze",
)
def altersgrenze_mit_arbeitslosigkeit_frauen_ohne_besonders_langjährig(
    wegen_arbeitslosigkeit__grundsätzlich_anspruchsberechtigt: bool,
    wegen_arbeitslosigkeit__altersgrenze: float,
    für_frauen__grundsätzlich_anspruchsberechtigt: bool,
    für_frauen__altersgrenze: float,
    langjährig__grundsätzlich_anspruchsberechtigt: bool,
    langjährig__altersgrenze: float,
    regelaltersrente__altersgrenze: float,
    xnp: ModuleType,
) -> float:
    """Full retirement age after eligibility checks, assuming eligibility for
    Regelaltersrente.

    Age at which pension can be claimed without deductions. This age is smaller or equal
    to the normal retirement age (FRA<=NRA) and depends on personal characteristics as
    gender, insurance duration, health/disability, employment status.
    """
    out = regelaltersrente__altersgrenze
    if für_frauen__grundsätzlich_anspruchsberechtigt:
        out = xnp.minimum(out, für_frauen__altersgrenze)
    if wegen_arbeitslosigkeit__grundsätzlich_anspruchsberechtigt:
        out = xnp.minimum(
            out,
            wegen_arbeitslosigkeit__altersgrenze,
        )
    if langjährig__grundsätzlich_anspruchsberechtigt:
        out = xnp.minimum(out, langjährig__altersgrenze)

    return out


@policy_function(
    start_date="2012-01-01",
    end_date="2017-12-31",
    leaf_name="altersgrenze",
)
def altersgrenze_mit_arbeitslosigkeit_frauen_besonders_langjährig(
    für_frauen__grundsätzlich_anspruchsberechtigt: bool,
    für_frauen__altersgrenze: float,
    wegen_arbeitslosigkeit__grundsätzlich_anspruchsberechtigt: bool,
    wegen_arbeitslosigkeit__altersgrenze: float,
    besonders_langjährig__grundsätzlich_anspruchsberechtigt: bool,
    besonders_langjährig__altersgrenze: float,
    langjährig__grundsätzlich_anspruchsberechtigt: bool,
    langjährig__altersgrenze: float,
    regelaltersrente__altersgrenze: float,
    xnp: ModuleType,
) -> float:
    """Full retirement age after eligibility checks, assuming eligibility for
    Regelaltersrente.

    Age at which pension can be claimed without deductions. This age is smaller or equal
    to the normal retirement age (FRA<=NRA) and depends on personal characteristics as
    gender, insurance duration, health/disability, employment status.

    Starting in 2012, the pension for the very long term insured (Altersrente für
    besonders langjährig Versicherte) is introduced. Policy becomes inactive in 2018
    because then all potential beneficiaries of the Rente wg. Arbeitslosigkeit and
    Rente für Frauen have reached the normal retirement age.
    """
    out = regelaltersrente__altersgrenze
    if für_frauen__grundsätzlich_anspruchsberechtigt:
        out = xnp.minimum(out, für_frauen__altersgrenze)
    if wegen_arbeitslosigkeit__grundsätzlich_anspruchsberechtigt:
        out = xnp.minimum(
            out,
            wegen_arbeitslosigkeit__altersgrenze,
        )
    if langjährig__grundsätzlich_anspruchsberechtigt:
        out = xnp.minimum(out, langjährig__altersgrenze)
    if besonders_langjährig__grundsätzlich_anspruchsberechtigt:
        out = xnp.minimum(
            out,
            besonders_langjährig__altersgrenze,
        )

    return out


@policy_function(
    start_date="2018-01-01",
    leaf_name="altersgrenze",
)
def altersgrenze_mit_besonders_langjährig_ohne_arbeitslosigkeit_frauen(
    besonders_langjährig__grundsätzlich_anspruchsberechtigt: bool,
    besonders_langjährig__altersgrenze: float,
    langjährig__grundsätzlich_anspruchsberechtigt: bool,
    langjährig__altersgrenze: float,
    regelaltersrente__altersgrenze: float,
    xnp: ModuleType,
) -> float:
    """Full retirement age after eligibility checks, assuming eligibility for
    Regelaltersrente.

    Age at which pension can be claimed without deductions. This age is smaller or equal
    to the normal retirement age (FRA<=NRA) and depends on personal characteristics as
    gender, insurance duration, health/disability, employment status.
    """
    out = regelaltersrente__altersgrenze
    if langjährig__grundsätzlich_anspruchsberechtigt:
        out = xnp.minimum(out, langjährig__altersgrenze)
    if besonders_langjährig__grundsätzlich_anspruchsberechtigt:
        out = xnp.minimum(
            out,
            besonders_langjährig__altersgrenze,
        )

    return out


@policy_function(
    end_date="2017-12-31",
    leaf_name="altersgrenze_vorzeitig",
)
def altersgrenze_vorzeitig_mit_arbeitslosigkeit_frauen(
    wegen_arbeitslosigkeit__grundsätzlich_anspruchsberechtigt: bool,
    wegen_arbeitslosigkeit__altersgrenze_vorzeitig: float,
    für_frauen__grundsätzlich_anspruchsberechtigt: bool,
    für_frauen__altersgrenze_vorzeitig: float,
    langjährig__grundsätzlich_anspruchsberechtigt: bool,
    langjährig__altersgrenze_vorzeitig: float,
    regelaltersrente__altersgrenze: float,
    xnp: ModuleType,
) -> float:
    """Earliest possible retirement age after checking for eligibility.

    Early retirement age depends on personal characteristics as gender, insurance
    duration, health/disability, employment status. Policy becomes inactive in 2018
    because then all potential beneficiaries of the Rente wg. Arbeitslosigkeit and Rente
    für Frauen have reached the normal retirement age.
    """
    frauen_vorzeitig = für_frauen__altersgrenze_vorzeitig

    arbeitsl_vorzeitig = wegen_arbeitslosigkeit__altersgrenze_vorzeitig

    langjährig_vorzeitig = langjährig__altersgrenze_vorzeitig

    out = regelaltersrente__altersgrenze

    if langjährig__grundsätzlich_anspruchsberechtigt:
        out = langjährig_vorzeitig
    if für_frauen__grundsätzlich_anspruchsberechtigt:
        out = xnp.minimum(out, frauen_vorzeitig)
    if wegen_arbeitslosigkeit__grundsätzlich_anspruchsberechtigt:
        out = xnp.minimum(out, arbeitsl_vorzeitig)

    return out


@policy_function(start_date="2018-01-01", leaf_name="altersgrenze_vorzeitig")
def altersgrenze_vorzeitig_ohne_arbeitslosigkeit_frauen(
    langjährig__grundsätzlich_anspruchsberechtigt: bool,
    langjährig__altersgrenze_vorzeitig: float,
    regelaltersrente__altersgrenze: float,
) -> float:
    """Earliest possible retirement age after checking for eligibility.

    Early retirement age depends on personal characteristics as gender, insurance
    duration, health/disability, employment status.
    """
    out = regelaltersrente__altersgrenze

    if langjährig__grundsätzlich_anspruchsberechtigt:
        out = langjährig__altersgrenze_vorzeitig
    else:
        out = regelaltersrente__altersgrenze

    return out


@policy_function(
    end_date="2017-12-31",
    leaf_name="vorzeitig_grundsätzlich_anspruchsberechtigt",
)
def vorzeitig_grundsätzlich_anspruchsberechtigt_mit_arbeitslosigkeit_frauen(
    für_frauen__grundsätzlich_anspruchsberechtigt: bool,
    langjährig__grundsätzlich_anspruchsberechtigt: bool,
    wegen_arbeitslosigkeit__grundsätzlich_anspruchsberechtigt: bool,
) -> bool:
    """Eligibility for some form ofearly retirement.

    Can only be claimed if eligible for "Rente für langjährig Versicherte" or "Rente für
    Frauen" or "Rente für Arbeitslose" (or -not yet implemented - for disabled). Policy
    becomes inactive in 2018 because then all potential beneficiaries of the Rente wg.
    Arbeitslosigkeit and Rente für Frauen have reached the normal retirement age.
    """
    return (
        für_frauen__grundsätzlich_anspruchsberechtigt
        or langjährig__grundsätzlich_anspruchsberechtigt
        or wegen_arbeitslosigkeit__grundsätzlich_anspruchsberechtigt
    )


@policy_function(
    start_date="2018-01-01",
    leaf_name="vorzeitig_grundsätzlich_anspruchsberechtigt",
)
def vorzeitig_grundsätzlich_anspruchsberechtigt_vorzeitig_ohne_arbeitslosigkeit_frauen(
    langjährig__grundsätzlich_anspruchsberechtigt: bool,
) -> bool:
    """Eligibility for early retirement.

    Can only be claimed if eligible for "Rente für langjährig Versicherte".
    """
    return langjährig__grundsätzlich_anspruchsberechtigt


@policy_function(end_date="2017-12-31", leaf_name="referenzalter_abschlag")
def referenzalter_abschlag_mit_arbeitslosigkeit_frauen(
    wegen_arbeitslosigkeit__grundsätzlich_anspruchsberechtigt: bool,
    wegen_arbeitslosigkeit__altersgrenze: float,
    für_frauen__grundsätzlich_anspruchsberechtigt: bool,
    für_frauen__altersgrenze: float,
    langjährig__grundsätzlich_anspruchsberechtigt: bool,
    langjährig__altersgrenze: float,
    regelaltersrente__altersgrenze: float,
    xnp: ModuleType,
) -> float:
    """Reference age for deduction calculation in case of early retirement
    (Zugangsfaktor).

    Normal retirement age if not eligible for early retirement. Policy becomes inactive
    in 2018 because then all potential beneficiaries of the Rente wg. Arbeitslosigkeit
    and Rente für Frauen have reached the normal retirement age.
    """
    if (
        langjährig__grundsätzlich_anspruchsberechtigt
        and für_frauen__grundsätzlich_anspruchsberechtigt
        and wegen_arbeitslosigkeit__grundsätzlich_anspruchsberechtigt
    ):
        out = xnp.min(
            xnp.asarray(
                [
                    für_frauen__altersgrenze,
                    langjährig__altersgrenze,
                    wegen_arbeitslosigkeit__altersgrenze,
                ]
            ),
        )
    elif (
        langjährig__grundsätzlich_anspruchsberechtigt
        and für_frauen__grundsätzlich_anspruchsberechtigt
    ):
        out = xnp.min(
            xnp.asarray(
                [
                    für_frauen__altersgrenze,
                    langjährig__altersgrenze,
                ]
            ),
        )
    elif (
        langjährig__grundsätzlich_anspruchsberechtigt
        and wegen_arbeitslosigkeit__grundsätzlich_anspruchsberechtigt
    ):
        out = xnp.min(
            xnp.asarray(
                [
                    langjährig__altersgrenze,
                    wegen_arbeitslosigkeit__altersgrenze,
                ]
            ),
        )
    elif langjährig__grundsätzlich_anspruchsberechtigt:
        out = langjährig__altersgrenze
    elif für_frauen__grundsätzlich_anspruchsberechtigt:
        out = für_frauen__altersgrenze
    elif wegen_arbeitslosigkeit__grundsätzlich_anspruchsberechtigt:
        out = wegen_arbeitslosigkeit__altersgrenze
    else:
        out = regelaltersrente__altersgrenze

    return out


@policy_function(start_date="2018-01-01", leaf_name="referenzalter_abschlag")
def referenzalter_abschlag_ohne_arbeitslosigkeit_frauen(
    langjährig__grundsätzlich_anspruchsberechtigt: bool,
    langjährig__altersgrenze: float,
    regelaltersrente__altersgrenze: float,
) -> float:
    """Reference age for deduction calculation in case of early retirement
    (Zugangsfaktor).

    Normal retirement age if not eligible for early retirement.
    """
    if langjährig__grundsätzlich_anspruchsberechtigt:
        out = langjährig__altersgrenze
    else:
        out = regelaltersrente__altersgrenze

    return out
