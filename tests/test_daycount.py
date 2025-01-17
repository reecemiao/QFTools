from datetime import date

import pytest

from qftools.date.calendar import Calendar
from qftools.date.daycount import DayCount
from qftools.date.frequency import Frequency


@pytest.fixture
def calendar():
    """Sample calendar for testing."""
    return Calendar('Test Calendar', [date(2024, 1, 1)])


def test_act_360():
    """Test Actual/360 day count."""
    start = date(2024, 1, 1)
    end = date(2024, 2, 1)
    result = DayCount.ACT_360.fraction(start, end)
    assert result == pytest.approx(31 / 360)


def test_act_365():
    """Test Actual/365 day count."""
    start = date(2024, 1, 1)
    end = date(2025, 1, 1)
    result = DayCount.ACT_365.fraction(start, end)
    assert result == pytest.approx(366 / 365)  # 2024 is a leap year


def test_act_365_nl():
    """Test Actual/365 No Leap day count."""
    # Test period including Feb 29
    start = date(2024, 2, 28)
    end = date(2024, 3, 1)
    result = DayCount.ACT_365_NL.fraction(start, end)
    assert result == pytest.approx(1 / 365)  # Feb 29 is excluded

    # Test normal period
    start = date(2024, 1, 1)
    end = date(2024, 2, 1)
    result = DayCount.ACT_365_NL.fraction(start, end)
    assert result == pytest.approx(31 / 365)


def test_act_act():
    """Test Actual/Actual day count."""
    # Test within same year
    start = date(2024, 1, 1)
    end = date(2025, 1, 1)
    result = DayCount.ACT_ACT.fraction(start, end)
    assert result == pytest.approx(1.0)  # Full year

    # Test across years
    start = date(2024, 7, 1)
    end = date(2025, 7, 1)
    result = DayCount.ACT_ACT.fraction(start, end)
    expected = 184 / 366 + 181 / 365  # First half in leap year, second in normal year
    assert result == pytest.approx(expected)


def test_act_act_afb():
    """Test Actual/Actual AFB day count."""
    # Test period within one year
    start = date(2024, 1, 1)
    end = date(2025, 1, 1)
    result = DayCount.ACT_ACT_AFB.fraction(start, end)
    assert result == pytest.approx(366 / 366)  # 2024 is leap year


def test_thirty_360():
    """Test 30/360 day count."""
    # Test normal case
    start = date(2024, 1, 30)
    end = date(2024, 2, 28)
    result = DayCount.THIRTY_360.fraction(start, end)
    assert result == pytest.approx(28 / 360)

    # Test end of month case
    start = date(2024, 1, 31)
    end = date(2024, 3, 31)
    result = DayCount.THIRTY_360.fraction(start, end)
    assert result == pytest.approx(60 / 360)


def test_thirty_360_e():
    """Test 30E/360 (Eurobond) day count."""
    start = date(2024, 1, 31)
    end = date(2024, 3, 31)
    result = DayCount.THIRTY_360_E.fraction(start, end)
    assert result == pytest.approx(60 / 360)  # Both dates are adjusted to 30th


def test_thirty_360_isda():
    """Test 30E/360 ISDA day count."""
    start = date(2024, 2, 29)  # Last day of February in leap year
    end = date(2025, 2, 28)  # Last day of February in normal year
    maturity = date(2026, 2, 28)
    result = DayCount.THIRTY_360_ISDA.fraction(start, end, maturity=maturity)
    assert result == pytest.approx(361 / 360)  # One year exactly


def test_thirty_360_us():
    """Test 30/360 US day count."""
    start = date(2024, 2, 29)
    end = date(2025, 2, 28)
    result = DayCount.THIRTY_360_US.fraction(start, end)
    assert result == pytest.approx(360 / 360)


def test_business_252(calendar):
    """Test Business/252 day count."""
    start = date(2024, 1, 1)
    end = date(2024, 1, 5)
    result = DayCount.BUSINESS_252.fraction(start, end, calendar=calendar)
    assert result == pytest.approx(4 / 252)  # Assuming 4 business days


def test_invalid_dates():
    """Test day count calculation with invalid dates."""
    start = date(2024, 2, 1)
    end = date(2024, 1, 1)

    with pytest.raises(ValueError, match='End date must not be before start date'):
        DayCount.ACT_360.fraction(start, end)


def test_missing_calendar():
    """Test Business/252 without calendar."""
    start = date(2024, 1, 1)
    end = date(2024, 1, 5)

    with pytest.raises(ValueError, match='Calendar required for Business/252 calculations'):
        DayCount.BUSINESS_252.fraction(start, end)


def test_missing_maturity():
    """Test 30E/360 ISDA without maturity date."""
    start = date(2024, 1, 1)
    end = date(2024, 12, 31)

    with pytest.raises(ValueError, match='Maturity date required for 30E/360 ISDA calculations'):
        DayCount.THIRTY_360_ISDA.fraction(start, end)


def test_act_act_icma():
    """Test Actual/Actual ICMA day count."""
    # Test regular period
    start = date(2024, 1, 1)
    end = date(2024, 7, 1)
    payment = date(2024, 7, 1)
    maturity = date(2026, 7, 1)
    result = DayCount.ACT_ACT_ICMA.fraction(
        start, end, maturity=maturity, payment=payment, frequency=Frequency.SEMIANNUAL
    )
    assert result == pytest.approx(0.5)  # Half year period

    # Test non-aligned period
    start = date(2024, 1, 15)
    end = date(2024, 6, 15)
    payment = date(2024, 7, 15)
    result = DayCount.ACT_ACT_ICMA.fraction(
        start, end, maturity=maturity, payment=payment, frequency=Frequency.SEMIANNUAL
    )
    assert result == pytest.approx(0.417582417582)

    # Test ultimo dates
    start = date(2024, 1, 31)
    end = date(2024, 7, 31)
    payment = date(2024, 7, 31)
    result = DayCount.ACT_ACT_ICMA.fraction(
        start, end, maturity=maturity, payment=payment, frequency=Frequency.SEMIANNUAL
    )
    assert result == pytest.approx(0.5)


def test_act_365_icma():
    """Test Actual/365 ICMA day count."""
    # Test regular period
    start = date(2024, 1, 1)
    end = date(2024, 7, 1)
    payment = date(2024, 7, 1)
    maturity = date(2026, 7, 1)
    result = DayCount.ACT_365_ICMA.fraction(
        start, end, maturity=maturity, payment=payment, frequency=Frequency.SEMIANNUAL
    )
    assert result == pytest.approx(182 / 365)  # Days in period / 365

    # Test period exceeding standard length
    start = date(2024, 1, 1)
    end = date(2024, 7, 15)  # 15 days more than standard period
    payment = date(2024, 7, 1)
    result = DayCount.ACT_365_ICMA.fraction(
        start, end, maturity=maturity, payment=payment, frequency=Frequency.SEMIANNUAL
    )
    assert result == pytest.approx(0.5 - 1 / 365)  # Special case handling


def test_icma_validation():
    """Test validation for ICMA calculations."""
    start = date(2024, 1, 1)
    end = date(2024, 7, 1)

    # Test missing maturity
    with pytest.raises(ValueError, match='Maturity, payment dates and frequency required for ACT/ACT ICMA'):
        DayCount.ACT_ACT_ICMA.fraction(start, end, payment=end, frequency=Frequency.SEMIANNUAL)

    # Test missing payment
    with pytest.raises(ValueError, match='Maturity, payment dates and frequency required for ACT/ACT ICMA'):
        DayCount.ACT_ACT_ICMA.fraction(start, end, maturity=end, frequency=Frequency.SEMIANNUAL)

    # Test missing frequency
    with pytest.raises(ValueError, match='Maturity, payment dates and frequency required for ACT/ACT ICMA'):
        DayCount.ACT_ACT_ICMA.fraction(start, end, maturity=end, payment=end)

    # Test ACT/365 ICMA validation
    with pytest.raises(ValueError, match='Maturity, payment dates and frequency required for ACT/365 ICMA'):
        DayCount.ACT_365_ICMA.fraction(start, end, maturity=end, payment=end)


def test_act_act_icma_edge_cases():
    """Test ACT/ACT ICMA edge cases."""
    start = date(2024, 2, 29)  # Leap year
    end = date(2024, 8, 31)  # End of month
    payment = date(2024, 8, 31)
    maturity = date(2026, 8, 31)

    result = DayCount.ACT_ACT_ICMA.fraction(
        start, end, maturity=maturity, payment=payment, frequency=Frequency.SEMIANNUAL
    )
    assert result == pytest.approx(0.5)


def test_act_365_icma_leap_year():
    """Test ACT/365 ICMA in leap year."""
    start = date(2024, 2, 29)
    end = date(2024, 8, 29)
    payment = date(2024, 8, 29)
    maturity = date(2026, 8, 29)

    result = DayCount.ACT_365_ICMA.fraction(
        start, end, maturity=maturity, payment=payment, frequency=Frequency.SEMIANNUAL
    )
    assert result == pytest.approx(182 / 365)


def test_frequency_validation():
    """Test frequency validation in ICMA calculations."""
    start = date(2024, 1, 1)
    end = date(2024, 7, 1)
    payment = date(2024, 7, 1)
    maturity = date(2026, 7, 1)

    with pytest.raises(ValueError):
        DayCount.ACT_ACT_ICMA.fraction(start, end, maturity=maturity, payment=payment, frequency=Frequency.OTHER)


def test_act_365_icma_with_frequencies():
    """Test ACT/365 ICMA with different frequencies."""
    start = date(2024, 1, 1)
    end = date(2024, 12, 31)
    maturity = date(2026, 12, 31)

    test_cases = [
        (Frequency.ANNUAL, date(2024, 12, 31), 1.0),
        (Frequency.SEMIANNUAL, date(2024, 6, 30), 0.4958904109589),
        (Frequency.QUARTERLY, date(2024, 3, 31), 0.2465753424657),
        (Frequency.MONTHLY, date(2024, 1, 31), 0.0821917808219),
    ]

    for freq, payment, expected in test_cases:
        result = DayCount.ACT_365_ICMA.fraction(start, end, maturity=maturity, payment=payment, frequency=freq)
        assert result == pytest.approx(expected, rel=1e-10), f'Failed for frequency {freq}'


def test_act_act_icma_with_frequencies():
    """Test ACT/ACT ICMA with different frequencies."""
    start = date(2024, 1, 1)  # Leap year
    end = date(2024, 12, 31)
    maturity = date(2026, 12, 31)

    test_cases = [
        (Frequency.ANNUAL, date(2024, 12, 31), -0.9972677595628),
        (Frequency.SEMIANNUAL, date(2024, 6, 30), -0.49453551912568),
        (Frequency.QUARTERLY, date(2024, 3, 31), -0.24725274725275),
        (Frequency.MONTHLY, date(2024, 1, 31), -0.08064516129032),
    ]

    for freq, payment, expected in test_cases:
        result = DayCount.ACT_ACT_ICMA.fraction(start, end, maturity=maturity, payment=payment, frequency=freq)
        assert result == pytest.approx(expected, rel=1e-10), f'Failed for frequency {freq}'


def test_icma_invalid_frequencies():
    """Test ICMA calculations with invalid frequencies."""
    start = date(2024, 1, 1)
    end = date(2024, 12, 31)
    maturity = date(2026, 12, 31)
    payment = date(2024, 12, 31)

    invalid_frequencies = [
        Frequency.ONCE,
        Frequency.BIWEEKLY,
        Frequency.WEEKLY,
        Frequency.DAILY,
        Frequency.CONTINUOUS,
        Frequency.OTHER,
    ]

    for freq in invalid_frequencies:
        with pytest.raises(ValueError, match='Frequency must not be'):
            DayCount.ACT_ACT_ICMA.fraction(start, end, maturity=maturity, payment=payment, frequency=freq)
        with pytest.raises(ValueError, match='Frequency must not be'):
            DayCount.ACT_365_ICMA.fraction(start, end, maturity=maturity, payment=payment, frequency=freq)
