"""Contribution rate for health insurance."""

from __future__ import annotations

from gettsim.tt import param_function, policy_function


@param_function(end_date="2005-06-30")
def beitragssatz_arbeitnehmer(beitragssatz: float) -> float:
    """Employee's health insurance contribution rate until June 2005.

    Basic split between employees and employers.
    """
    return beitragssatz / 2


@param_function(end_date="2005-12-31")
def beitragssatz_arbeitnehmer_midijob(beitragssatz_jahresanfang: float) -> float:
    """Employee's health insurance contribution rate for the beginning of the year until
    June 2005.

    Basic split between employees and employers.
    """
    return beitragssatz_jahresanfang / 2


@policy_function(
    start_date="2005-07-01",
    end_date="2008-12-31",
    leaf_name="beitragssatz_arbeitnehmer",
)
def beitragssatz_arbeitnehmer_voller_zusatzbeitrag_ab_07_2005_bis_2008(
    zusatzbeitragssatz: float,
    parameter_beitragssatz: dict[str, float],
) -> float:
    """Employee's health insurance contribution rate.

    From July 2005 the contribution rates consists of a general rate (split equally
    between employers and employees, differs across sickness funds) and a top-up rate,
    which is fully paid by employees.
    """
    return parameter_beitragssatz["mean_allgemein"] / 2 + zusatzbeitragssatz


@param_function(
    start_date="2006-01-01",
    end_date="2008-12-31",
    leaf_name="beitragssatz_arbeitnehmer_midijob",
)
def beitragssatz_arbeitnehmer_midijob_voller_zusatzbeitrag_ab_2006_bis_2008(
    parameter_beitragssatz_jahresanfang: dict[str, float],
) -> float:
    """Employee's health insurance contribution rate at the beginning of the year.

    Starting in 2006, the "Jahresanfang" contribution rate includes the Sonderbeitrag.
    """
    return (
        parameter_beitragssatz_jahresanfang["mean_allgemein"] / 2
        + parameter_beitragssatz_jahresanfang["sonderbeitrag"]
    )


@policy_function(
    start_date="2009-01-01",
    end_date="2018-12-31",
    leaf_name="beitragssatz_arbeitnehmer",
)
def beitragssatz_arbeitnehmer_voller_zusatzbeitrag_ab_2009_bis_2018(
    zusatzbeitragssatz: float,
    parameter_beitragssatz: dict[str, float],
) -> float:
    """Employee's health insurance contribution rate.

    From July 2005 the contribution rates consists of a general rate (split equally
    between employers and employees, differs across sickness funds) and a top-up rate,
    which is fully paid by employees.
    """
    return parameter_beitragssatz["allgemein"] / 2 + zusatzbeitragssatz


@param_function(
    start_date="2009-01-01",
    end_date="2014-12-31",
    leaf_name="beitragssatz_arbeitnehmer_midijob",
)
def beitragssatz_arbeitnehmer_midijob_voller_sonderbeitragssatz(
    parameter_beitragssatz_jahresanfang: dict[str, float],
) -> float:
    """Employee's health insurance contribution rate at the beginning of the year.

    From July 2005 the contribution rates consists of a general rate (split equally
    between employers and employees, differs across sickness funds) and a top-up rate,
    which is fully paid by employees.
    """
    return (
        parameter_beitragssatz_jahresanfang["allgemein"] / 2
        + parameter_beitragssatz_jahresanfang["sonderbeitrag"]
    )


@param_function(
    start_date="2015-01-01",
    end_date="2018-12-31",
    leaf_name="beitragssatz_arbeitnehmer_midijob",
)
def beitragssatz_arbeitnehmer_midijob_voller_zusatzbeitragssatz(
    parameter_beitragssatz_jahresanfang: dict[str, float],
) -> float:
    """Employee's health insurance contribution rate at the beginning of the year.

    From July 2005 the contribution rates consists of a general rate (split equally
    between employers and employees, differs across sickness funds) and a top-up rate,
    which is fully paid by employees.
    """
    return (
        parameter_beitragssatz_jahresanfang["allgemein"] / 2
        + parameter_beitragssatz_jahresanfang["mean_zusatzbeitrag"]
    )


@policy_function(
    start_date="2019-01-01",
    leaf_name="beitragssatz_arbeitnehmer",
)
def beitragssatz_arbeitnehmer_paritätischer_zusatzbeitrag(
    zusatzbeitragssatz: float,
    parameter_beitragssatz: dict[str, float],
) -> float:
    """Employee's health insurance contribution rate.

    Since 2019. Zusatzbeitrag is split equally between employers and employees.
    """
    return (parameter_beitragssatz["allgemein"] + zusatzbeitragssatz) / 2


@param_function(
    start_date="2019-01-01",
    leaf_name="beitragssatz_arbeitnehmer_midijob",
)
def beitragssatz_arbeitnehmer_midijob_paritätischer_zusatzbeitrag(
    parameter_beitragssatz_jahresanfang: dict[str, float],
) -> float:
    """Employee's health insurance contribution rate at the beginning of the year.

    Zusatzbeitrag is split equally between employers and employees.
    """
    return (
        parameter_beitragssatz_jahresanfang["allgemein"]
        + parameter_beitragssatz_jahresanfang["mean_zusatzbeitrag"]
    ) / 2


@param_function(
    end_date="2005-06-30",
    leaf_name="beitragssatz_arbeitgeber",
)
def beitragssatz_arbeitgeber_bis_06_2005(beitragssatz: float) -> float:
    """Employer's health insurance contribution rate."""
    return beitragssatz / 2


@param_function(
    end_date="2005-12-31",
    leaf_name="beitragssatz_arbeitgeber_midijob",
)
def beitragssatz_arbeitgeber_midijob_bis_06_2005(
    beitragssatz_jahresanfang: float,
) -> float:
    """Employer's health insurance contribution rate at the beginning of the year."""
    return beitragssatz_jahresanfang / 2


@param_function(
    start_date="2005-07-01",
    end_date="2008-12-31",
    leaf_name="beitragssatz_arbeitgeber",
)
def beitragssatz_arbeitgeber_ohne_zusatzbeitrag_ab_07_2005_bis_2008(
    parameter_beitragssatz: dict[str, float],
) -> float:
    """Employer's health insurance contribution rate."""
    return parameter_beitragssatz["mean_allgemein"] / 2


@param_function(
    start_date="2006-01-01",
    end_date="2008-12-31",
    leaf_name="beitragssatz_arbeitgeber_midijob",
)
def beitragssatz_arbeitgeber_midijob_ohne_zusatzbeitrag_ab_06_2006_bis_2008(
    parameter_beitragssatz_jahresanfang: dict[str, float],
) -> float:
    """Employer's health insurance contribution rate at the begging of the year."""
    return parameter_beitragssatz_jahresanfang["mean_allgemein"] / 2


@param_function(
    start_date="2009-01-01",
    end_date="2018-12-31",
    leaf_name="beitragssatz_arbeitgeber",
)
def beitragssatz_arbeitgeber_ohne_zusatzbeitrag_ab_09_2009_bis_2018(
    parameter_beitragssatz: dict[str, float],
) -> float:
    """Employer's health insurance contribution rate."""
    return parameter_beitragssatz["allgemein"] / 2


@param_function(
    start_date="2009-01-01",
    end_date="2018-12-31",
    leaf_name="beitragssatz_arbeitgeber_midijob",
)
def beitragssatz_arbeitgeber_midijob_ohne_zusatzbeitrag_ab_09_2009_bis_2018(
    parameter_beitragssatz_jahresanfang: dict[str, float],
) -> float:
    """Employer's health insurance contribution rate at the beginning of the year."""
    return parameter_beitragssatz_jahresanfang["allgemein"] / 2


@policy_function(
    start_date="2019-01-01",
    leaf_name="beitragssatz_arbeitgeber",
)
def beitragssatz_arbeitgeber_paritätischer_zusatzbeitrag(
    beitragssatz_arbeitnehmer: float,
) -> float:
    """Employer's health insurance contribution rate.

    Since 2019, the full contribution rate is now split equally between employers and
    employees.
    """
    return beitragssatz_arbeitnehmer


@param_function(
    start_date="2019-01-01",
    leaf_name="beitragssatz_arbeitgeber_midijob",
)
def beitragssatz_arbeitgeber_midijob_paritätischer_zusatzbeitrag(
    beitragssatz_arbeitnehmer_midijob: float,
) -> float:
    """Employer's health insurance contribution rate at the beginning of the year.

    Since 2019, the full contribution rate is now split equally between employers and
    employees.
    """
    return beitragssatz_arbeitnehmer_midijob


@param_function(
    start_date="2005-07-01",
    end_date="2014-12-31",
    leaf_name="zusatzbeitragssatz",
)
def zusatzbeitragssatz_genannt_sonderbeitrag(
    parameter_beitragssatz: dict[str, float],
) -> float:
    """Health insurance top-up (Zusatzbeitrag) rate until December 2014.

    Overwrite this in order to use an individual-specific Zusatzbeitragssatz.
    """
    return parameter_beitragssatz["sonderbeitrag"]


@param_function(start_date="2015-01-01")
def zusatzbeitragssatz(
    parameter_beitragssatz: dict[str, float],
) -> float:
    """Health insurance top-up rate (Zusatzbeitrag) since January 2015.

    Most datasets will not contain information about the individual-specific
    Zusatzbeitrag. This function returns the mean Zusatzbeitrag of the specific policy
    date. Overwrite this function in order to use an individual-specific
    Zusatzbeitragssatz.
    """
    return parameter_beitragssatz["mean_zusatzbeitrag"]
