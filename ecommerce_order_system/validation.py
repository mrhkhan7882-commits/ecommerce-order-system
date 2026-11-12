"""
validation.py
-------------
validate_order() NEVER crashes. It never raises an error:
it collects every problem in a list and returns that list.
    empty list  -> order is valid
    list of text -> order is invalid (these are the reasons)

It checks the ORDER and also the PRODUCT DATA the order uses
(price, stock, name, category), because bad product data must not crash the batch.
"""

import math

from config import VALID_PAYMENT_STATUSES
from utils import has_at_most_two_decimals


def describe(value, max_length=60):
    """
    Safe text for an error message: repr(value), shortened if it is very long.
    repr() of a gigantic int (4300+ digits) raises ValueError, and validation
    must NEVER crash, so that case becomes a short placeholder.
    """
    try:
        text = repr(value)
    except (ValueError, RecursionError):
        return f"<{type(value).__name__} too large to show>"
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def is_positive_whole_number(value):
    """True only for ints > 0. bool is excluded (True is technically 1 in Python)."""
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def is_non_negative_whole_number(value):
    """True only for ints >= 0 (used for stock). bool is excluded."""
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def is_non_negative_number(value):
    """True for int/float >= 0 (used for price). bool, nan and inf are excluded."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False

    # Integers have arbitrary precision in Python and are always finite.
    # Passing an extremely large int to math.isfinite() can raise OverflowError
    # because math.isfinite() first converts it to a float.
    if isinstance(value, int):
        return value >= 0

    return math.isfinite(value) and value >= 0


def is_non_empty_text(value):
    """True only for a string that is not empty after strip()."""
    return isinstance(value, str) and value.strip() != ""


def validate_product(product):
    """Return the problems with ONE product dictionary (empty list = fine)."""
    if not isinstance(product, dict):
        return ["product is not a valid dictionary"]

    problems = []
    if not is_non_empty_text(product.get("name")):
        problems.append(
            f"name must be non-empty text, got {describe(product.get('name'))}"
        )
    if not is_non_empty_text(product.get("category")):
        problems.append(
            f"category must be non-empty text, got {describe(product.get('category'))}"
        )
    price = product.get("price")
    if not is_non_negative_number(price) or not has_at_most_two_decimals(price):
        problems.append(
            "price must be a number >= 0 with at most 2 decimal places, "
            f"got {describe(price)}"
        )
    if not is_non_negative_whole_number(product.get("stock")):
        problems.append(
            f"stock must be a whole number >= 0, got {describe(product.get('stock'))}"
        )
    return problems


def validate_order(order, products):
    errors = []

    # 1) The order itself must be a dictionary
    if not isinstance(order, dict):
        return ["Order is not a valid dictionary"]

    # 1b) The product catalogue must be a dictionary too
    if not isinstance(products, dict):
        return ["Products data is not a valid dictionary"]

    # 2) Order ID (same rule as customer: non-empty text)
    if not is_non_empty_text(order.get("order_id")):
        errors.append("Missing or invalid order ID")

    # 3) Customer name
    if not is_non_empty_text(order.get("customer")):
        errors.append("Missing or invalid customer name")

    # 4) Payment status (must be text AND one of the allowed values)
    status = order.get("payment_status")
    if not isinstance(status, str) or status not in VALID_PAYMENT_STATUSES:
        errors.append(f"Invalid payment status: {describe(status)}")

    # 5) Items list must exist and must not be empty
    items = order.get("items")
    if not isinstance(items, list) or len(items) == 0:
        errors.append("Order has no items")
        return errors  # nothing more to check

    # 6) Check every item; also add up the total quantity wanted per product
    requested = {}  # {"P001": 3, ...}  (same product may appear on 2 lines)
    product_is_ok = {}  # {"P001": True/False}  each product's data is checked only ONCE
    for position, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            errors.append(f"Item {position}: not a valid dictionary")
            continue

        product_id = item.get("product_id")
        quantity = item.get("quantity")
        item_ok = True

        if not isinstance(product_id, str) or product_id not in products:
            errors.append(f"Item {position}: unknown product ID {describe(product_id)}")
            item_ok = False
        else:
            # The product exists, but is its DATA usable? (price, stock, name, category)
            if product_id not in product_is_ok:
                problems = validate_product(products[product_id])
                product_is_ok[product_id] = not problems
                if problems:
                    errors.append(
                        f"Product {product_id} has invalid data: " + "; ".join(problems)
                    )
            if not product_is_ok[product_id]:
                item_ok = False

        if not is_positive_whole_number(quantity):
            errors.append(
                f"Item {position}: quantity must be a positive whole number, "
                f"got {describe(quantity)}"
            )
            item_ok = False

        if item_ok:
            requested[product_id] = requested.get(product_id, 0) + quantity

    # 7) Stock check (using the combined quantity per product).
    #    Only products whose data passed validation are in `requested`,
    #    so stock is a valid int here.
    for product_id, total_quantity in requested.items():
        available = products[product_id]["stock"]
        if total_quantity > available:
            name = products[product_id]["name"]
            errors.append(
                f"Insufficient stock for {name} ({product_id}): "
                f"requested {describe(total_quantity)}, available {describe(available)}"
            )

    return errors
