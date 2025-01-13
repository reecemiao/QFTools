from datetime import date

import pytest

from qftools.date.calendar import Calendar
from qftools.date.roll import RollType, _get_bom, _get_eom, _get_imm_date


@pytest.fixture
def calendar():
    """Create a test calendar with weekends and some holidays."""
    holidays = {
        date(2024, 1, 1),  # New Year's Day
        date(2024, 12, 25),  # Christmas
    }
    return Calendar('test', holidays)


def test_roll_following(calendar):
    """Test FOLLOWING roll convention."""
    # Friday to Monday
    assert RollType.FOLLOWING.roll(date(2024, 1, 5), calendar) == date(2024, 1, 5)
    # Saturday to Monday
    assert RollType.FOLLOWING.roll(date(2024, 1, 6), calendar) == date(2024, 1, 8)
    # Holiday to next business day
    assert RollType.FOLLOWING.roll(date(2024, 1, 1), calendar) == date(2024, 1, 2)


def test_roll_previous(calendar):
    """Test PREVIOUS roll convention."""
    # Monday to Monday
    assert RollType.PREVIOUS.roll(date(2024, 1, 8), calendar) == date(2024, 1, 8)
    # Saturday to Friday
    assert RollType.PREVIOUS.roll(date(2024, 1, 6), calendar) == date(2024, 1, 5)
    # Holiday to previous business day
    assert RollType.PREVIOUS.roll(date(2024, 1, 1), calendar) == date(2023, 12, 29)


def test_roll_modified_following(calendar):
    """Test MODIFIED_FOLLOWING roll convention."""
    # Regular case - rolls forward
    assert RollType.MODIFIED_FOLLOWING.roll(date(2024, 1, 6), calendar) == date(2024, 1, 8)
    # Month boundary case - rolls backward
    assert RollType.MODIFIED_FOLLOWING.roll(date(2024, 1, 31), calendar) == date(2024, 1, 31)
    assert RollType.MODIFIED_FOLLOWING.roll(date(2024, 3, 30), calendar) == date(2024, 3, 29)


def test_roll_modified_previous(calendar):
    """Test MODIFIED_PREVIOUS roll convention."""
    # Regular case - rolls backward
    assert RollType.MODIFIED_PREVIOUS.roll(date(2024, 1, 6), calendar) == date(2024, 1, 5)
    # Month boundary case - rolls forward
    assert RollType.MODIFIED_PREVIOUS.roll(date(2024, 2, 1), calendar) == date(2024, 2, 1)


def test_roll_modified_following_eom(calendar):
    """Test MODIFIED_FOLLOWING_EOM roll convention."""
    # End of month cases
    assert RollType.MODIFIED_FOLLOWING_EOM.roll(date(2024, 1, 31), calendar) == date(2024, 1, 31)
    assert RollType.MODIFIED_FOLLOWING_EOM.roll(date(2024, 2, 29), calendar) == date(2024, 2, 29)
    # Mid-month case still goes to EOM
    assert RollType.MODIFIED_FOLLOWING_EOM.roll(date(2024, 1, 15), calendar) == date(2024, 1, 31)


def test_roll_unadjusted_eom():
    """Test UNADJUSTED_EOM roll convention."""
    assert RollType.UNADJUSTED_EOM.roll(date(2024, 1, 15), None) == date(2024, 1, 31)
    assert RollType.UNADJUSTED_EOM.roll(date(2024, 2, 1), None) == date(2024, 2, 29)
    assert RollType.UNADJUSTED_EOM.roll(date(2024, 12, 10), None) == date(2024, 12, 31)


def test_roll_imm():
    """Test IMM roll convention."""
    # Third Wednesday of month
    assert RollType.IMM.roll(date(2024, 1, 1), None) == date(2024, 1, 17)
    assert RollType.IMM.roll(date(2024, 2, 1), None) == date(2024, 2, 21)
    assert RollType.IMM.roll(date(2024, 3, 1), None) == date(2024, 3, 20)


def test_roll_cad_imm():
    """Test CAD_IMM roll convention."""
    # Third Wednesday minus 2 days
    assert RollType.CAD_IMM.roll(date(2024, 1, 1), None) == date(2024, 1, 15)
    assert RollType.CAD_IMM.roll(date(2024, 2, 1), None) == date(2024, 2, 19)
    assert RollType.CAD_IMM.roll(date(2024, 3, 1), None) == date(2024, 3, 18)


def test_roll_none(calendar):
    """Test NONE roll convention."""
    test_date = date(2024, 1, 1)
    assert RollType.NONE.roll(test_date, calendar) == test_date


def test_helper_functions():
    """Test roll helper functions."""
    test_date = date(2024, 1, 15)

    # Test end of month
    assert _get_eom(test_date) == date(2024, 1, 31)
    assert _get_eom(date(2024, 2, 1)) == date(2024, 2, 29)
    assert _get_eom(date(2024, 12, 1)) == date(2024, 12, 31)

    # Test beginning of month
    assert _get_bom(test_date) == date(2024, 1, 1)
    assert _get_bom(date(2024, 12, 31)) == date(2024, 12, 1)

    # Test IMM date
    assert _get_imm_date(test_date) == date(2024, 1, 17)
    assert _get_imm_date(date(2024, 2, 1)) == date(2024, 2, 21)
