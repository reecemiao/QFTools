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
    OTHER = 999
