from enum import Enum

from .frequency import Frequency


class TenorUnit(Enum):
    """Units used to describe tenor periods."""

    DAY = 'D'
    WEEK = 'W'
    MONTH = 'M'
    YEAR = 'Y'

    def __str__(self):
        """Return the string representation of the tenor unit."""
        return self.value


class Tenor:
    """Class representing a time tenor (amount + unit)."""

    __slots__ = ['amount', 'unit']

    def __init__(self, amount: int, unit: TenorUnit):
        """
        Initialize a Tenor object.

        Parameters
        ----------
        amount : int
            Integer amount (can be negative)
        unit : TenorUnit
            Unit of the tenor period

        Raises
        ------
        ValueError
            If amount is not an integer or unit is not a TenorUnit
        """
        if not isinstance(amount, int):
            raise ValueError(f'Amount must be an integer, got {type(amount)}')
        if not isinstance(unit, TenorUnit):
            raise ValueError(f'Unit must be a TenorUnit, got {type(unit)}')
        self.amount = amount
        self.unit = unit

    @classmethod
    def from_string(cls, tenor_str: str) -> 'Tenor':
        """Create a Tenor from a string.

        Parameters
        ----------
        tenor_str : str
            String in format "nX" where n is an integer and X is a tenor unit letter

        Returns
        -------
        Tenor
            New Tenor instance

        Raises
        ------
        ValueError
            If string format is invalid
        """
        try:
            amount = int(tenor_str[:-1])
            unit = TenorUnit(tenor_str[-1])
            return cls(amount, unit)
        except (ValueError, IndexError) as e:
            raise ValueError(f'Invalid tenor string format: {tenor_str}') from e

    @classmethod
    def from_frequency(cls, freq: Frequency) -> 'Tenor':
        """Create a Tenor from a Frequency.

        Parameters
        ----------
        freq : Frequency
            Frequency enum value

        Returns
        -------
        Tenor
            New Tenor instance

        Raises
        ------
        ValueError
            If frequency cannot be converted to tenor
        """
        if freq == Frequency.ONCE:
            return cls(0, TenorUnit.YEAR)
        elif freq == Frequency.ANNUAL:
            return cls(1, TenorUnit.YEAR)
        elif freq in (Frequency.SEMIANNUAL, Frequency.QUARTERLY, Frequency.BIMONTHLY, Frequency.MONTHLY):
            return cls(12 // freq.value, TenorUnit.MONTH)
        elif freq in (Frequency.BIWEEKLY, Frequency.WEEKLY):
            return cls(52 // freq.value, TenorUnit.WEEK)
        elif freq == Frequency.DAILY:
            return cls(1, TenorUnit.DAY)
        else:
            raise ValueError(f'Unknown frequency: {freq}')

    def __str__(self) -> str:
        """Return compact string representation."""
        return f'{self.amount}{self.unit}'

    def __repr__(self) -> str:
        """Return the string representation of the Tenor object."""
        return f'Tenor({self.amount}, {self.unit})'

    def __eq__(self, other: 'Tenor') -> bool:
        """Check if two Tenor objects are equal."""
        if not isinstance(other, Tenor):
            return NotImplemented
        if self.amount == 0 and other.amount == 0:
            return True
        try:
            match (self.unit, other.unit):
                case (unit, other_unit) if unit == other_unit:
                    return self.amount == other.amount
                case (TenorUnit.YEAR | TenorUnit.MONTH, TenorUnit.YEAR | TenorUnit.MONTH):
                    return self._convert_to_unit(TenorUnit.MONTH) == other._convert_to_unit(TenorUnit.MONTH)
                case (TenorUnit.WEEK | TenorUnit.DAY, TenorUnit.WEEK | TenorUnit.DAY):
                    return self._convert_to_unit(TenorUnit.DAY) == other._convert_to_unit(TenorUnit.DAY)
                case _:
                    return False
        except ValueError:
            return False

    def __hash__(self) -> int:
        """Return the hash of the Tenor object."""
        return hash((self.amount, self.unit))

    def _convert_to_unit(self, target_unit: TenorUnit, approx: bool = False) -> int:
        """Convert amount to target unit if possible.

        Parameters
        ----------
        target_unit : TenorUnit
            Unit to convert to
        approx : bool, optional
            Whether to allow approximate conversions (for month/year to days), by default False

        Returns
        -------
        int
            Converted amount

        Raises
        ------
        ValueError
            If conversion is not possible or requires approximation when approx=False
        """
        match (self.unit, target_unit):
            case (unit, target) if unit == target:
                return self.amount
            case (TenorUnit.YEAR, TenorUnit.MONTH):
                return self.amount * 12
            case (TenorUnit.WEEK, TenorUnit.DAY):
                return self.amount * 7
            case (TenorUnit.YEAR, TenorUnit.DAY) if approx:
                return int(self.amount * 365.25)
            case (TenorUnit.MONTH, TenorUnit.DAY) if approx:
                return int(self.amount * 30.4375)
            case (TenorUnit.YEAR | TenorUnit.MONTH, TenorUnit.DAY) if not approx:
                raise ValueError(f'Cannot convert {self.unit} to {target_unit} without approximation')
            case _:
                raise ValueError(f'Cannot convert {self.unit} to {target_unit}')

    def __add__(self, other: 'Tenor') -> 'Tenor':
        """
        Add two Tenor objects.

        Parameters
        ----------
        other : Tenor
            The tenor to add to this one

        Returns
        -------
        Tenor
            A new Tenor representing the sum

        Raises
        ------
        ValueError
            If tenors with incompatible units are added
        """
        if not isinstance(other, Tenor):
            return NotImplemented

        if self.amount == 0:
            return Tenor(other.amount, other.unit)
        if other.amount == 0:
            return Tenor(self.amount, self.unit)

        try:
            match (self.unit, other.unit):
                case (unit, other_unit) if unit == other_unit:
                    return Tenor(self.amount + other.amount, self.unit)
                case (TenorUnit.YEAR | TenorUnit.MONTH, TenorUnit.YEAR | TenorUnit.MONTH):
                    months = self._convert_to_unit(TenorUnit.MONTH) + other._convert_to_unit(TenorUnit.MONTH)
                    return Tenor(months, TenorUnit.MONTH)
                case (TenorUnit.WEEK | TenorUnit.DAY, TenorUnit.WEEK | TenorUnit.DAY):
                    days = self._convert_to_unit(TenorUnit.DAY) + other._convert_to_unit(TenorUnit.DAY)
                    return Tenor(days, TenorUnit.DAY)
                case _:
                    raise ValueError(f'Cannot add {self} and {other}')
        except ValueError as e:
            raise ValueError(f'Cannot add {self} and {other}: {e}')

    def __sub__(self, other: 'Tenor') -> 'Tenor':
        """Subtract two Tenor objects."""
        if not isinstance(other, Tenor):
            return NotImplemented
        return self + Tenor(-other.amount, other.unit)

    def __mul__(self, n: int) -> 'Tenor':
        """Multiply a Tenor object by an integer."""
        if not isinstance(n, int):
            return NotImplemented
        return Tenor(self.amount * n, self.unit)

    def __rmul__(self, n: int) -> 'Tenor':
        """Multiply a Tenor object by an integer."""
        return self * n

    def __truediv__(self, n: int) -> 'Tenor':
        """Divide a Tenor object by an integer."""
        if not isinstance(n, int):
            return NotImplemented
        if n == 0:
            raise ZeroDivisionError('Cannot divide tenor by zero')

        if self.amount % n == 0:
            return Tenor(self.amount // n, self.unit)

        match self.unit:
            case TenorUnit.YEAR:
                months = self._convert_to_unit(TenorUnit.MONTH)
                if months % n == 0:
                    return Tenor(months // n, TenorUnit.MONTH)
            case TenorUnit.WEEK:
                days = self._convert_to_unit(TenorUnit.DAY)
                if days % n == 0:
                    return Tenor(days // n, TenorUnit.DAY)

        raise ValueError(f'{self} cannot be divided by {n}')

    def _month_to_frequency(self, amount: int) -> Frequency:
        """Convert month amount to frequency."""
        match amount:
            case 1:
                return Frequency.MONTHLY
            case 2:
                return Frequency.BIMONTHLY
            case 3:
                return Frequency.QUARTERLY
            case 6:
                return Frequency.SEMIANNUAL
            case 12:
                return Frequency.ANNUAL
            case _:
                return Frequency.OTHER

    def to_frequency(self) -> Frequency:
        """Convert tenor to frequency if possible.

        Returns
        -------
            Frequency enum value representing this tenor
        """
        if self.amount == 0:
            return Frequency.ONCE
        if self.amount < 0:
            return Frequency.OTHER

        try:
            match self.unit:
                case TenorUnit.YEAR:
                    return self._month_to_frequency(self._convert_to_unit(TenorUnit.MONTH))
                case TenorUnit.MONTH:
                    return self._month_to_frequency(self.amount)
                case TenorUnit.WEEK:
                    return (
                        Frequency.WEEKLY
                        if self.amount == 1
                        else Frequency.BIWEEKLY
                        if self.amount == 2
                        else Frequency.OTHER
                    )
                case TenorUnit.DAY:
                    return Frequency.DAILY if self.amount == 1 else Frequency.OTHER
        except ValueError:
            return Frequency.OTHER

    def __lt__(self, other: 'Tenor') -> bool:
        """Compare if this tenor is less than another tenor."""
        if not isinstance(other, Tenor):
            return NotImplemented

        try:
            match (self.unit, other.unit):
                case (unit, other_unit) if unit == other_unit:
                    return self.amount < other.amount
                case (TenorUnit.YEAR | TenorUnit.MONTH, TenorUnit.YEAR | TenorUnit.MONTH):
                    return self._convert_to_unit(TenorUnit.MONTH) < other._convert_to_unit(TenorUnit.MONTH)
                case (TenorUnit.WEEK | TenorUnit.DAY, TenorUnit.WEEK | TenorUnit.DAY):
                    return self._convert_to_unit(TenorUnit.DAY) < other._convert_to_unit(TenorUnit.DAY)
                case _:
                    # Allow approximate comparison for different unit types
                    return self._convert_to_unit(TenorUnit.DAY, approx=True) < other._convert_to_unit(
                        TenorUnit.DAY, approx=True
                    )
        except ValueError as e:
            raise ValueError(f'Cannot compare {self} and {other}: {e}')

    def __le__(self, other: 'Tenor') -> bool:
        """Compare if this tenor is less than or equal to another tenor."""
        if not isinstance(other, Tenor):
            return NotImplemented
        return self < other or self == other

    def __gt__(self, other: 'Tenor') -> bool:
        """Compare if this tenor is greater than another tenor."""
        if not isinstance(other, Tenor):
            return NotImplemented
        return not (self <= other)

    def __ge__(self, other: 'Tenor') -> bool:
        """Compare if this tenor is greater than or equal to another tenor."""
        if not isinstance(other, Tenor):
            return NotImplemented
        return not (self < other)
