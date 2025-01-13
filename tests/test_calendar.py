from datetime import date, timedelta
from time import perf_counter

import pytest

from qftools.date.calendar import Calendar, Weekend


@pytest.fixture
def sample_holidays():
    """Sample holidays for testing."""
    return [
        date(2024, 1, 1),  # New Year's Day
        date(2024, 12, 25),  # Christmas
    ]


@pytest.fixture
def calendar(sample_holidays):
    """Fixture for creating a calendar instance."""
    return Calendar('Test Calendar', sample_holidays)


def test_calendar_init(sample_holidays):
    """Test calendar initialization."""
    cal = Calendar('Test Calendar', sample_holidays)
    assert cal.name == 'Test Calendar'
    assert len(cal.holidays) == 2
    assert cal.weekend == set([Weekend.SATURDAY, Weekend.SUNDAY])


def test_calendar_init_with_invalid_weekend():
    """Test calendar initialization with all days as weekend."""
    all_days = {
        Weekend.MONDAY,
        Weekend.TUESDAY,
        Weekend.WEDNESDAY,
        Weekend.THURSDAY,
        Weekend.FRIDAY,
        Weekend.SATURDAY,
        Weekend.SUNDAY,
    }
    with pytest.raises(ValueError, match='Every day of the week is defined as a weekend'):
        Calendar('Invalid Calendar', [], all_days)


def test_is_weekend(calendar):
    """Test weekend day detection."""
    saturday = date(2024, 1, 6)  # A Saturday
    sunday = date(2024, 1, 7)  # A Sunday
    monday = date(2024, 1, 8)  # A Monday

    assert calendar.is_weekend(saturday) is True
    assert calendar.is_weekend(sunday) is True
    assert calendar.is_weekend(monday) is False


def test_is_business_day(calendar):
    """Test business day detection."""
    holiday = date(2024, 1, 1)  # New Year's Day (holiday)
    saturday = date(2024, 1, 6)  # A Saturday (weekend)
    regular = date(2024, 1, 2)  # Regular business day

    assert calendar.is_business_day(holiday) is False
    assert calendar.is_business_day(saturday) is False
    assert calendar.is_business_day(regular) is True


def test_add_business_days(calendar):
    """Test adding business days to a date."""
    start_date = date(2024, 1, 1)  # New Year's Day (holiday)

    # Add 1 business day from holiday
    result = calendar.add_business_days(start_date, 1, True)
    assert result == date(2024, 1, 3)

    # Add -1 business day from holiday
    result = calendar.add_business_days(start_date, -1, False)
    assert result == date(2023, 12, 28)  # Previous Friday


def test_adjust_up_down(calendar):
    """Test adjusting dates up and down to business days."""
    holiday = date(2024, 1, 1)  # New Year's Day (holiday)

    # Adjust up from holiday
    assert calendar.adjust_up(holiday) == date(2024, 1, 2)

    # Adjust down from holiday
    assert calendar.adjust_down(holiday) == date(2023, 12, 29)


def test_holiday_lookup_performance():
    """Test performance of holiday lookups."""
    # Create a calendar with many holidays
    many_holidays = [date(2024, 1, 1) + timedelta(days=i) for i in range(1000)]
    cal = Calendar('Test Calendar', many_holidays)

    # Test date not in holidays
    test_date = date(2025, 1, 1)

    # Measure lookup time
    start = perf_counter()
    for _ in range(10000):
        cal.is_business_day(test_date)
    end = perf_counter()

    # Should complete quickly even with many holidays
    assert end - start < 1.0  # Should complete in under a second


def test_calendar_addition():
    """Test joining calendars with + operator."""
    # Create two calendars with different holidays and weekends
    cal1 = Calendar(
        'US',
        {date(2024, 1, 1), date(2024, 7, 4)},  # New Year's and Independence Day
        {Weekend.SATURDAY, Weekend.SUNDAY},
    )

    cal2 = Calendar(
        'UK',
        {date(2024, 1, 1), date(2024, 12, 26)},  # New Year's and Boxing Day
        {Weekend.SATURDAY, Weekend.SUNDAY, Weekend.FRIDAY},  # Friday-Sunday weekend
    )

    # Join calendars
    combined = cal1 + cal2

    # Check combined calendar properties
    assert combined.name == 'US+UK'
    assert len(combined.holidays) == 3  # New Year's appears only once
    assert combined.weekend == {Weekend.FRIDAY, Weekend.SATURDAY, Weekend.SUNDAY}

    # Check business days
    assert not combined.is_business_day(date(2024, 1, 1))  # New Year's
    assert not combined.is_business_day(date(2024, 7, 4))  # Independence Day
    assert not combined.is_business_day(date(2024, 12, 26))  # Boxing Day
    assert not combined.is_business_day(date(2024, 1, 5))  # Friday
    assert combined.is_business_day(date(2024, 1, 2))  # Regular business day


def test_calendar_addition_invalid():
    """Test calendar addition with invalid operand."""
    cal = Calendar('Test', {date(2024, 1, 1)})

    # Adding non-Calendar should return NotImplemented
    result = cal.__add__(42)
    assert result is NotImplemented
