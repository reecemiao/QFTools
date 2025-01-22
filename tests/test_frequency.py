import pytest

from qftools.date.frequency import Frequency


def test_annual_frequency():
    """Test annual_frequency method."""
    test_cases = [
        (Frequency.ONCE, float('nan')),
        (Frequency.BIANNUAL, 0.5),
        (Frequency.ANNUAL, 1.0),
        (Frequency.SEMIANNUAL, 2.0),
        (Frequency.QUARTERLY, 4.0),
        (Frequency.BIMONTHLY, 6.0),
        (Frequency.MONTHLY, 12.0),
        (Frequency.BIWEEKLY, 26.0),
        (Frequency.WEEKLY, 52.0),
        (Frequency.DAILY, 365.0),
        (Frequency.CONTINUOUS, float('inf')),
        (Frequency.OTHER, float('nan')),
    ]

    for freq, expected in test_cases:
        result = freq.annual_frequency()
        if isinstance(expected, float) and expected != expected:
            assert result != result  # NaN check
        else:
            assert result == pytest.approx(expected), f'Failed for frequency {freq}'


def test_period_months():
    """Test period_months method."""
    test_cases = [
        (Frequency.ONCE, float('nan')),
        (Frequency.BIANNUAL, 24.0),
        (Frequency.ANNUAL, 12.0),
        (Frequency.SEMIANNUAL, 6.0),
        (Frequency.QUARTERLY, 3.0),
        (Frequency.BIMONTHLY, 2.0),
        (Frequency.MONTHLY, 1.0),
        (Frequency.BIWEEKLY, 12 / 26),
        (Frequency.WEEKLY, 12 / 52),
        (Frequency.DAILY, 12 / 365),
        (Frequency.CONTINUOUS, 0.0),
        (Frequency.OTHER, float('nan')),
    ]

    for freq, expected in test_cases:
        result = freq.period_months()
        if isinstance(expected, float) and expected != expected:
            assert result != result  # NaN check
        else:
            assert result == pytest.approx(expected), f'Failed for frequency {freq}'


def test_frequency_values():
    """Test frequency enum values."""
    assert Frequency.ONCE.value == 0
    assert Frequency.BIANNUAL.value == -2
    assert Frequency.ANNUAL.value == 1
    assert Frequency.SEMIANNUAL.value == 2
    assert Frequency.QUARTERLY.value == 4
    assert Frequency.BIMONTHLY.value == 6
    assert Frequency.MONTHLY.value == 12
    assert Frequency.BIWEEKLY.value == 26
    assert Frequency.WEEKLY.value == 52
    assert Frequency.DAILY.value == 365
    assert Frequency.CONTINUOUS.value == 999
    assert Frequency.OTHER.value == 9999
