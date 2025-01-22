from enum import Enum


class Frequency(Enum):
    """
    Enumeration representing frequency of events.

    Attributes
    ----------
    ONCE : int
        Single occurrence (0)
    BIANNUAL : int
        Bi-yearly occurrences (-2)
    ANNUAL : int
        Yearly occurrence (1)
    SEMIANNUAL : int
        Semi-annual occurrences (2)
    QUARTERLY : int
        Quarterly occurrences (4)
    BIMONTHLY : int
        Bi-monthly occurrences (6)
    MONTHLY : int
        Monthly occurrences (12)
    BIWEEKLY : int
        Bi-weekly occurrences (26)
    WEEKLY : int
        Weekly occurrences (52)
    DAILY : int
        Daily occurrences (365)
    CONTINUOUS : int
        Continuous occurrences (999)
    OTHER : int
        Other occurrences (9999)
    """

    ONCE = 0
    BIANNUAL = -2
    ANNUAL = 1
    SEMIANNUAL = 2
    QUARTERLY = 4
    BIMONTHLY = 6
    MONTHLY = 12
    BIWEEKLY = 26
    WEEKLY = 52
    DAILY = 365
    CONTINUOUS = 999
    OTHER = 9999

    def annual_frequency(self) -> float:
        """
        Return the number of occurrences per year.

        Returns
        -------
        float
            Number of times the frequency occurs in a year.
            For BIANNUAL returns 0.5, for ANNUAL returns 1, etc.
        """
        if self == Frequency.ONCE or self == Frequency.OTHER:
            return float('nan')
        if self == Frequency.CONTINUOUS:
            return float('inf')
        if self == Frequency.BIANNUAL:
            return 0.5
        return abs(float(self.value))

    def period_months(self) -> float:
        """
        Return the number of months per period.

        Returns
        -------
        float
            Number of months between each occurrence.
            For ANNUAL returns 12, for SEMIANNUAL returns 6, etc.
        """
        if self == Frequency.ONCE or self == Frequency.OTHER:
            return float('nan')
        if self == Frequency.CONTINUOUS:
            return 0.0
        if self == Frequency.BIANNUAL:
            return 24.0
        if self == Frequency.BIWEEKLY:
            return 12 / 26
        if self == Frequency.WEEKLY:
            return 12 / 52
        if self == Frequency.DAILY:
            return 12 / 365
        return 12 / self.value
