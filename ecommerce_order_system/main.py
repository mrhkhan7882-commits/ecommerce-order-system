"""
main.py
-------
Entry point. Run:  python main.py
"""

from data import get_products, get_orders
from inventory import copy_products
from processing import process_all_orders
from reports import (
    generate_sales_report,
    generate_customer_report,
    generate_product_report,
)
from utils import format_money, format_discount


def print_order_details(processed_orders):
    print("\n---------- ORDER DETAILS ----------")
    for order in processed_orders:
        print(
            f"\n{order['order_id']} | {order['customer']} | {order['status'].upper()}"
        )
        if order["status"] == "rejected":
            for error in order["errors"]:
                print(f"   x {error}")
            continue
        for item in order["items"]:
            print(
                f"   {item['name']}: {item['quantity']} x "
                f"{format_money(item['unit_price'])}"
                f" = {format_money(item['line_total'])}"
            )
        print(f"   Subtotal: {format_money(order['subtotal'])}")
        print(f"   Discount: {format_discount(order['discount'])}")
        print(f"   Shipping: {format_money(order['shipping'])}")
        print(f"   Total   : {format_money(order['total'])}")
        if order["status"] == "pending":
            print("   (pending: not counted as revenue, stock not reduced)")


def print_extra_info(processed_orders, products):
    customer_report = generate_customer_report(processed_orders)
    product_report = generate_product_report(processed_orders, products)

    print("\n---------- EXTRA INFO ----------")
    print("Unique customers :", customer_report["unique_customers"])
    print("Categories sold  :", product_report["categories_sold"])
    print(
        "Spending (paid)  :",
        {
            name: format_money(amount)
            for name, amount in customer_report["spending"].items()
        },
    )
    print("Units sold       :", product_report["units_sold"])
    print("Stock now        :", {pid: info["stock"] for pid, info in products.items()})


def main():
    products = get_products()
    orders = get_orders()

    processed_orders = process_all_orders(orders, products)

    print(generate_sales_report(processed_orders, products))
    print_order_details(processed_orders)
    print_extra_info(processed_orders, products)

    # ---- Demo of **kwargs options (fresh data, so the first run is not affected) ----
    print("\n---------- OPTIONS DEMO (**kwargs) ----------")
    demo_products = copy_products(get_products())
    demo = process_all_orders(
        get_orders()[:1], demo_products, apply_discount=False, include_shipping=False
    )
    print(
        "ORD001 without discount and without shipping ->",
        format_money(demo[0]["total"]),
    )


if __name__ == "__main__":
    main()
