from enum import Enum


class Frequency(Enum):
    """
    Enumeration representing frequency of events.

    Attributes
    ----------
    ONCE : int
        Single occurrence (0)
    ANNUAL : int
        Yearly occurrence (1)
    SEMIANNUAL : int
        Twice per year (2)
    QUARTERLY : int
        Four times per year (4)
    BIMONTHLY : int
        Six times per year (6)
    MONTHLY : int
        Twelve times per year (12)
    BIWEEKLY : int
        Twenty-six times per year (26)
    WEEKLY : int
        Fifty-two times per year (52)
    DAILY : int
        Three hundred sixty-five times per year (365)
    OTHER_FREQUENCY : int
        Special value for other frequencies (999)
    """

    ONCE = 0
    ANNUAL = 1
    SEMIANNUAL = 2
    QUARTERLY = 4
    BIMONTHLY = 6
    MONTHLY = 12
    BIWEEKLY = 26
    WEEKLY = 52
    DAILY = 365
    OTHER_FREQUENCY = 999
