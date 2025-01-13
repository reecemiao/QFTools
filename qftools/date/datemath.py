from datetime import date, timedelta
from typing import List, Optional

from .calendar import Calendar
from .frequency import Frequency
from .roll import RollType
from .tenor import TenorUnit


class DateMath:
    """
    Static class providing date calculation utilities.

    This class provides methods for:
    - Adding tenors to dates
    - Rolling dates according to conventions
    - Generating date sequences
    - Business day calculations
    """

    @staticmethod
    def add_tenor(
        from_date: date,
        amount: int,
        unit: TenorUnit,
        roll_type: Optional[RollType] = None,
        calendar: Optional[Calendar] = None,
    ) -> date:
        """
        Add a tenor to a date.

        Parameters
        ----------
        from_date : date
            Starting date
        amount : int
            Amount to add
        unit : TenorUnit
            Unit of the tenor
        roll_type : Optional[RollType], default=None
            Roll convention to apply
        calendar : Optional[Calendar], default=None
            Calendar for business day adjustments

        Returns
        -------
        date
            Resulting date after tenor addition and optional rolling
        """
        if amount == 0:
            return from_date

        match unit:
            case TenorUnit.YEAR:
                result = _add_years(from_date, amount)
            case TenorUnit.MONTH:
                result = _add_months(from_date, amount)
            case TenorUnit.WEEK:
                result = from_date + timedelta(weeks=amount)
            case TenorUnit.DAY:
                result = from_date + timedelta(days=amount)
            case _:
                raise ValueError(f'Invalid tenor unit: {unit}')

        if roll_type and calendar:
            return roll_type.roll(result, calendar)
        return result

    @staticmethod
    def generate_dates(
        start: date,
        roll: date,
        maturity: date,
        frequency: Optional[Frequency] = None,
        roll_type: Optional[RollType] = None,
        reverse: bool = False,
        calendar: Optional[Calendar] = None,
    ) -> List[date]:
        """
        Generate a sequence of dates between start and maturity.

        Parameters
        ----------
        start : date
            Start date
        roll : date
            Roll date
        maturity : date
            Maturity date
        frequency : Optional[Frequency], default=None
            Payment frequency
        roll_type : Optional[RollType], default=None
            Roll convention
        reverse : bool, default=False
            If True, generate dates in reverse order
        calendar : Optional[Calendar], default=None
            Calendar for business day adjustments

        Returns
        -------
        List[date]
            List of generated dates

        Raises
        ------
        ValueError
            If dates are invalid or required parameters missing
        """
        if start > roll or roll > maturity:
            raise ValueError('Dates must be in order: start <= roll <= maturity')

        frequency = frequency or Frequency.QUARTERLY
        roll_type = roll_type or RollType.MODIFIED_FOLLOWING
        calendar = calendar or Calendar('default', set())

        dates = []
        months_per_period = 12 // abs(frequency.value)

        if not reverse:
            if roll != start:
                dates.append(roll_type.roll(roll, calendar))

            current = roll
            while current < maturity:
                current = DateMath.add_tenor(roll, len(dates) * months_per_period, TenorUnit.MONTH, roll_type, calendar)
                if current < maturity:
                    dates.append(current)

            if maturity > roll:
                dates.append(roll_type.roll(maturity, calendar))
        else:
            dates.append(roll_type.roll(maturity, calendar))

            current = maturity
            while current > roll:
                current = DateMath.add_tenor(
                    maturity, -len(dates) * months_per_period, TenorUnit.MONTH, roll_type, calendar
                )
                if current > roll:
                    dates.insert(0, current)

            if roll > start:
                dates.insert(0, roll)

        return dates

    @staticmethod
    def add_business_days(from_date: date, days: int, calendar: Calendar, adjust_up: bool = True) -> date:
        """
        Add business days to a date.

        Parameters
        ----------
        from_date : date
            Starting date
        days : int
            Number of business days to add (can be negative)
        calendar : Calendar
            Calendar for business day calculations
        adjust_up : bool, optional
            If True, adjust start date up to next business day if needed, by default True

        Returns
        -------
        date
            Resulting date after adding business days
        """
        date_ = calendar.adjust_up(from_date) if adjust_up else calendar.adjust_down(from_date)

        if days == 0:
            return date_

        step = 1 if days >= 0 else -1
        remaining = abs(days)

        while remaining > 0:
            date_ = date_ + timedelta(days=step)
            if calendar.is_business_day(date_):
                remaining -= 1

        return date_


def _add_months(date_: date, months: int) -> date:
    """Add months to a date, preserving end-of-month if applicable."""
    year = date_.year + ((date_.month - 1 + months) // 12)
    month = (date_.month - 1 + months) % 12 + 1

    # Try to maintain same day of month
    try:
        return date(year, month, date_.day)
    except ValueError:
        # If day is invalid (e.g. Feb 30), return end of month
        return date(year, month + 1, 1) - timedelta(days=1)


def _add_years(date_: date, years: int) -> date:
    """Add years to a date, preserving end-of-month if applicable."""
    try:
        return date(date_.year + years, date_.month, date_.day)
    except ValueError:
        # Handle Feb 29 in leap years
        return date(date_.year + years, date_.month, 28)
