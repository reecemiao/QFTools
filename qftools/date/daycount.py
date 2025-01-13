from datetime import date, timedelta
from enum import Enum
from typing import Optional

from .calendar import Calendar
from .frequency import Frequency


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
    ACT_365_ICMA : int
        Actual/365 ICMA convention
    ACT_365_NL : int
        Actual/365 No Leap convention - actual days excluding Feb 29 divided by 365
    ACT_ACT : int
        Actual/Actual convention - actual days divided by actual days in year
    ACT_ACT_AFB : int
        Actual/Actual AFB convention - French Bond Market Association method
    ACT_ACT_ICMA : int
        Actual/Actual ICMA convention
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
    """

    ACT_360 = 1
    ACT_365 = 2
    ACT_365_ICMA = 3
    ACT_365_NL = 4
    ACT_ACT = 5
    ACT_ACT_AFB = 6
    ACT_ACT_ICMA = 7
    THIRTY_360 = 8
    THIRTY_360_E = 9
    THIRTY_360_ISDA = 10
    THIRTY_360_US = 11
    BUSINESS_252 = 12

    def fraction(
        self,
        start: date,
        end: date,
        maturity: Optional[date] = None,
        calendar: Optional[Calendar] = None,
        payment: Optional[date] = None,
        frequency: Optional[Frequency] = None,
    ) -> float:
        """
        Calculate year fraction between two dates.

        Parameters
        ----------
        start : date
            Start date
        end : date
            End date
        maturity : Optional[date], default=None
            Maturity date, required for some conventions
        calendar : Optional[Calendar], default=None
            Calendar for business day calculations
        payment : Optional[date], default=None
            Payment date, required for ICMA conventions
        frequency : Optional[Frequency], default=None
            Payment frequency, required for ICMA conventions

        Returns
        -------
        float
            Year fraction according to the specified day count convention

        Raises
        ------
        ValueError
            If required parameters are missing or invalid
        """
        if end < start:
            raise ValueError('End date must not be before start date')

        dispatch = {
            DayCount.ACT_360: lambda: self._act_360(start, end),
            DayCount.ACT_365: lambda: self._act_365(start, end),
            DayCount.ACT_365_NL: lambda: self._act_365_nl(start, end),
            DayCount.ACT_ACT: lambda: self._act_act(start, end),
            DayCount.ACT_ACT_AFB: lambda: self._act_act_afb(start, end),
            DayCount.THIRTY_360: lambda: self._thirty_360(start, end),
            DayCount.THIRTY_360_E: lambda: self._thirty_360_e(start, end),
            DayCount.THIRTY_360_ISDA: lambda: self._validate_and_calc_isda(start, end, maturity),
            DayCount.THIRTY_360_US: lambda: self._thirty_360_us(start, end),
            DayCount.BUSINESS_252: lambda: self._validate_and_calc_business(start, end, calendar),
            DayCount.ACT_ACT_ICMA: lambda: self._validate_and_calc_icma(start, end, maturity, payment, frequency),
            DayCount.ACT_365_ICMA: lambda: self._validate_and_calc_icma_365(start, end, maturity, payment, frequency),
        }

        return dispatch[self]()

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
    def _act_365_icma(cls, start: date, end: date, maturity: date, payment: date, frequency: Frequency) -> float:
        """
        Actual/365 ICMA day count.

        This convention is similar to ACT/ACT ICMA but uses 365 as a fixed denominator. It has special
        handling for periods that exceed the standard length.

        Key features:
        1. Uses actual days for numerator
        2. Uses 365 as fixed denominator
        3. Special handling for long periods
        4. Considers payment frequency for period calculations

        Parameters
        ----------
        start : date
            Start date of the period
        end : date
            End date of the period
        maturity : date
            Final maturity date of the instrument
        payment : date
            Next payment date
        frequency : Frequency
            Payment frequency (e.g., SEMIANNUAL = 2, QUARTERLY = 4)

        Returns
        -------
        float
            Year fraction according to ACT/365 ICMA convention
        """
        if not payment or not maturity:
            raise ValueError('Payment and maturity dates required for ACT/365 ICMA')

        freq_factor = frequency.value if frequency.value > 0 else -1 / frequency.value
        months_per_period = int(12 // freq_factor)

        # Check if dates align with frequency
        if cls._check_period_alignment(start, payment, months_per_period) and cls._check_date_alignment(start, payment):
            days = (end - start).days
            if days > 365 / freq_factor and end != payment:
                # Special case: period exceeds standard length
                return 1 / freq_factor - 1 / 365
            # Regular case: actual days / 365
            return days / 365

        # Handle non-aligned periods
        current, target, direction = cls._get_period_dates(start, payment, maturity)

        total_fraction = 0.0
        while direction * (current - target).days < 0:
            next_date = cls._get_next_period_date(current, direction * months_per_period)
            period_start = max(start, min(next_date, current))
            period_end = min(end, max(next_date, current))

            days = (period_end - period_start).days
            if days > 0:
                if direction == -1 and period_end == current and period_start == next_date:
                    days = 365 / freq_factor
                elif direction == 1 and period_end == next_date and period_start == current:
                    days = 365 / freq_factor
                total_fraction += days / (365 / freq_factor)

            current = next_date

        return total_fraction / freq_factor

    @classmethod
    def _act_365_nl(cls, start: date, end: date) -> float:
        """
        Actual/365 No Leap day count.

        Parameters
        ----------
        start : date
            Start date
        end : date
            End date

        Returns
        -------
        float
            Day count fraction using Actual/365 No Leap convention

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

    @classmethod
    def _act_act_icma(cls, start: date, end: date, maturity: date, payment: date, frequency: Frequency) -> float:
        """
        Actual/Actual ICMA day count.

        This convention divides the actual number of days in a period by the actual number of days
        in the coupon period, then divides by the frequency. It's commonly used for bonds.

        Key features:
        1. Uses actual days in both numerator and denominator
        2. Considers payment frequency for period calculations
        3. Special handling for non-aligned periods
        4. Different calculation for forward/backward periods

        Parameters
        ----------
        start : date
            Start date of the period
        end : date
            End date of the period
        maturity : date
            Final maturity date
        payment : date
            Next payment date
        frequency : Frequency
            Payment frequency (e.g., SEMIANNUAL = 2, QUARTERLY = 4)

        Returns
        -------
        float
            Year fraction according to ACT/ACT ICMA convention
        """
        freq_factor = frequency.value if frequency.value > 0 else -1 / frequency.value
        months_per_period = int(12 // freq_factor)

        if cls._check_period_alignment(start, payment, months_per_period) and cls._check_date_alignment(start, payment):
            return (end - start).days / ((payment - start).days * freq_factor)

        current, target, direction = cls._get_period_dates(start, payment, maturity, months_per_period)

        total_fraction = 0.0
        while direction * (current - target).days < 0:
            next_date = cls._get_next_period_date(current, direction * months_per_period)
            period_start = max(start, min(next_date, current))
            period_end = min(end, max(next_date, current))

            days = (period_end - period_start).days
            if days > 0:
                total_fraction += days / (next_date - current).days

            current = next_date

        return total_fraction / freq_factor

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

    def _validate_and_calc_icma(
        self, start: date, end: date, maturity: Optional[date], payment: Optional[date], frequency: Optional[Frequency]
    ) -> float:
        """Validate and calculate ACT/ACT ICMA day count."""
        if not all([maturity, payment, frequency]):
            raise ValueError('Maturity, payment dates and frequency required for ACT/ACT ICMA')
        if frequency in (Frequency.ONCE, Frequency.BIWEEKLY, Frequency.WEEKLY, Frequency.DAILY, Frequency.OTHER):
            raise ValueError('Frequency must not be ONCE, BIWEEKLY, WEEKLY, DAILY, or OTHER for ACT/ACT ICMA')
        return self._act_act_icma(start, end, maturity, payment, frequency)

    def _validate_and_calc_icma_365(
        self, start: date, end: date, maturity: Optional[date], payment: Optional[date], frequency: Optional[Frequency]
    ) -> float:
        """Validate and calculate ACT/365 ICMA day count."""
        if not all([maturity, payment, frequency]):
            raise ValueError('Maturity, payment dates and frequency required for ACT/365 ICMA')
        if frequency in (Frequency.ONCE, Frequency.BIWEEKLY, Frequency.WEEKLY, Frequency.DAILY, Frequency.OTHER):
            raise ValueError('Frequency must not be ONCE, BIWEEKLY, WEEKLY, DAILY, or OTHER for ACT/365 ICMA')
        return self._act_365_icma(start, end, maturity, payment, frequency)

    @staticmethod
    def _is_leap_year(year: int) -> bool:
        """Check if year is a leap year."""
        try:
            date(year, 2, 29)
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_last_day_of_february(date_: date) -> bool:
        """Check if date is the last day of February."""
        next_date = date_ + timedelta(days=1)
        return next_date.month == 3 and next_date.day == 1

    @staticmethod
    def _get_new_month(month: int, number: int) -> int:
        """Get new month after adding number of months."""
        total = month + number
        if total <= 0:
            return total % 12 + 12
        return (total - 1) % 12 + 1

    @staticmethod
    def _get_new_year(year: int, month: int, number: int) -> int:
        """Get new year after adding number of months."""
        total = month + number
        if total <= 0:
            return year - 1 + total // 12
        return year + (total - 1) // 12

    @staticmethod
    def _is_ultimo(date_: date) -> bool:
        """Check if date is the last day of month."""
        return (date_ + timedelta(days=1)).day == 1

    @staticmethod
    def _get_ultimo(year: int, month: int) -> date:
        """Get last day of month."""
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        return date(year, month, 1) - timedelta(days=1)

    @staticmethod
    def _invalid_date(year: int, month: int, day: int) -> bool:
        """Check if date would be invalid."""
        try:
            test_date = date(year, month, 1)
            return (test_date + timedelta(days=day - 1)).month != month
        except ValueError:
            return True

    @classmethod
    def _get_next_period_date(cls, current: date, months: int) -> date:
        """Get the next period date based on months offset."""
        year = cls._get_new_year(current.year, current.month, months)
        month = cls._get_new_month(current.month, months)

        if cls._invalid_date(year, month, current.day):
            return cls._get_ultimo(year, month)
        return date(year, month, current.day)

    @classmethod
    def _get_period_dates(cls, start: date, payment: date, maturity: date) -> tuple[date, date, int]:
        """Get period dates for ICMA calculations."""
        direction = 1 if payment == maturity else -1
        current = start if direction == 1 else payment
        target = payment if direction == 1 else start
        return current, target, direction

    @classmethod
    def _check_period_alignment(cls, start: date, payment: date, months_per_period: int) -> bool:
        """Check if dates align with payment frequency."""
        year_diff = payment.year - start.year
        month_diff = payment.month - start.month
        return year_diff * 12 + month_diff == months_per_period

    @classmethod
    def _check_date_alignment(cls, start: date, payment: date) -> bool:
        """Check if dates align on same day or ultimo."""
        return (
            start.day == payment.day
            or (cls._invalid_date(start.year, start.month, payment.day) and cls._is_ultimo(start))
            or (cls._invalid_date(payment.year, payment.month, start.day) and cls._is_ultimo(payment))
        )
