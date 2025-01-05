from datetime import date, timedelta
from enum import Enum
from typing import Optional

from .calendar import Calendar


class DayCount(Enum):
    """
    Enumeration for day count conventions.

    Parameters
    ----------
    None

    Attributes
    ----------
    ACT_360 : int
        Actual/360 convention - actual days divided by 360
    ACT_365 : int
        Actual/365 convention - actual days divided by 365
    ACT_365L : int
        Actual/365L convention - actual days excluding Feb 29 divided by 365
    ACT_ACT : int
        Actual/Actual convention - actual days divided by actual days in year
    ACT_ACT_AFB : int
        Actual/Actual AFB convention - French Bond Market Association method
    THIRTY_360 : int
        30/360 convention - months are 30 days, year is 360 days
    THIRTY_360_E : int
        30E/360 (Eurobond) convention - European variant of 30/360
    THIRTY_360_ISDA : int
        30E/360 (ISDA) convention - ISDA variant of 30/360
    THIRTY_360_US : int
        30/360 US convention - US variant of 30/360
    BUSINESS_252 : int
        Business/252 convention - business days divided by 252

    TODO:
    - ACT_ACT_ICMA
    """

    ACT_360 = 1
    ACT_365 = 2
    ACT_365L = 3
    ACT_ACT = 4
    ACT_ACT_AFB = 5
    THIRTY_360 = 6
    THIRTY_360_E = 7
    THIRTY_360_ISDA = 8
    THIRTY_360_US = 9
    BUSINESS_252 = 10

    @classmethod
    def _act_360(cls, start: date, end: date) -> float:
        """
        Actual/360 day count.

        Parameters
        ----------
        start : date
            Start date
        end : date
            End date

        Returns
        -------
        float
            Day count fraction using Actual/360 convention
        """
        return (end - start).days / 360.0

    @classmethod
    def _act_365(cls, start: date, end: date) -> float:
        """
        Actual/365 day count.

        Parameters
        ----------
        start : date
            Start date
        end : date
            End date

        Returns
        -------
        float
            Day count fraction using Actual/365 convention
        """
        return (end - start).days / 365.0

    @classmethod
    def _act_365l(cls, start: date, end: date) -> float:
        """
        Actual/365L day count.

        Parameters
        ----------
        start : date
            Start date
        end : date
            End date

        Returns
        -------
        float
            Day count fraction using Actual/365L convention

        Notes
        -----
        Counts actual days excluding February 29th divided by 365
        """
        current = start
        days = 0

        while current < end:
            if not (current.month == 2 and current.day == 29):
                days += 1
            current += timedelta(days=1)

        return days / 365.0

    @classmethod
    def _act_act(cls, start: date, end: date) -> float:
        """
        Actual/Actual day count.

        Parameters
        ----------
        start : date
            Start date
        end : date
            End date

        Returns
        -------
        float
            Day count fraction using Actual/Actual convention

        Notes
        -----
        This implementation follows the ISDA method where the fraction is calculated as:
        years + (end - start_of_end_year)/(days_in_end_year) - (start - start_of_start_year)/(days_in_start_year)
        """
        start_year_begin = date(start.year, 1, 1)
        end_year_begin = date(end.year, 1, 1)
        start_next_year = date(start.year + 1, 1, 1)
        end_next_year = date(end.year + 1, 1, 1)

        return (
            (end.year - start.year)
            + (end - end_year_begin).days / (end_next_year - end_year_begin).days
            - (start - start_year_begin).days / (start_next_year - start_year_begin).days
        )

    @classmethod
    def _act_act_afb(cls, start: date, end: date) -> float:
        """
        Actual/Actual AFB day count.

        Parameters
        ----------
        start : date
            Start date
        end : date
            End date

        Returns
        -------
        float
            Day count fraction using Actual/Actual AFB convention

        Notes
        -----
        French Bond Market Association (AFB) method
        """
        days = (end - start).days
        denominator = 365.0
        is_multi_year = days > 366.0

        if not is_multi_year:
            if not cls._is_leap_year(start.year) and not cls._is_leap_year(end.year):
                is_multi_year = days > 365.0
                denominator = 365.0
            else:
                leap_year = start.year if cls._is_leap_year(start.year) else end.year
                leap_day = date(leap_year, 2, 29)

                if start <= leap_day <= end:
                    denominator = 366.0
                else:
                    is_multi_year = days > 365.0
                    denominator = 365.0

        if not is_multi_year:
            return days / denominator

        # Handle multi-year periods recursively
        if end.month == 2 and end.day == 29:
            prev_year_end = date(end.year - 1, 2, 28)
        elif end.month == 2 and end.day == 28 and cls._is_leap_year(end.year - 1):
            prev_year_end = date(end.year - 1, 2, 29)
        else:
            prev_year_end = date(end.year - 1, end.month, end.day)

        return cls._act_act_afb(start, prev_year_end) + cls._act_act_afb(prev_year_end, end)

    @staticmethod
    def _is_leap_year(year: int) -> bool:
        """Check if year is a leap year."""
        try:
            date(year, 2, 29)
            return True
        except ValueError:
            return False

    @classmethod
    def _thirty_360(cls, start: date, end: date) -> float:
        """
        30/360 day count.

        Parameters
        ----------
        start : date
            Start date
        end : date
            End date

        Returns
        -------
        float
            Day count fraction using 30/360 convention

        Notes
        -----
        - If the end date is 31 and the start date is greater than or equal to 30, the end date is treated as 30 days.
        - If the start date is 31, it is treated as 30 days.
        """
        d1 = min(start.day, 30) if start.day != 31 else 30
        d2 = end.day if end.day != 31 else (30 if start.day >= 30 else 31)

        return (360 * (end.year - start.year) + 30 * (end.month - start.month) + (d2 - d1)) / 360.0

    @classmethod
    def _thirty_360_e(cls, start: date, end: date) -> float:
        """
        30E/360 (Eurobond) day count.

        Parameters
        ----------
        start : date
            Start date
        end : date
            End date

        Returns
        -------
        float
            Day count fraction using 30E/360 convention

        Notes
        -----
        - If the end date is 31, it is treated as 30 days.
        - If the start date is 31, it is treated as 30 days.
        """
        d1 = 30 if start.day == 31 else start.day
        d2 = 30 if end.day == 31 else end.day

        return (360 * (end.year - start.year) + 30 * (end.month - start.month) + (d2 - d1)) / 360.0

    @classmethod
    def _thirty_360_isda(cls, start: date, end: date, maturity: date) -> float:
        """
        30E/360 ISDA day count.

        Parameters
        ----------
        start : date
            Start date
        end : date
            End date
        maturity : date
            Maturity date

        Returns
        -------
        float
            Day count fraction using 30E/360 ISDA convention

        Notes
        -----
        - If the start date is the last day of February, it is treated as 30 days.
        - If the end date is the last day of February, except for the maturity, it is treated as 30 days.
        - If the end date is 31 and the start date is greater than or equal to 30, the end date is treated as 30 days.
        - If the start date is 31, it is treated as 30 days.
        """
        d1 = (
            (30 if cls._is_last_day_of_february(start) else (30 if start.day == 31 else start.day))
            if start.month != 2
            else start.day
        )

        d2 = (
            (end.day if end == maturity else 30)
            if cls._is_last_day_of_february(end)
            else (30 if end.day == 31 else end.day)
            if end.month != 2
            else end.day
        )

        return (360 * (end.year - start.year) + 30 * (end.month - start.month) + (d2 - d1)) / 360.0

    @classmethod
    def _thirty_360_us(cls, start: date, end: date) -> float:
        """
        30/360 US day count.

        Parameters
        ----------
        start : date
            Start date
        end : date
            End date

        Returns
        -------
        float
            Day count fraction using 30/360 US convention

        Notes
        -----
        - If the end date is the last day of February, it is treated as 30 days.
        - If the start date is the last day of February, it is treated as 30 days.
        - If the end date is 31 and the start date is greater than or equal to 30, the end date is treated as 30 days.
        - If the start date is 31, it is treated as 30 days.
        """
        d1 = start.day
        d2 = end.day

        if cls._is_last_day_of_february(start) and cls._is_last_day_of_february(end):
            d2 = 30
        if cls._is_last_day_of_february(start):
            d1 = 30
        if d2 == 31 and d1 >= 30:
            d2 = 30
        if d1 == 31:
            d1 = 30

        return (360 * (end.year - start.year) + 30 * (end.month - start.month) + (d2 - d1)) / 360.0

    @classmethod
    def _business_252(cls, start: date, end: date, calendar: Calendar) -> float:
        """
        Business/252 day count.

        Counts actual business days (excluding holidays and weekends)
        divided by 252 trading days per year.

        Parameters
        ----------
        start : date
            Start date
        end : date
            End date
        calendar : Calendar
            Calendar for business day calculations

        Returns
        -------
        float
            Day count fraction using Business/252 convention
        """
        business_days = sum(
            1 for d in range((end - start).days + 1) if calendar.is_business_day(start + timedelta(days=d))
        )
        return business_days / 252.0

    def year_fraction(
        self, start: date, end: date, maturity: Optional[date] = None, calendar: Optional[Calendar] = None
    ) -> float:
        """Calculate year fraction between two dates."""
        if end < start:
            raise ValueError('End date must not be before start date')

        dispatch = {
            DayCount.ACT_360: lambda: self._act_360(start, end),
            DayCount.ACT_365: lambda: self._act_365(start, end),
            DayCount.ACT_365L: lambda: self._act_365l(start, end),
            DayCount.ACT_ACT: lambda: self._act_act(start, end),
            DayCount.ACT_ACT_AFB: lambda: self._act_act_afb(start, end),
            DayCount.THIRTY_360: lambda: self._thirty_360(start, end),
            DayCount.THIRTY_360_E: lambda: self._thirty_360_e(start, end),
            DayCount.THIRTY_360_ISDA: lambda: self._validate_and_calc_isda(start, end, maturity),
            DayCount.THIRTY_360_US: lambda: self._thirty_360_us(start, end),
            DayCount.BUSINESS_252: lambda: self._validate_and_calc_business(start, end, calendar),
        }

        return dispatch[self]()

    def _validate_and_calc_isda(self, start: date, end: date, maturity: Optional[date]) -> float:
        """Validate and calculate 30E/360 ISDA day count."""
        if maturity is None:
            raise ValueError('Maturity date required for 30E/360 ISDA calculations')
        return self._thirty_360_isda(start, end, maturity)

    def _validate_and_calc_business(self, start: date, end: date, calendar: Optional[Calendar]) -> float:
        """Validate and calculate Business/252 day count."""
        if calendar is None:
            raise ValueError('Calendar required for Business/252 calculations')
        return self._business_252(start, end, calendar)

    @staticmethod
    def _is_last_day_of_february(date_: date) -> bool:
        """Check if date is the last day of February."""
        next_date = date_ + timedelta(days=1)
        return next_date.month == 3 and next_date.day == 1
