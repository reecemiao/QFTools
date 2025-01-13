from datetime import date, timedelta
from enum import Enum
from typing import Optional

from .calendar import Calendar


class RollType(Enum):
    """
    Enumeration for date rolling conventions.

    Parameters
    ----------
    None

    Attributes
    ----------
    MODIFIED_FOLLOWING : int
        Modified Following convention - roll forward unless crosses month boundary
    FOLLOWING : int
        Following convention - always roll forward
    MODIFIED_PREVIOUS : int
        Modified Previous convention - roll backward unless crosses month boundary
    PREVIOUS : int
        Previous convention - always roll backward
    NONE : int
        No roll adjustment
    MODIFIED_FOLLOWING_EOM : int
        Modified Following End of Month convention
    IMM : int
        IMM convention - third Wednesday of the month
    CAD_IMM : int
        Canadian IMM convention - third Wednesday minus 2 days
    UNADJUSTED_EOM : int
        Unadjusted End of Month convention
    """

    MODIFIED_FOLLOWING = 1
    FOLLOWING = 2
    MODIFIED_PREVIOUS = 3
    PREVIOUS = 4
    NONE = 5
    MODIFIED_FOLLOWING_EOM = 6
    IMM = 7
    CAD_IMM = 8
    UNADJUSTED_EOM = 9

    def roll(self, date_: date, calendar: Optional[Calendar] = None) -> date:
        """
        Roll a date according to the convention.

        Parameters
        ----------
        date_ : date
            Date to roll
        calendar : Calendar
            Calendar to use for business day adjustments

        Returns
        -------
        date
            Rolled date according to convention

        Raises
        ------
        ValueError
            If calendar is None or roll type is invalid
        """
        if calendar is None:
            calendar = Calendar('default', set())
        return self._apply_roll_convention(date_, calendar)

    def _apply_roll_convention(self, date_: date, calendar: Calendar) -> date:
        """Apply the specific roll convention."""
        match self:
            case RollType.FOLLOWING:
                return calendar.adjust_up(date_)
            case RollType.PREVIOUS:
                return calendar.adjust_down(date_)
            case RollType.MODIFIED_FOLLOWING:
                return self._roll_modified_following(date_, calendar)
            case RollType.MODIFIED_PREVIOUS:
                return self._roll_modified_previous(date_, calendar)
            case RollType.MODIFIED_FOLLOWING_EOM:
                return calendar.adjust_down(_get_eom(date_))
            case RollType.UNADJUSTED_EOM:
                return _get_eom(date_)
            case RollType.IMM:
                return _get_imm_date(date_)
            case RollType.CAD_IMM:
                return _get_imm_date(date_) - timedelta(days=2)
            case RollType.NONE:
                return date_
            case _:
                raise ValueError(f'Unknown roll type: {self}')

    def _roll_modified_following(self, date_: date, calendar: Calendar) -> date:
        """Handle modified following roll logic."""
        result = calendar.adjust_up(date_)
        return calendar.adjust_down(date_) if result.month != date_.month else result

    def _roll_modified_previous(self, date_: date, calendar: Calendar) -> date:
        """Handle modified previous roll logic."""
        result = calendar.adjust_down(date_)
        return calendar.adjust_up(date_) if result.month != date_.month else result


def _get_eom(date_: date) -> date:
    """Get end of month date."""
    if date_.month == 12:
        return date(date_.year + 1, 1, 1) - timedelta(days=1)
    else:
        return date(date_.year, date_.month + 1, 1) - timedelta(days=1)


def _get_bom(date_: date) -> date:
    """Get beginning of month date."""
    return date(date_.year, date_.month, 1)


def _get_imm_date(date_: date) -> date:
    """Get IMM date (third Wednesday of the month)."""
    first_day = _get_bom(date_)

    # Find first Wednesday
    while first_day.weekday() != 2:  # 2 = Wednesday
        first_day += timedelta(days=1)

    # Add two weeks to get third Wednesday
    return first_day + timedelta(weeks=2)
