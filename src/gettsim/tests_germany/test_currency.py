"""GETTSIM's currency registration (GEP 10).

Importing ``gettsim`` registers the euro as the base currency and the
Deutsche Mark relative to it, plus the dated statutory-currency mapping that
tells the engine which currency each policy date computes in.
"""

from __future__ import annotations

import datetime

import pytest
from ttsim.tt.currencies import (
    base_currency,
    currency_conversion_factor,
    statutory_currency_for_date,
)

# Importing gettsim runs germany/__init__.py, which registers the currencies.
import gettsim  # noqa: F401

#: 1 euro = 1.95583 DM, fixed by the Euro-Einführungsgesetz.
DM_PER_EUR = 1.95583


def test_euro_is_the_base_currency():
    assert base_currency() == "EUR"


def test_deutsche_mark_converts_to_euro_at_the_statutory_rate():
    assert currency_conversion_factor("DM", "EUR") == pytest.approx(1 / DM_PER_EUR)


def test_euro_converts_to_deutsche_mark_at_the_statutory_rate():
    assert currency_conversion_factor("EUR", "DM") == pytest.approx(DM_PER_EUR)


@pytest.mark.parametrize(
    ("policy_date", "expected"),
    [
        (datetime.date(1984, 1, 1), "DM"),
        (datetime.date(2001, 12, 31), "DM"),
        (datetime.date(2002, 1, 1), "EUR"),
        (datetime.date(2025, 1, 1), "EUR"),
    ],
)
def test_statutory_currency_changes_over_to_the_euro_in_2002(policy_date, expected):
    assert statutory_currency_for_date(policy_date) == expected
