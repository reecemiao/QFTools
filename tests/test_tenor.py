import pytest

from qftools.date.frequency import Frequency
from qftools.date.tenor import Tenor, TenorUnit


def test_tenor_creation():
    """Test the creation of a Tenor object."""
    # Basic creation
    t1 = Tenor(2, TenorUnit.YEAR)
    assert t1.amount == 2
    assert t1.unit == TenorUnit.YEAR

    # String parsing
    t2 = Tenor.from_string('2Y')
    assert t2.amount == 2
    assert t2.unit == TenorUnit.YEAR

    # Invalid inputs
    with pytest.raises(ValueError):
        Tenor('not an int', TenorUnit.YEAR)
    with pytest.raises(ValueError):
        Tenor(1, 'not a unit')


def test_tenor_string_representation():
    """Test the string representation of a Tenor object."""
    t = Tenor(2, TenorUnit.YEAR)
    assert str(t) == '2Y'
    assert repr(t) == 'Tenor(2, Y)'


def test_tenor_equality():
    """Test equality of Tenor objects with unit conversion."""
    assert Tenor(1, TenorUnit.YEAR) == Tenor(12, TenorUnit.MONTH)
    assert Tenor(2, TenorUnit.WEEK) == Tenor(14, TenorUnit.DAY)
    assert Tenor(1, TenorUnit.YEAR) != Tenor(1, TenorUnit.DAY)
    assert Tenor(0, TenorUnit.YEAR) == Tenor(0, TenorUnit.DAY)


def test_tenor_comparison():
    """Test comparison operations between Tenors."""
    assert Tenor(1, TenorUnit.YEAR) > Tenor(11, TenorUnit.MONTH)
    assert Tenor(1, TenorUnit.MONTH) < Tenor(2, TenorUnit.MONTH)
    assert Tenor(2, TenorUnit.WEEK) >= Tenor(14, TenorUnit.DAY)
    assert Tenor(1, TenorUnit.DAY) <= Tenor(1, TenorUnit.DAY)


def test_tenor_arithmetic():
    """Test arithmetic operations with Tenors."""
    # Addition
    assert Tenor(1, TenorUnit.YEAR) + Tenor(6, TenorUnit.MONTH) == Tenor(18, TenorUnit.MONTH)
    assert Tenor(2, TenorUnit.WEEK) + Tenor(3, TenorUnit.DAY) == Tenor(17, TenorUnit.DAY)

    # Subtraction
    assert Tenor(1, TenorUnit.YEAR) - Tenor(6, TenorUnit.MONTH) == Tenor(6, TenorUnit.MONTH)

    # Multiplication
    assert Tenor(2, TenorUnit.MONTH) * 3 == Tenor(6, TenorUnit.MONTH)
    assert 2 * Tenor(3, TenorUnit.DAY) == Tenor(6, TenorUnit.DAY)

    # Division
    assert Tenor(12, TenorUnit.MONTH) / 3 == Tenor(4, TenorUnit.MONTH)
    assert Tenor(14, TenorUnit.DAY) / 2 == Tenor(7, TenorUnit.DAY)


def test_tenor_from_frequency():
    """Test creation of Tenor from Frequency."""
    assert Tenor.from_frequency(Frequency.ONCE) == Tenor(0, TenorUnit.YEAR)
    assert Tenor.from_frequency(Frequency.ANNUAL) == Tenor(1, TenorUnit.YEAR)
    assert Tenor.from_frequency(Frequency.SEMIANNUAL) == Tenor(6, TenorUnit.MONTH)
    assert Tenor.from_frequency(Frequency.QUARTERLY) == Tenor(3, TenorUnit.MONTH)
    assert Tenor.from_frequency(Frequency.MONTHLY) == Tenor(1, TenorUnit.MONTH)
    assert Tenor.from_frequency(Frequency.WEEKLY) == Tenor(1, TenorUnit.WEEK)
    assert Tenor.from_frequency(Frequency.DAILY) == Tenor(1, TenorUnit.DAY)


def test_tenor_to_frequency():
    """Test conversion of Tenor to Frequency."""
    assert Tenor(0, TenorUnit.YEAR).to_frequency() == Frequency.ONCE
    assert Tenor(1, TenorUnit.YEAR).to_frequency() == Frequency.ANNUAL
    assert Tenor(6, TenorUnit.MONTH).to_frequency() == Frequency.SEMIANNUAL
    assert Tenor(3, TenorUnit.MONTH).to_frequency() == Frequency.QUARTERLY
    assert Tenor(1, TenorUnit.MONTH).to_frequency() == Frequency.MONTHLY
    assert Tenor(1, TenorUnit.WEEK).to_frequency() == Frequency.WEEKLY
    assert Tenor(1, TenorUnit.DAY).to_frequency() == Frequency.DAILY

    # Edge cases
    assert Tenor(-1, TenorUnit.YEAR).to_frequency() == Frequency.OTHER
    assert Tenor(5, TenorUnit.MONTH).to_frequency() == Frequency.OTHER


def test_tenor_unit_conversion():
    """Test unit conversion with and without approximation."""
    t = Tenor(1, TenorUnit.YEAR)

    # Exact conversions
    assert t._convert_to_unit(TenorUnit.MONTH) == 12
    assert Tenor(2, TenorUnit.WEEK)._convert_to_unit(TenorUnit.DAY) == 14

    # Approximate conversions
    assert t._convert_to_unit(TenorUnit.DAY, approx=True) == 365

    # Invalid conversions
    with pytest.raises(ValueError):
        t._convert_to_unit(TenorUnit.DAY, approx=False)


def test_tenor_negative_amounts():
    """Test Tenor behavior with negative amounts."""
    t = Tenor(-2, TenorUnit.MONTH)
    assert t.amount == -2
    assert t.to_frequency() == Frequency.OTHER

    # Test arithmetic with negative amounts
    assert t + Tenor(3, TenorUnit.MONTH) == Tenor(1, TenorUnit.MONTH)
    assert -2 * Tenor(3, TenorUnit.MONTH) == Tenor(-6, TenorUnit.MONTH)


def test_tenor_invalid_operations():
    """Test error cases for invalid Tenor operations."""
    t1 = Tenor(1, TenorUnit.YEAR)
    t2 = Tenor(1, TenorUnit.DAY)

    with pytest.raises(ValueError, match='Cannot add'):
        t1 + t2

    with pytest.raises(ValueError, match='cannot be divided'):
        Tenor(5, TenorUnit.MONTH) / 2


def test_tenor_from_frequency_edge_cases():
    """Test edge cases for creating Tenor from Frequency."""
    # Test ONCE frequency
    assert Tenor.from_frequency(Frequency.ONCE) == Tenor(0, TenorUnit.YEAR)

    # Test BIANNUAL frequency
    assert Tenor.from_frequency(Frequency.BIANNUAL) == Tenor(2, TenorUnit.YEAR)

    # Test invalid frequencies
    with pytest.raises(ValueError, match='Cannot convert CONTINUOUS frequency to tenor'):
        Tenor.from_frequency(Frequency.CONTINUOUS)

    with pytest.raises(ValueError, match='Unknown frequency'):
        Tenor.from_frequency(Frequency.OTHER)


def test_tenor_from_frequency_standard_cases():
    """Test standard cases for creating Tenor from Frequency."""
    test_cases = [
        (Frequency.ANNUAL, Tenor(1, TenorUnit.YEAR)),
        (Frequency.SEMIANNUAL, Tenor(6, TenorUnit.MONTH)),
        (Frequency.QUARTERLY, Tenor(3, TenorUnit.MONTH)),
        (Frequency.BIMONTHLY, Tenor(2, TenorUnit.MONTH)),
        (Frequency.MONTHLY, Tenor(1, TenorUnit.MONTH)),
        (Frequency.BIWEEKLY, Tenor(2, TenorUnit.WEEK)),
        (Frequency.WEEKLY, Tenor(1, TenorUnit.WEEK)),
        (Frequency.DAILY, Tenor(1, TenorUnit.DAY)),
    ]

    for freq, expected in test_cases:
        assert Tenor.from_frequency(freq) == expected, f'Failed for frequency {freq}'
