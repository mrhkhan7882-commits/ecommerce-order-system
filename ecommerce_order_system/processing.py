"""
processing.py
-------------
The main business flow for orders.
"""

import math

from calculations import (
    calculate_line_totals,
    calculate_order_subtotal,
    calculate_discount,
    calculate_shipping,
)
from config import MAX_ORDER_AMOUNT
from inventory import update_inventory
from utils import add_amounts
from validation import validate_order

# The only options process_order understands (a set -> easy to compare)
ALLOWED_OPTIONS = {"include_shipping", "apply_discount"}


def build_result(
    order_id, customer, status, items, subtotal, discount, shipping, total, errors
):
    """One place that builds the result dictionary (same keys every time)."""
    return {
        "order_id": order_id,
        "customer": customer,
        "status": status,  # "paid", "pending" or "rejected"
        "items": items,
        "subtotal": subtotal,
        "discount": discount,
        "shipping": shipping,
        "total": total,
        "errors": errors,
    }


def read_options(options):
    """
    Check the **options and return (include_shipping, apply_discount).
    - unknown name  -> ValueError (a typo like 'aply_discount' must not do nothing)
    - not True/False -> TypeError (apply_discount="no" is a non-empty string,
      so it would count as True - a trap!)
    """
    unknown = set(options) - ALLOWED_OPTIONS
    if unknown:
        raise ValueError(f"Unknown option(s): {sorted(unknown)}")

    include_shipping = options.get("include_shipping", True)
    apply_discount = options.get("apply_discount", True)
    for name, value in (
        ("include_shipping", include_shipping),
        ("apply_discount", apply_discount),
    ):
        if not isinstance(value, bool):
            raise TypeError(f"Option {name!r} must be True or False, got {value!r}")
    return include_shipping, apply_discount


def is_finite_amount(value):
    """
    True if `value` is a normal, finite number.
    An int too big for a float (like 10**400) counts as NOT finite:
    math.isfinite() would raise OverflowError for it.
    """
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def clean_text(value):
    """Return the stripped text if `value` is a non-empty string, else None."""
    if isinstance(value, str) and value.strip() != "":
        return value.strip()
    return None


def read_identity(order):
    """
    Safe way to read (order_id, customer) even if the order is broken.
    Each one is stripped text, or None when it is missing / not a non-empty string.
    """
    if isinstance(order, dict):
        return clean_text(order.get("order_id")), clean_text(order.get("customer"))
    return None, None


def process_order(order, products, **options):
    """
    Process ONE order.

    **options lets the caller switch features on/off by name:
        process_order(order, products)                          -> defaults (both True)
        process_order(order, products, apply_discount=False)
        process_order(order, products, include_shipping=False)

    Steps:  validate -> subtotal -> discount -> shipping -> total
            -> update stock (paid only)
    """
    include_shipping, apply_discount = read_options(options)

    # A rejected order never keeps a bad customer value (None, 123 ...):
    # it becomes "UNKNOWN".
    order_id, customer = read_identity(order)
    order_id = order_id or "UNKNOWN"
    customer = customer or "UNKNOWN"

    # --- 1. validate ---
    errors = validate_order(order, products)
    if errors:
        return build_result(order_id, customer, "rejected", [], 0, 0, 0, 0, errors)

    # --- 2. calculate ---
    # Huge prices can overflow: 1e308 * 2 -> inf, and 10**400 cannot even
    # become a float.
    # Such an order is rejected BEFORE any stock is changed.
    try:
        items = calculate_line_totals(order, products)
        subtotal = calculate_order_subtotal(order, products)
        discount = calculate_discount(subtotal) if apply_discount else 0
        shipping = calculate_shipping(subtotal) if include_shipping else 0
        total = add_amounts(subtotal, -discount, shipping)
    except OverflowError:
        return build_result(
            order_id,
            customer,
            "rejected",
            [],
            0,
            0,
            0,
            0,
            ["Calculated total is not a finite number"],
        )

    amounts = [line["line_total"] for line in items] + [
        subtotal,
        discount,
        shipping,
        total,
    ]
    if not all(is_finite_amount(amount) for amount in amounts):
        return build_result(
            order_id,
            customer,
            "rejected",
            [],
            0,
            0,
            0,
            0,
            ["Calculated total is not a finite number"],
        )

    if subtotal > MAX_ORDER_AMOUNT or total > MAX_ORDER_AMOUNT:
        return build_result(
            order_id,
            customer,
            "rejected",
            [],
            0,
            0,
            0,
            0,
            [f"Order amount is above the maximum allowed ({MAX_ORDER_AMOUNT:,})"],
        )

    # --- 3. payment + inventory ---
    status = order["payment_status"]  # "paid" or "pending" (already validated)
    if status == "paid":
        update_inventory(order, products)  # stock reduces ONLY for paid orders
        # NOTE: "pending" orders do NOT reserve stock (see README assumptions).

    return build_result(
        order_id, customer, status, items, subtotal, discount, shipping, total, []
    )


def process_all_orders(orders, products, **options):
    """
    Process orders ONE BY ONE, in order.
    It must be sequential: stock changed by order 1 must be seen by order 2.

    - Options are checked ONCE here, at the top (a typo is a programming error,
      not an order error).
    - An order ID that was already accepted (paid/pending) is rejected as a
      duplicate (case ignored).
    - One broken order can never stop the batch: an unexpected error becomes a
      rejection.
    """
    read_options(options)

    seen_ids = set()  # IDs (lower-cased) of orders that were accepted (paid / pending)
    results = []
    for order in orders:
        order_id, customer = read_identity(order)

        if order_id is not None and order_id.casefold() in seen_ids:
            result = build_result(
                order_id,
                customer or "UNKNOWN",
                "rejected",
                [],
                0,
                0,
                0,
                0,
                [f"Duplicate order ID: {order_id!r} was already processed"],
            )
        else:
            try:
                result = process_order(order, products, **options)
            except (
                Exception
            ) as error:  # safety net: never let one order stop the others
                result = build_result(
                    order_id or "UNKNOWN",
                    customer or "UNKNOWN",
                    "rejected",
                    [],
                    0,
                    0,
                    0,
                    0,
                    [
                        f"Unexpected error while processing order: "
                        f"{type(error).__name__}: {error}"
                    ],
                )

        if order_id is not None and result["status"] != "rejected":
            seen_ids.add(order_id.casefold())  # "ORD001" and "ord001" are the SAME id
        results.append(result)
    return results
