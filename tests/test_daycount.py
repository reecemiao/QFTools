from datetime import date

import pytest

from qftools.date.calendar import Calendar
from qftools.date.daycount import DayCountBasis, calculate


@pytest.fixture
def calendar():
    """Sample calendar for testing."""
    return Calendar('Test Calendar', [date(2024, 1, 1)])


def test_act_360():
    """Test Actual/360 day count."""
    start = date(2024, 1, 1)
    end = date(2024, 2, 1)
    result = calculate(DayCountBasis.ACT_360, start, end)
    assert result == pytest.approx(31 / 360)


def test_thirty_360():
    """Test 30/360 day count."""
    start = date(2024, 1, 30)
    end = date(2024, 2, 28)
    result = calculate(DayCountBasis.THIRTY_360, start, end)
    assert result == pytest.approx(28 / 360)


def test_business_252(calendar):
    """Test Business/252 day count."""
    start = date(2024, 1, 1)
    end = date(2024, 1, 5)
    result = calculate(DayCountBasis.BUSINESS_252, start, end, calendar=calendar)
    assert result == pytest.approx(4 / 252)  # Assuming 4 business days


def test_invalid_dates():
    """Test day count calculation with invalid dates."""
    start = date(2024, 2, 1)
    end = date(2024, 1, 1)

    with pytest.raises(ValueError, match='End date must not be before start date'):
        calculate(DayCountBasis.ACT_360, start, end)


def test_act_365():
    """Test Actual/365 day count."""
    start = date(2024, 1, 1)
    end = date(2025, 1, 1)
    result = calculate(DayCountBasis.ACT_365, start, end)
    assert result == pytest.approx(366 / 365)  # 2024 is a leap year


def test_act_act():
    """Test Actual/Actual day count."""
    # Test within same year
    start = date(2024, 1, 1)
    end = date(2025, 1, 1)
    result = calculate(DayCountBasis.ACT_ACT, start, end)
    assert result == pytest.approx(366 / 366)  # 2024 is a leap year

    # Test across years
    start = date(2024, 7, 1)
    end = date(2025, 7, 1)
    result = calculate(DayCountBasis.ACT_ACT, start, end)
    expected = 184 / 366 + 181 / 365  # First half in leap year, second in normal year
    assert result == pytest.approx(expected)


def test_thirty_360_e():
    """Test 30E/360 (Eurobond) day count."""
    start = date(2024, 1, 30)
    end = date(2024, 2, 28)
    result = calculate(DayCountBasis.THIRTY_360_E, start, end)
    assert result == pytest.approx(28 / 360)  # Both dates are adjusted to 30th
