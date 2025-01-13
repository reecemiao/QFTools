from datetime import date, timedelta
from enum import Enum
from typing import Set


class Weekend(Enum):
    """Enumeration representing days of the week that can be considered weekend days."""

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class Calendar:
    """A calendar class that handles business days, holidays and weekend calculations."""

    def __init__(self, name: str, holidays: Set[date], weekend: Set[Weekend] = {Weekend.SATURDAY, Weekend.SUNDAY}):
        """
        Initialize Calendar instance.

        Parameters
        ----------
        name : str
            Calendar name
        holidays : Set[date]
            Set of holiday dates
        weekend : Set[Weekend], optional
            Set of weekend days, by default {Weekend.SATURDAY, Weekend.SUNDAY}

        Raises
        ------
        ValueError
            If all days are marked as weekend
        """
        if self._all_weekend(weekend):
            raise ValueError('Every day of the week is defined as a weekend. Illegal.')

        self.name = name
        self.holidays = set(holidays)  # Ensure we have a copy
        self.weekend = weekend

    def __add__(self, other: 'Calendar') -> 'Calendar':
        """
        Join two calendars, combining their holidays and weekend days.

        Parameters
        ----------
        other : Calendar
            Calendar to join with this one

        Returns
        -------
        Calendar
            New calendar with combined holidays and weekend days

        Examples
        --------
        >>> us_cal = Calendar('US', us_holidays)
        >>> uk_cal = Calendar('UK', uk_holidays)
        >>> us_uk_cal = us_cal + uk_cal  # Contains holidays from both calendars
        """
        if not isinstance(other, Calendar):
            return NotImplemented

        name = f'{self.name}+{other.name}'
        holidays = self.holidays | other.holidays  # Union of holiday sets
        weekend = self.weekend | other.weekend  # Union of weekend sets

        return Calendar(name, holidays, weekend)

    def __repr__(self) -> str:
        """Return string representation of the calendar."""
        return f"Calendar(name='{self.name}', holidays={len(self.holidays)}, weekend={self.weekend})"

    def add_holiday(self, holiday: date) -> None:
        """
        Add a holiday to the calendar.

        Parameters
        ----------
        holiday : date
            Date to add as holiday
        """
        self.holidays.add(holiday)

    def remove_holiday(self, holiday: date) -> None:
        """
        Remove a holiday from the calendar.

        Parameters
        ----------
        holiday : date
            Date to remove from holidays
        """
        self.holidays.discard(holiday)

    def is_weekend(self, date_: date) -> bool:
        """Check if given date falls on a weekend."""
        return self._is_weekend(date_, self.weekend)

    @staticmethod
    def _is_weekend(date_: date, weekend: Set[Weekend]) -> bool:
        weekday = date_.weekday()
        # The weekend_map keys should match Python's weekday() values (0-6 starting from Monday)
        weekend_map = {
            0: Weekend.MONDAY,
            1: Weekend.TUESDAY,
            2: Weekend.WEDNESDAY,
            3: Weekend.THURSDAY,
            4: Weekend.FRIDAY,
            5: Weekend.SATURDAY,
            6: Weekend.SUNDAY,
        }
        return weekend_map[weekday] in weekend

    def is_business_day(self, date_: date) -> bool:
        """Check if given date is a business day."""
        if self.is_weekend(date_):
            return False
        return date_ not in self.holidays

    def add_business_days(self, from_date: date, days: int, adjust_up: bool) -> date:
        """
        Add business days to a given date.

        Parameters
        ----------
        from_date : date
            Starting date
        days : int
            Number of business days to add (can be negative)
        adjust_up : bool
            If True, adjust start date up to next business day if it falls on holiday/weekend
            If False, adjust start date down to previous business day

        Returns
        -------
        date
            Resulting date after adding business days
        """
        date_ = self.adjust_up(from_date) if adjust_up else self.adjust_down(from_date)
        if days == 0:
            return date_

        step = 1 if days >= 0 else -1
        count = 0
        days = abs(days)

        while count != days:
            date_ = date_ + timedelta(days=step)
            if self.is_business_day(date_):
                count += 1

        return date_

    def adjust_up(self, from_date: date) -> date:
        """
        Adjust date upward to next business day.

        Parameters
        ----------
        from_date : date
            Date to adjust

        Returns
        -------
        date
            Next business day
        """
        date_ = from_date
        while not self.is_business_day(date_):
            date_ = date_ + timedelta(days=1)
        return date_

    def adjust_down(self, from_date: date) -> date:
        """
        Adjust date downward to previous business day.

        Parameters
        ----------
        from_date : date
            Date to adjust

        Returns
        -------
        date
            Previous business day
        """
        date_ = from_date
        while not self.is_business_day(date_):
            date_ = date_ + timedelta(days=-1)
        return date_

    @staticmethod
    def _all_weekend(weekend: Set[Weekend]) -> bool:
        """
        Check if all days are marked as weekend.

        Parameters
        ----------
        weekend : Set[Weekend]
            Set of weekend days to check

        Returns
        -------
        bool
            True if all days are weekend, False otherwise
        """
        all_days = {
            Weekend.MONDAY,
            Weekend.TUESDAY,
            Weekend.WEDNESDAY,
            Weekend.THURSDAY,
            Weekend.FRIDAY,
            Weekend.SATURDAY,
            Weekend.SUNDAY,
        }
        return weekend == all_days
