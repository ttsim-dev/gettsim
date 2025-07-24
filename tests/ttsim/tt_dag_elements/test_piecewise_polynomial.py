"""
Tests for `piecewise_polynomial`
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy
import pytest

if TYPE_CHECKING:
    from types import ModuleType


from ttsim.tt_dag_elements.piecewise_polynomial import (
    PiecewisePolynomialParamValue,
    get_piecewise_parameters,
    piecewise_polynomial,
)


@pytest.fixture
def parameters(xnp: ModuleType):
    return PiecewisePolynomialParamValue(
        thresholds=xnp.array([-xnp.inf, 9168.0, 14254.0, 55960.0, 265326.0, xnp.inf]),
        rates=xnp.array(
            [
                [
                    0.00000000e00,
                    1.40000000e-01,
                    2.39700000e-01,
                    4.20000000e-01,
                    4.50000000e-01,
                ],
                [
                    0.00000000e00,
                    9.80141565e-06,
                    2.16155949e-06,
                    0.00000000e00,
                    0.00000000e00,
                ],
            ],
        ),
        intercepts=xnp.array([0.0, 0.0, 965.5771, 14722.3012, 102656.0212]),
    )


def test_get_piecewise_parameters_all_intercepts_supplied(xnp: ModuleType):
    parameter_dict = {
        0: {
            "lower_threshold": "-inf",
            "upper_threshold": 2005,
            "rate_linear": 0,
            "intercept_at_lower_threshold": 0.27,
        },
        1: {
            "lower_threshold": 2005,
            "upper_threshold": 2021,
            "rate_linear": 0.02,
            "intercept_at_lower_threshold": 0.5,
        },
        2: {
            "lower_threshold": 2021,
            "upper_threshold": 2041,
            "rate_linear": 0.01,
            "intercept_at_lower_threshold": 0.8,
        },
        3: {
            "lower_threshold": 2041,
            "upper_threshold": "inf",
            "rate_linear": 0,
            "intercept_at_lower_threshold": 1,
        },
    }

    actual = get_piecewise_parameters(
        leaf_name="test",
        func_type="piecewise_linear",
        parameter_dict=parameter_dict,
        xnp=xnp,
    )
    expected = xnp.array([0.27, 0.5, 0.8, 1])

    numpy.testing.assert_allclose(actual.intercepts, expected, atol=1e-7)


def test_piecewise_polynomial(
    parameters: PiecewisePolynomialParamValue,
    xnp: ModuleType,
):
    x = xnp.array([-1_000, 1_000, 10_000, 30_000, 100_000, 1_000_000])
    expected = xnp.array([0.0, 0.0, 246.53, 10551.65, 66438.2, 866518.64])

    actual = piecewise_polynomial(
        x=x,
        parameters=parameters,
        rates_multiplier=2,
        xnp=xnp,
    )
    numpy.testing.assert_allclose(xnp.array(actual), expected, atol=0.01)
