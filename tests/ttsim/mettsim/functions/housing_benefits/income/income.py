from ttsim import policy_function
from ttsim.rounding import RoundingDirection, RoundingSpec


@policy_function(rounding_spec=RoundingSpec(base=1, direction=RoundingDirection.DOWN))
def amount_m(
    gross_wage_m: float,
    payroll_tax__amount_m: float,
) -> float:
    return gross_wage_m - payroll_tax__amount_m
