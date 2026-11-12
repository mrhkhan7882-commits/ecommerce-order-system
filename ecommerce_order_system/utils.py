"""
utils.py
--------
Small helper functions used everywhere.

Money is calculated with decimal.Decimal (exact decimal arithmetic) and handed
back as a normal number rounded to cents. Plain floats cannot store 0.1 exactly,
so adding thousands of float amounts slowly drifts away from the true total.
"""

from contextlib import contextmanager
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation, localcontext

CENT = Decimal("0.01")
# Very large numbers (like 1e308 or 10**400) must not hit Decimal's default
# 28-digit limit; the order-amount limit in processing.py rejects them later.
MONEY_PRECISION = 2000


@contextmanager
def money_context():
    """High precision, and inf - inf gives nan (like floats) instead of raising."""
    with localcontext() as context:
        context.prec = MONEY_PRECISION
        context.traps[InvalidOperation] = False
        yield


def to_decimal(amount):
    """int -> exact Decimal; float -> Decimal of its shortest text (0.1 -> 0.1)."""
    if isinstance(amount, int):
        return Decimal(amount)
    return Decimal(repr(amount))


def round_money(value):
    """Round a Decimal to whole cents (half cents go UP) and return a number."""
    if value.is_finite():
        with money_context():
            value = value.quantize(CENT, rounding=ROUND_HALF_UP)
    return float(value)


def multiply_money(amount, factor):
    """amount x factor (price x quantity, subtotal x discount rate), in cents."""
    with money_context():
        return round_money(to_decimal(amount) * to_decimal(factor))


def has_at_most_two_decimals(amount):
    """True if the number has no fraction of a cent (19.99 yes, 19.999 no)."""
    return to_decimal(amount).as_tuple().exponent >= -2


def add_amounts(*amounts):
    """
    Add ANY number of money values and round to 2 decimals.

    *args means: the function can receive 1, 2, 10 ... values.
    Python packs them into a tuple called `amounts`.

    Examples:
        add_amounts(10, 5)            -> 15
        add_amounts(100, -15, 20)     -> 105   (negative = discount)
        add_amounts(*[1.1, 2.2, 3.3]) -> 6.6   (the * unpacks a list)
    """
    with money_context():
        total = sum((to_decimal(amount) for amount in amounts), Decimal(0))
        return round_money(total)


def format_money(amount):
    """1062.5 -> '$1,062.50'"""
    return f"${amount:,.2f}"


def format_discount(amount):
    """50 -> '-$50.00' but 0 -> '$0.00' (never '-$0.00')."""
    if amount == 0:
        return format_money(0)
    return f"-{format_money(amount)}"
