from datetime import date

import pytest

from qftools.date.calendar import Calendar
from qftools.date.daycount import DayCount
from qftools.date.frequency import Frequency


@pytest.fixture
def calendar():
    """Sample calendar for testing."""
    return Calendar('Test Calendar', [date(2024, 1, 1), date(2024, 12, 25)])


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


def test_thirty_360_month_end():
    """Test month-end handling in 30/360 conventions."""
    test_cases = [
        # Start and end on month ends
        (
            date(2024, 1, 31),
            date(2024, 2, 29),
            {
                DayCount.THIRTY_360: 29 / 360,  # 31->30, 29->29
                DayCount.THIRTY_360_E: 29 / 360,  # 31->30, 29->29
                DayCount.THIRTY_360_ISDA: 30 / 360,  # 31->30, 29->30
                DayCount.THIRTY_360_US: 29 / 360,  # 31->30, 29->29
            },
        ),
        # Start on month end, end mid-month
        (
            date(2024, 1, 31),
            date(2024, 2, 15),
            {
                DayCount.THIRTY_360: 15 / 360,  # 31->30, 15->15
                DayCount.THIRTY_360_E: 15 / 360,  # 31->30, 15->15
                DayCount.THIRTY_360_ISDA: 15 / 360,  # 31->30, 15->15
                DayCount.THIRTY_360_US: 15 / 360,  # 31->30, 15->15
            },
        ),
        # Start mid-month, end on month end
        (
            date(2024, 1, 15),
            date(2024, 2, 29),
            {
                DayCount.THIRTY_360: 44 / 360,  # 15->15, 29->29
                DayCount.THIRTY_360_E: 44 / 360,  # 15->15, 29->29
                DayCount.THIRTY_360_ISDA: 45 / 360,  # 15->15, 29->30
                DayCount.THIRTY_360_US: 44 / 360,  # 15->15, 29->29
            },
        ),
        # February to February (leap year to non-leap year)
        (
            date(2024, 2, 29),
            date(2025, 2, 28),
            {
                DayCount.THIRTY_360: 359 / 360,  # 29->29, 28->28
                DayCount.THIRTY_360_E: 359 / 360,  # 29->29, 28->28
                DayCount.THIRTY_360_ISDA: 361 / 360,  # 29->29, 28->30
                DayCount.THIRTY_360_US: 360 / 360,  # Feb end special case
            },
        ),
    ]

    for start, end, expected_results in test_cases:
        for convention, expected in expected_results.items():
            maturity = date(2026, 12, 31)  # Far future maturity for ISDA
            result = convention.fraction(start, end, maturity=maturity)
            assert result == pytest.approx(expected), f'Failed for {convention} from {start} to {end}'


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
    assert result == pytest.approx(0.4175824175824176)

    # Test ultimo dates
    start = date(2024, 1, 31)
    end = date(2024, 7, 31)
    payment = date(2024, 7, 31)
    result = DayCount.ACT_ACT_ICMA.fraction(
        start, end, maturity=maturity, payment=payment, frequency=Frequency.SEMIANNUAL
    )
    assert result == pytest.approx(0.5)


def test_act_act_icma_with_aligned_frequencies():
    """Test ACT/ACT ICMA with different frequencies."""
    start = date(2024, 1, 1)  # Leap year
    maturity = date(2026, 1, 1)

    test_cases = [
        (Frequency.ANNUAL, date(2024, 12, 1), date(2025, 1, 1), 0.9153005464480874),
        (Frequency.SEMIANNUAL, date(2024, 6, 1), date(2024, 7, 1), 0.4175824175824176),
        (Frequency.QUARTERLY, date(2024, 3, 1), date(2024, 4, 1), 0.16483516483516483),
        (Frequency.MONTHLY, date(2024, 1, 15), date(2024, 2, 1), 0.03763440860215054),
    ]

    for freq, end, payment, expected in test_cases:
        result = DayCount.ACT_ACT_ICMA.fraction(start, end, maturity=maturity, payment=payment, frequency=freq)
        assert result == pytest.approx(expected, rel=1e-10), f'Failed for frequency {freq}'


def test_act_act_icma_with_long_stub():
    """Test ACT/ACT ICMA with long stub period."""
    start = date(2024, 1, 1)  # Leap year
    maturity = date(2026, 1, 1)

    test_cases = [
        (Frequency.ANNUAL, date(2025, 1, 15), date(2025, 2, 1), 1.0384834194176211),
        (Frequency.SEMIANNUAL, date(2024, 7, 15), date(2024, 8, 1), 0.537535833731486),
        (Frequency.QUARTERLY, date(2024, 4, 15), date(2024, 5, 1), 0.28979468599033814),
        (Frequency.MONTHLY, date(2024, 2, 15), date(2024, 3, 1), 0.1235632183908046),
    ]

    for freq, end, payment, expected in test_cases:
        result = DayCount.ACT_ACT_ICMA.fraction(start, end, maturity=maturity, payment=payment, frequency=freq)
        assert result == pytest.approx(expected, rel=1e-10), f'Failed for frequency {freq}'


def test_act_act_icma_with_long_stub_maturity():
    """Test ACT/ACT ICMA with long stub period, maturity is payment."""
    start = date(2024, 1, 1)  # Leap year

    test_cases = [
        (Frequency.ANNUAL, date(2025, 1, 15), date(2025, 2, 1), 1.0383561643835617),
        (Frequency.SEMIANNUAL, date(2024, 7, 15), date(2024, 8, 1), 0.5380434782608696),
        (Frequency.QUARTERLY, date(2024, 4, 15), date(2024, 5, 1), 0.28846153846153844),
        (Frequency.MONTHLY, date(2024, 2, 15), date(2024, 3, 1), 0.1235632183908046),
    ]

    for freq, end, payment, expected in test_cases:
        result = DayCount.ACT_ACT_ICMA.fraction(start, end, maturity=payment, payment=payment, frequency=freq)
        assert result == pytest.approx(expected, rel=1e-10), f'Failed for frequency {freq}'


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
    start = date(2024, 3, 1)
    end = date(2024, 8, 31)
    payment = date(2024, 9, 1)  # 15 days more than standard period
    result = DayCount.ACT_365_ICMA.fraction(
        start, end, maturity=maturity, payment=payment, frequency=Frequency.SEMIANNUAL
    )
    assert result == pytest.approx(0.5 - 1 / 365)  # Special case handling


def test_act_365_icma_with_aligned_frequencies():
    """Test ACT/365 ICMA with different frequencies."""
    start = date(2024, 1, 1)
    maturity = date(2025, 1, 1)

    test_cases = [
        (Frequency.ANNUAL, date(2024, 12, 1), date(2025, 1, 1), 0.9178082191780822),
        (Frequency.SEMIANNUAL, date(2024, 6, 1), date(2024, 7, 1), 0.41643835616438357),
        (Frequency.QUARTERLY, date(2024, 3, 1), date(2024, 4, 1), 0.1643835616438356),
        (Frequency.MONTHLY, date(2024, 1, 15), date(2024, 2, 1), 0.038356164383561646),
    ]

    for freq, end, payment, expected in test_cases:
        result = DayCount.ACT_365_ICMA.fraction(start, end, maturity=maturity, payment=payment, frequency=freq)
        assert result == pytest.approx(expected, rel=1e-10), f'Failed for frequency {freq}'


def test_act_365_icma_with_long_stub():
    """Test ACT/365 ICMA with long stub period."""
    start = date(2024, 1, 1)  # Leap year
    maturity = date(2026, 1, 1)

    test_cases = [
        (Frequency.ANNUAL, date(2025, 1, 15), date(2025, 2, 1), 1.0410958904109588),
        (Frequency.SEMIANNUAL, date(2024, 7, 15), date(2024, 8, 1), 0.536986301369863),
        (Frequency.QUARTERLY, date(2024, 4, 15), date(2024, 5, 1), 0.2876712328767123),
        (Frequency.MONTHLY, date(2024, 2, 15), date(2024, 3, 1), 0.12168949771689497),
    ]

    for freq, end, payment, expected in test_cases:
        result = DayCount.ACT_365_ICMA.fraction(start, end, maturity=maturity, payment=payment, frequency=freq)
        assert result == pytest.approx(expected, rel=1e-10), f'Failed for frequency {freq}'


def test_act_365_icma_with_long_stub_maturity():
    """Test ACT/365 ICMA with long stub period, maturity is payment."""
    start = date(2024, 1, 1)  # Leap year

    test_cases = [
        (Frequency.ANNUAL, date(2025, 1, 15), date(2025, 2, 1), 1.0383561643836),
        (Frequency.SEMIANNUAL, date(2024, 7, 15), date(2024, 8, 1), 0.5383561643835616),
        (Frequency.QUARTERLY, date(2024, 4, 15), date(2024, 5, 1), 0.28835616438356165),
        (Frequency.MONTHLY, date(2024, 2, 15), date(2024, 3, 1), 0.12168949771689497),
    ]

    for freq, end, payment, expected in test_cases:
        result = DayCount.ACT_365_ICMA.fraction(start, end, maturity=payment, payment=payment, frequency=freq)
        assert result == pytest.approx(expected, rel=1e-10), f'Failed for frequency {freq}'


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


def test_leap_year_handling():
    """Test day count handling across leap years."""
    # Test period spanning leap day
    start = date(2024, 2, 28)  # 2024 is leap year
    end = date(2024, 3, 1)

    test_cases = [
        (DayCount.ACT_360, 2 / 360),  # 2 actual days / 360
        (DayCount.ACT_365, 2 / 365),  # 2 actual days / 365
        (DayCount.ACT_365_NL, 1 / 365),  # Feb 29 excluded
        (DayCount.ACT_ACT, 2 / 366),  # 2 days in leap year
    ]

    for convention, expected in test_cases:
        result = convention.fraction(start, end)
        assert result == pytest.approx(expected), f'Failed for {convention}'

    # Test full leap year
    start = date(2024, 1, 1)
    end = date(2025, 1, 1)

    test_cases = [
        (DayCount.ACT_360, 366 / 360),
        (DayCount.ACT_365, 366 / 365),
        (DayCount.ACT_365_NL, 365 / 365),
        (DayCount.ACT_ACT, 1.0),
        (DayCount.THIRTY_360, 1.0),
        (DayCount.THIRTY_360_E, 1.0),
    ]

    for convention, expected in test_cases:
        result = convention.fraction(start, end)
        assert result == pytest.approx(expected), f'Failed for {convention}'

    # Test period spanning multiple leap years
    start = date(2024, 1, 1)  # Leap year
    end = date(2029, 1, 1)  # Next leap year

    result = DayCount.ACT_ACT.fraction(start, end)
    assert result == pytest.approx(5.0), 'Failed for multi-year period'


def test_business_252_scenarios(calendar):
    """Test Business/252 convention with various scenarios."""
    test_cases = [
        # Regular week (5 business days)
        (
            date(2024, 1, 2),  # Tuesday
            date(2024, 1, 6),  # Saturday
            4 / 252,  # 4 business days
        ),
        # Week with holiday
        (
            date(2024, 1, 1),  # New Year's Day (Holiday)
            date(2024, 1, 6),  # Saturday
            4 / 252,  # 4 business days (excluding holiday)
        ),
        # Full month
        (
            date(2024, 1, 1),
            date(2024, 1, 31),
            22 / 252,  # Typical business days in January 2024
        ),
        # Period spanning holiday
        (
            date(2024, 12, 24),
            date(2024, 12, 26),
            2 / 252,  # Only Dec 24 and 26 are business days
        ),
    ]

    for start, end, expected in test_cases:
        result = DayCount.BUSINESS_252.fraction(start, end, calendar=calendar)
        assert result == pytest.approx(expected), f'Failed for period {start} to {end}'

    # Test full year
    start = date(2024, 1, 1)
    end = date(2024, 12, 31)
    result = DayCount.BUSINESS_252.fraction(start, end, calendar=calendar)
    assert result == pytest.approx(52 * 5 / 252), 'Failed for full year'  # Assuming ~250 business days in 2024
