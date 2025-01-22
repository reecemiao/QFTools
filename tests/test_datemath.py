from datetime import date

import pytest

from qftools.date.calendar import Calendar
from qftools.date.datemath import DateMath, _add_months, _add_years
from qftools.date.frequency import Frequency
from qftools.date.roll import RollType
from qftools.date.tenor import TenorUnit


@pytest.fixture
def calendar():
    """Create a test calendar with weekends and some holidays."""
    holidays = {
        date(2024, 1, 1),  # New Year's Day
        date(2024, 12, 25),  # Christmas
    }
    return Calendar('test', holidays)


def test_add_tenor_basic():
    """Test basic tenor addition without rolling."""
    base_date = date(2024, 1, 15)

    # Test different units
    assert DateMath.add_tenor(base_date, 1, TenorUnit.DAY) == date(2024, 1, 16)
    assert DateMath.add_tenor(base_date, 1, TenorUnit.WEEK) == date(2024, 1, 22)
    assert DateMath.add_tenor(base_date, 1, TenorUnit.MONTH) == date(2024, 2, 15)
    assert DateMath.add_tenor(base_date, 1, TenorUnit.YEAR) == date(2025, 1, 15)

    # Test negative amounts
    assert DateMath.add_tenor(base_date, -1, TenorUnit.MONTH) == date(2023, 12, 15)

    # Test zero amount
    assert DateMath.add_tenor(base_date, 0, TenorUnit.MONTH) == base_date


def test_add_tenor_with_roll(calendar):
    """Test tenor addition with rolling."""
    base_date = date(2024, 1, 6)  # Saturday

    result = DateMath.add_tenor(base_date, 1, TenorUnit.WEEK, roll_type=RollType.FOLLOWING, calendar=calendar)
    assert result == date(2024, 1, 15)  # Monday after next


def test_add_tenor_month_end():
    """Test tenor addition with month-end cases."""
    # January 31 + 1 month = February 29 (2024 is leap year)
    assert DateMath.add_tenor(date(2024, 1, 31), 1, TenorUnit.MONTH) == date(2024, 2, 29)

    # March 31 + 1 month = April 30
    assert DateMath.add_tenor(date(2024, 3, 31), 1, TenorUnit.MONTH) == date(2024, 4, 30)


def test_add_tenor_invalid():
    """Test invalid tenor addition cases."""
    with pytest.raises(ValueError, match='Invalid tenor unit'):
        DateMath.add_tenor(date(2024, 1, 1), 1, None)


def test_generate_dates_forward():
    """Test forward date generation."""
    start = date(2024, 1, 1)
    roll = date(2024, 1, 15)
    maturity = date(2024, 12, 15)

    dates = DateMath.generate_dates(start, roll, maturity, frequency=Frequency.QUARTERLY)

    expected = [
        date(2024, 1, 15),  # roll date
        date(2024, 4, 15),  # Q1
        date(2024, 7, 15),  # Q2
        date(2024, 10, 15),  # Q3
        date(2024, 12, 16),  # maturity with weekend roll
    ]

    assert dates == expected


def test_generate_dates_reverse():
    """Test reverse date generation."""
    start = date(2024, 1, 1)
    roll = date(2024, 1, 15)
    maturity = date(2024, 12, 15)

    dates = DateMath.generate_dates(start, roll, maturity, frequency=Frequency.QUARTERLY, reverse=True)

    expected = [
        date(2024, 1, 15),  # roll date
        date(2024, 3, 15),  # maturity - Q3
        date(2024, 6, 17),  # maturity - Q2
        date(2024, 9, 16),  # maturity - Q1
        date(2024, 12, 16),  # maturity with weekend roll
    ]

    assert dates == expected


def test_generate_dates_invalid():
    """Test invalid date generation cases."""
    with pytest.raises(ValueError, match='Dates must be in order'):
        DateMath.generate_dates(
            date(2024, 2, 1),  # start after roll
            date(2024, 1, 1),
            date(2024, 12, 1),
        )


def test_helper_functions():
    """Test date math helper functions."""
    base_date = date(2024, 1, 31)

    # Test month addition
    assert _add_months(base_date, 1) == date(2024, 2, 29)  # leap year
    assert _add_months(base_date, 2) == date(2024, 3, 31)
    assert _add_months(base_date, -1) == date(2023, 12, 31)

    # Test year addition
    assert _add_years(base_date, 1) == date(2025, 1, 31)
    assert _add_years(date(2024, 2, 29), 1) == date(2025, 2, 28)  # non-leap year
    assert _add_years(base_date, -1) == date(2023, 1, 31)


def test_generate_dates_invalid_frequencies():
    """Test date generation with invalid frequencies."""
    start = date(2024, 1, 1)
    roll = date(2024, 1, 15)
    maturity = date(2024, 12, 31)

    invalid_frequencies = [Frequency.ONCE, Frequency.CONTINUOUS, Frequency.OTHER]
    error_msg = 'Frequency must not be ONCE, CONTINUOUS, or OTHER for date generation'

    for freq in invalid_frequencies:
        with pytest.raises(ValueError, match=error_msg):
            DateMath.generate_dates(start, roll, maturity, frequency=freq)
