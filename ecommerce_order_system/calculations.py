"""
calculations.py
---------------
Pure money calculations. No printing, no changing of data.
These functions expect an order that is ALREADY validated.
"""

from config import DISCOUNT_TIERS, FREE_SHIPPING_MIN, SHIPPING_FEE
from utils import add_amounts, multiply_money


def calculate_line_totals(order, products):
    """Price x quantity for EACH item (list comprehension)."""
    return [
        {
            "product_id": item["product_id"],
            "name": products[item["product_id"]]["name"],
            "category": products[item["product_id"]]["category"],
            "quantity": item["quantity"],
            "unit_price": products[item["product_id"]]["price"],
            "line_total": multiply_money(
                products[item["product_id"]]["price"], item["quantity"]
            ),
        }
        for item in order["items"]
    ]


def calculate_order_subtotal(order, products):
    """Complete subtotal = sum of all line totals."""
    lines = calculate_line_totals(order, products)
    line_totals = [line["line_total"] for line in lines]
    return add_amounts(*line_totals)  # * unpacks the list into separate arguments


def get_discount_rate(subtotal):
    """Return the discount RATE (0.15, 0.10, 0.05 or 0)."""
    for minimum, rate in DISCOUNT_TIERS:
        if subtotal >= minimum:
            return rate
    return 0


def calculate_discount(subtotal):
    """Return the discount AMOUNT in dollars."""
    return multiply_money(subtotal, get_discount_rate(subtotal))


def calculate_shipping(subtotal):
    """Free shipping from $500 (based on subtotal), otherwise $20."""
    if subtotal >= FREE_SHIPPING_MIN:
        return 0
    return SHIPPING_FEE
