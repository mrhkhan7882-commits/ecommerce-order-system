"""
config.py
---------
All business rules (numbers) are kept in ONE place.
If the business changes a rule (e.g. discount %), we change it only here.
These are constants: we only READ them, we never change them in the code.
"""

# (minimum subtotal, discount rate) -> highest tier first, so the first match wins
DISCOUNT_TIERS = [
    (1000, 0.15),  # >= $1000 -> 15%
    (500, 0.10),  # >= $500  -> 10%
    (200, 0.05),  # >= $200  -> 5%
]

FREE_SHIPPING_MIN = 500  # subtotal >= 500 -> free shipping
SHIPPING_FEE = 20  # otherwise $20

# A set: fast membership check, and no duplicates
VALID_PAYMENT_STATUSES = {"paid", "pending"}

# A product is "low stock" when stock <= this number
LOW_STOCK_THRESHOLD = 10

# An order whose subtotal or total is above this is rejected
# (it is almost certainly a data error).
# It also keeps the sums in the sales report far away from float overflow.
MAX_ORDER_AMOUNT = 1_000_000_000_000  # $1 trillion
