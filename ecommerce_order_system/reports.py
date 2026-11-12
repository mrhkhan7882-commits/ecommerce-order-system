"""
reports.py
----------
Build the customer report, product report and the final sales report text.
Only PAID orders count as revenue / sales.
"""

from config import LOW_STOCK_THRESHOLD
from utils import add_amounts, format_money
from validation import validate_product


def get_paid_orders(processed_orders):
    return [order for order in processed_orders if order["status"] == "paid"]


def get_accepted_orders(processed_orders):
    """Valid orders only (paid or pending). Rejected ones never count as customers."""
    return [
        order for order in processed_orders if order["status"] in ("paid", "pending")
    ]


def build_customer_names(processed_orders):
    """
    Group customers ignoring case and spaces: "Ali", " ali " and "ALI" are ONE customer.
    Returns {"ali": "Ali"}  ->  lowercase key -> the name as it first appeared.
    """
    names = {}
    for order in get_accepted_orders(processed_orders):
        name = order["customer"].strip()
        names.setdefault(name.casefold(), name)
    return names


def get_unique_customers(processed_orders):
    """Unique customers of VALID orders only (a rejected order may have a bad name)."""
    return sorted(build_customer_names(processed_orders).values(), key=str.casefold)


def make_low_stock_checker(threshold):
    """
    Closure example (the 'E' in LEGB - Enclosing scope).
    The inner function remembers `threshold` from the outer function,
    so we don't need a global variable.
    """

    def is_low(product):
        return product["stock"] <= threshold

    return is_low


# ---------------------------------------------------------------- customers
def generate_customer_report(processed_orders):
    """Total spending per customer (paid orders only) + top customer(s)."""
    names = build_customer_names(processed_orders)
    spending = {}
    for order in get_paid_orders(processed_orders):
        name = names[
            order["customer"].strip().casefold()
        ]  # same customer -> same display name
        spending[name] = add_amounts(spending.get(name, 0), order["total"])

    # lambda: sort by spending (high -> low), then by name (A -> Z) so ties are stable
    ranking = sorted(spending.items(), key=lambda pair: (-pair[1], pair[0]))

    if ranking:
        top_spend = ranking[0][1]
        top_customers = [
            name for name, amount in ranking if amount == top_spend
        ]  # handles ties
    else:
        top_spend, top_customers = 0, []

    return {
        "spending": spending,
        "ranking": ranking,
        "top_customers": top_customers,
        "top_spend": top_spend,
        "unique_customers": get_unique_customers(processed_orders),
    }


# ----------------------------------------------------------------- products
def generate_product_report(
    processed_orders, products, low_stock_threshold=LOW_STOCK_THRESHOLD
):
    """Units sold per product (paid orders only), top seller(s), low-stock list."""
    units_sold = {}
    names = {}
    categories_sold = set()

    for order in get_paid_orders(processed_orders):
        for item in order["items"]:
            product_id = item["product_id"]
            units_sold[product_id] = units_sold.get(product_id, 0) + item["quantity"]
            names[product_id] = item["name"]
            categories_sold.add(item["category"])

    ranking = sorted(units_sold.items(), key=lambda pair: (-pair[1], names[pair[0]]))

    if ranking:
        top_units = ranking[0][1]
        top_products = [
            names[pid] for pid, units in ranking if units == top_units
        ]  # ties
    else:
        top_units, top_products = 0, []

    is_low = make_low_stock_checker(low_stock_threshold)
    low_stock = []

    # The catalogue may contain malformed entries (or may not be a dictionary).
    # Reports must remain available even when validation has rejected bad data.
    if isinstance(products, dict):
        for product_id, info in products.items():
            if validate_product(info):
                continue
            if is_low(info):
                low_stock.append((product_id, info["name"], info["stock"]))

    low_stock.sort(key=lambda row: (row[2], row[1]))  # lowest stock first

    return {
        "units_sold": units_sold,
        "ranking": ranking,
        "top_products": top_products,
        "top_units": top_units,
        "categories_sold": sorted(categories_sold),
        "low_stock": low_stock,
    }


# -------------------------------------------------------------------- sales
def generate_sales_report(
    processed_orders, products, low_stock_threshold=LOW_STOCK_THRESHOLD
):
    """Return the final report as ONE text string in the required format."""
    paid = get_paid_orders(processed_orders)
    pending = [o for o in processed_orders if o["status"] == "pending"]
    rejected = [o for o in processed_orders if o["status"] == "rejected"]

    total_revenue = add_amounts(*[o["total"] for o in paid])
    total_discount = add_amounts(*[o["discount"] for o in paid])
    total_shipping = add_amounts(*[o["shipping"] for o in paid])

    customer_report = generate_customer_report(processed_orders)
    product_report = generate_product_report(
        processed_orders, products, low_stock_threshold
    )

    # --- top customer text ---
    if customer_report["top_customers"]:
        names = ", ".join(customer_report["top_customers"])
        top_customer = f"{names} ({format_money(customer_report['top_spend'])})"
    else:
        top_customer = "N/A"

    # --- top product text (tie-aware) ---
    if product_report["top_products"]:
        names = ", ".join(product_report["top_products"])
        if len(product_report["top_products"]) > 1:
            top_product = f"{names} (tie - {product_report['top_units']} units each)"
        else:
            top_product = f"{names} ({product_report['top_units']} units)"
    else:
        top_product = "N/A"

    # --- low stock lines ---
    if product_report["low_stock"]:
        low_stock_lines = [
            f"- {name} ({pid}): {stock} left"
            for pid, name, stock in product_report["low_stock"]
        ]
    else:
        low_stock_lines = ["- None"]

    lines = (
        [
            "========== SALES REPORT ==========",
            "",
            f"Total Orders: {len(processed_orders)}",
            f"Paid Orders: {len(paid)}",
            f"Pending Orders: {len(pending)}",
            f"Rejected Orders: {len(rejected)}",
            "",
            f"Total Revenue: {format_money(total_revenue)}",
            f"Total Discount: {format_money(total_discount)}",
            f"Total Shipping: {format_money(total_shipping)}",
            "",
            f"Top Customer: {top_customer}",
            f"Top Selling Product: {top_product}",
            "",
            "Low Stock Products:",
        ]
        + low_stock_lines
        + [
            "",
            "==================================",
        ]
    )
    return "\n".join(lines)
