from datetime import date, timedelta
from enum import Enum
from typing import Optional

from .calendar import Calendar


class DayCountBasis(Enum):
    """
    Enumeration for day count conventions.

    Attributes
    ----------
    ACT_360 : int
        Actual/360 convention - actual days divided by 360
    ACT_365 : int
        Actual/365 convention - actual days divided by 365
    ACT_ACT : int
        Actual/Actual convention - actual days divided by actual days in year
    THIRTY_360 : int
        30/360 convention - months are 30 days, year is 360 days
    THIRTY_360_E : int
        30E/360 (Eurobond) convention - European variant of 30/360
    BUSINESS_252 : int
        Business/252 convention - business days divided by 252
    """

    ACT_360 = 1
    ACT_365 = 2
    ACT_ACT = 3
    THIRTY_360 = 4
    THIRTY_360_E = 5
    BUSINESS_252 = 6


def calculate(basis: DayCountBasis, start: date, end: date, calendar: Optional[Calendar] = None) -> float:
    """
    Calculate day count fraction between two dates.

    Parameters
    ----------
    basis : DayCountBasis
        Day count convention to use
    start : date
        Start date of the period
    end : date
        End date of the period
    calendar : Optional[Calendar], default=None
        Calendar for business day calculations (required for BUSINESS_252)

    Returns
    -------
    float
        Day count fraction representing the period length according to the specified convention

    Raises
    ------
    ValueError
        If end date is before start date
        If calendar is missing for BUSINESS_252 calculations
        If convention is not supported
    """
    if end < start:
        raise ValueError('End date must not be before start date')

    if basis == DayCountBasis.ACT_360:
        return _act_360(start, end)
    elif basis == DayCountBasis.ACT_365:
        return _act_365(start, end)
    elif basis == DayCountBasis.ACT_ACT:
        return _act_act(start, end)
    elif basis == DayCountBasis.THIRTY_360:
        return _thirty_360(start, end)
    elif basis == DayCountBasis.THIRTY_360_E:
        return _thirty_360_e(start, end)
    elif basis == DayCountBasis.BUSINESS_252:
        if calendar is None:
            raise ValueError('Calendar required for Business/252 calculations')
        return _business_252(start, end, calendar)

    raise ValueError(f'Day count basis {basis} not implemented')


def _act_360(start: date, end: date) -> float:
    """
    Actual/360 day count.

    Uses actual number of days between dates divided by 360.
    """
    return (end - start).days / 360.0


def _act_365(start: date, end: date) -> float:
    """
    Actual/365 day count.

    Uses actual number of days between dates divided by 365.
    """
    return (end - start).days / 365.0


def _act_act(start: date, end: date) -> float:
    """
    Actual/Actual day count.

    Uses actual number of days divided by actual days in the year,
    handling leap years correctly.
    """
    if start.year == end.year:
        days_in_year = 366 if start.year % 4 == 0 else 365
        return (end - start).days / days_in_year

    # Handle multi-year periods
    result = 0.0
    current = start
    while current.year < end.year:
        year_end = date(current.year + 1, 1, 1)
        days_in_year = 366 if current.year % 4 == 0 else 365
        result += (year_end - current).days / days_in_year
        current = year_end

    if current < end:
        days_in_year = 366 if current.year % 4 == 0 else 365
        result += (end - current).days / days_in_year

    return result


def _thirty_360(start: date, end: date) -> float:
    """
    30/360 day count.

    Each month is treated as having 30 days, year as 360 days.
    Special rules apply for month ends.
    """
    d1 = min(start.day, 30)
    d2 = min(end.day, 30) if d1 < 30 else end.day

    return (360 * (end.year - start.year) + 30 * (end.month - start.month) + (d2 - d1)) / 360.0


def _thirty_360_e(start: date, end: date) -> float:
    """
    30E/360 (Eurobond) day count.

    European variant of 30/360 where all month ends are treated as 30th.
    """
    d1 = min(start.day, 30)
    d2 = min(end.day, 30)

    return (360 * (end.year - start.year) + 30 * (end.month - start.month) + (d2 - d1)) / 360.0


def _business_252(start: date, end: date, calendar: Calendar) -> float:
    """
    Business/252 day count.

    Counts actual business days (excluding holidays and weekends)
    divided by 252 trading days per year.
    """
    business_days = sum(1 for d in range((end - start).days + 1) if calendar.is_business_day(start + timedelta(days=d)))
    return business_days / 252.0
