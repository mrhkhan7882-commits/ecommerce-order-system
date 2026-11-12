"""
test_cases.py
-------------
Simple tests using plain functions and `assert` (no classes, no libraries).
Run:  python test_cases.py
"""

from calculations import (
    calculate_discount,
    calculate_shipping,
    calculate_order_subtotal,
)
from data import get_products, get_orders
from inventory import copy_products
from processing import process_order, process_all_orders
from reports import (
    generate_sales_report,
    generate_product_report,
    generate_customer_report,
)
from utils import add_amounts, format_discount
from validation import validate_order, validate_product, is_non_negative_number


def make_order(items, status="paid", customer="Ali", order_id="T1"):
    return {
        "order_id": order_id,
        "customer": customer,
        "items": items,
        "payment_status": status,
    }


# ------------------------------------------------------------ calculations
def test_discount_boundaries():
    assert calculate_discount(199.99) == 0
    assert calculate_discount(200) == 10  # 5%
    assert calculate_discount(499.99) == 25.0  # 5%
    assert calculate_discount(500) == 50  # 10%
    assert calculate_discount(999) == 99.9  # 10%
    assert calculate_discount(1000) == 150  # 15%


def test_shipping_boundaries():
    assert calculate_shipping(499.99) == 20
    assert calculate_shipping(500) == 0
    assert calculate_shipping(0.01) == 20


def test_subtotal():
    products = get_products()
    order = make_order(
        [{"product_id": "P001", "quantity": 1}, {"product_id": "P002", "quantity": 2}]
    )
    assert calculate_order_subtotal(order, products) == 1250


def test_add_amounts_args():
    assert add_amounts() == 0
    assert add_amounts(5) == 5
    assert add_amounts(100, -15, 20) == 105
    assert add_amounts(*[1.1, 2.2, 3.3]) == 6.6


# -------------------------------------------------------------- validation
def test_unknown_product():
    errors = validate_order(
        make_order([{"product_id": "P999", "quantity": 1}]), get_products()
    )
    assert len(errors) == 1 and "unknown product" in errors[0]


def test_zero_quantity():
    assert validate_order(
        make_order([{"product_id": "P001", "quantity": 0}]), get_products()
    )


def test_negative_quantity():
    assert validate_order(
        make_order([{"product_id": "P001", "quantity": -3}]), get_products()
    )


def test_bad_quantity_types():
    for bad in ["2", 2.5, True, None]:
        assert validate_order(
            make_order([{"product_id": "P001", "quantity": bad}]), get_products()
        ), bad


def test_quantity_more_than_stock():
    errors = validate_order(
        make_order([{"product_id": "P001", "quantity": 11}]), get_products()
    )
    assert "Insufficient stock" in errors[0]


def test_exact_stock_is_allowed():
    assert (
        validate_order(
            make_order([{"product_id": "P001", "quantity": 10}]), get_products()
        )
        == []
    )


def test_same_product_twice_checked_together():
    items = [
        {"product_id": "P001", "quantity": 6},
        {"product_id": "P001", "quantity": 6},
    ]
    assert validate_order(make_order(items), get_products())  # 12 > 10


def test_no_items():
    assert validate_order(make_order([]), get_products())
    assert validate_order(
        {"order_id": "X", "customer": "Ali", "payment_status": "paid"}, get_products()
    )


def test_invalid_payment_status():
    order = make_order([{"product_id": "P001", "quantity": 1}], status="refunded")
    assert any("payment status" in e for e in validate_order(order, get_products()))


def test_empty_products_dictionary():
    errors = validate_order(make_order([{"product_id": "P001", "quantity": 1}]), {})
    assert "unknown product" in errors[0]


def test_garbage_input_does_not_crash():
    for garbage in [None, 5, "text", [], {}]:
        assert validate_order(garbage, get_products())


# -------------------------------------------------------------- processing
def test_paid_order_reduces_stock_and_calculates():
    products = get_products()
    result = process_order(get_orders()[0], products)
    assert result["status"] == "paid"
    assert (
        result["subtotal"],
        result["discount"],
        result["shipping"],
        result["total"],
    ) == (1250, 187.5, 0, 1062.5)
    assert products["P001"]["stock"] == 9 and products["P002"]["stock"] == 48


def test_pending_order_does_not_reduce_stock():
    products = get_products()
    result = process_order(get_orders()[2], products)
    assert result["status"] == "pending"
    assert products["P002"]["stock"] == 50


def test_rejected_order_does_not_reduce_stock():
    products = get_products()
    result = process_order(
        make_order([{"product_id": "P001", "quantity": 99}]), products
    )
    assert result["status"] == "rejected" and products["P001"]["stock"] == 10


def test_options_kwargs():
    order = make_order([{"product_id": "P001", "quantity": 1}])
    full = process_order(order, copy_products(get_products()))
    no_discount = process_order(
        order, copy_products(get_products()), apply_discount=False
    )
    no_shipping = process_order(
        make_order([{"product_id": "P002", "quantity": 1}]),
        copy_products(get_products()),
        include_shipping=False,
    )
    assert full["total"] == 1020
    assert no_discount["total"] == 1200
    assert no_shipping["total"] == 25


def test_unknown_option_raises():
    try:
        process_order(
            make_order([{"product_id": "P001", "quantity": 1}]),
            get_products(),
            aply_discount=False,
        )
    except ValueError:
        return
    raise AssertionError("ValueError expected")


def test_stock_is_updated_between_orders():
    products = get_products()
    orders = [
        make_order([{"product_id": "P001", "quantity": 8}], order_id="A"),
        make_order(
            [{"product_id": "P001", "quantity": 8}], order_id="B"
        ),  # only 2 left now
    ]
    results = process_all_orders(orders, products)
    assert [r["status"] for r in results] == ["paid", "rejected"]


# ----------------------------------------------------------------- reports
def test_full_sample_report():
    products = get_products()
    processed = process_all_orders(get_orders(), products)
    report = generate_sales_report(processed, products)
    assert "Total Orders: 3" in report
    assert "Paid Orders: 2" in report
    assert "Pending Orders: 1" in report
    assert "Rejected Orders: 0" in report
    assert "Total Revenue: $1,510.00" in report  # 1062.5 + 447.5
    assert "Total Discount: $210.00" in report  # 187.5 + 22.5
    assert "Total Shipping: $20.00" in report  # only ORD002 pays shipping
    assert "Top Customer: Ali ($1,062.50)" in report
    assert "Keyboard, Mouse (tie - 2 units each)" in report
    assert "- Laptop (P001): 9 left" in report


def test_empty_orders_list():
    products = get_products()
    report = generate_sales_report([], products)
    assert "Total Orders: 0" in report and "Total Revenue: $0.00" in report
    assert "Top Customer: N/A" in report and "Top Selling Product: N/A" in report


def test_empty_products_and_orders():
    report = generate_sales_report([], {})
    assert "- None" in report


def test_empty_products_with_orders_all_rejected():
    processed = process_all_orders(get_orders(), {})
    assert [o["status"] for o in processed] == ["rejected"] * 3
    assert "Rejected Orders: 3" in generate_sales_report(processed, {})


def test_multiple_orders_same_customer():
    products = get_products()
    orders = [
        make_order(
            [{"product_id": "P004", "quantity": 1}], customer="Sara", order_id="A"
        ),
        make_order(
            [{"product_id": "P003", "quantity": 1}], customer="Sara", order_id="B"
        ),
        make_order(
            [{"product_id": "P002", "quantity": 1}], customer="Omar", order_id="C"
        ),
    ]
    processed = process_all_orders(orders, products)
    report = generate_customer_report(processed)
    assert report["top_customers"] == ["Sara"]
    assert report["unique_customers"] == ["Omar", "Sara"]
    # order A: 300 - 5% (15) + 20 shipping = 305 ; order B: 75 + 20 shipping = 95
    assert report["spending"]["Sara"] == 400.0


def test_tie_in_top_selling_product():
    products = get_products()
    orders = [
        make_order([{"product_id": "P002", "quantity": 2}], order_id="A"),
        make_order([{"product_id": "P003", "quantity": 2}], order_id="B"),
    ]
    report = generate_product_report(process_all_orders(orders, products), products)
    assert report["top_products"] == ["Keyboard", "Mouse"]


def test_no_low_stock_products():
    products = get_products()
    products["P001"]["stock"] = 100
    report = generate_product_report([], products, low_stock_threshold=5)
    assert report["low_stock"] == []


def test_pending_not_in_sales_or_revenue():
    products = get_products()
    processed = process_all_orders(
        [make_order([{"product_id": "P002", "quantity": 5}], status="pending")],
        products,
    )
    assert generate_product_report(processed, products)["units_sold"] == {}
    assert "Total Revenue: $0.00" in generate_sales_report(processed, products)


# ------------------------------------------- fixes from the code review
LAPTOP_ITEM = [{"product_id": "P001", "quantity": 1}]


def test_duplicate_order_id_is_rejected():
    products = get_products()
    orders = get_orders()
    orders.append(dict(orders[0]))  # a copy of ORD001
    results = process_all_orders(orders, products)
    assert [r["status"] for r in results] == ["paid", "paid", "pending", "rejected"]
    assert "Duplicate order ID" in results[3]["errors"][0]
    assert products["P001"]["stock"] == 9  # stock reduced ONCE, not twice
    assert "Total Revenue: $1,510.00" in generate_sales_report(results, products)


def test_rejected_order_does_not_block_same_id_later():
    # first ORD1 is rejected (too many laptops)
    # -> a corrected ORD1 may still be accepted
    orders = [
        make_order([{"product_id": "P001", "quantity": 99}], order_id="ORD1"),
        make_order(LAPTOP_ITEM, order_id="ORD1"),
    ]
    results = process_all_orders(orders, get_products())
    assert [r["status"] for r in results] == ["rejected", "paid"]


def test_missing_or_bad_order_id_is_rejected():
    no_id = {"customer": "Ali", "items": LAPTOP_ITEM, "payment_status": "paid"}
    for bad in [None, "", "   ", 5]:
        order = make_order(LAPTOP_ITEM, order_id=bad)
        assert any("order ID" in e for e in validate_order(order, get_products())), bad
    assert any("order ID" in e for e in validate_order(no_id, get_products()))
    result = process_order(no_id, get_products())
    assert result["status"] == "rejected" and result["order_id"] == "UNKNOWN"


def test_bad_product_data_is_rejected_not_crash():
    base = {"name": "Thing", "price": 10, "category": "Misc", "stock": 5}
    broken = {
        "missing stock": {k: v for k, v in base.items() if k != "stock"},
        "stock as text": dict(base, stock="50"),
        "negative stock": dict(base, stock=-1),
        "missing category": {k: v for k, v in base.items() if k != "category"},
        "price as text": dict(base, price="25"),
        "negative price": dict(base, price=-5),
        "price is nan": dict(base, price=float("nan")),
        "price is bool": dict(base, price=True),
        "missing name": {k: v for k, v in base.items() if k != "name"},
        "product not a dict": "oops",
    }
    for label, product in broken.items():
        products = {"P1": product}
        order = make_order([{"product_id": "P1", "quantity": 1}])
        errors = validate_order(order, products)
        assert errors and "invalid data" in errors[0], label
        assert process_order(order, products)["status"] == "rejected", label


def test_products_not_a_dictionary():
    order = make_order(LAPTOP_ITEM)
    for bad in [None, [], "text", 5]:
        assert validate_order(order, bad) == ["Products data is not a valid dictionary"]


def test_negative_price_is_never_paid():
    products = get_products()
    products["P002"]["price"] = -5
    order = make_order([{"product_id": "P002", "quantity": 1}])
    assert process_order(order, products)["status"] == "rejected"


def test_one_bad_product_does_not_stop_the_batch():
    products = get_products()
    products["P002"]["price"] = "25"  # ORD001 uses Mouse -> rejected
    results = process_all_orders(get_orders(), products)
    assert [r["status"] for r in results] == ["rejected", "paid", "rejected"]
    assert results[0]["order_id"] == "ORD001"  # real ID kept
    assert "invalid data" in results[0]["errors"][0]
    generate_sales_report(results, products)  # report still works


def test_unexpected_error_becomes_rejection_with_real_id():
    # a list-like object with a weird type inside:
    # force a crash in the middle of processing
    class Boom(dict):
        def __getitem__(self, key):
            raise RuntimeError("boom")

    orders = [
        Boom(make_order(LAPTOP_ITEM, order_id="X1")),
        make_order(LAPTOP_ITEM, order_id="X2"),
    ]
    results = process_all_orders(orders, get_products())
    assert results[0]["status"] == "rejected" and results[0]["order_id"] == "X1"
    assert "Unexpected error" in results[0]["errors"][0]
    assert results[1]["status"] == "paid"


def test_rejected_order_with_bad_customer_does_not_crash_report():
    products = get_products()
    for bad_customer in [None, 123, "", "   "]:
        orders = [
            make_order(LAPTOP_ITEM, customer="Ali", order_id="A"),
            {
                "order_id": "B",
                "customer": bad_customer,
                "items": [],
                "payment_status": "paid",
            },
        ]
        processed = process_all_orders(orders, copy_products(products))
        assert (
            processed[1]["status"] == "rejected"
            and processed[1]["customer"] == "UNKNOWN"
        )
        report = generate_sales_report(processed, products)  # must not raise
        assert "Rejected Orders: 1" in report
        assert generate_customer_report(processed)["unique_customers"] == ["Ali"]


def test_unique_customers_exclude_rejected_orders():
    orders = [
        make_order(LAPTOP_ITEM, customer="Ali", order_id="A"),
        make_order(
            [{"product_id": "P999", "quantity": 1}], customer="Ghost", order_id="B"
        ),
    ]
    processed = process_all_orders(orders, get_products())
    assert generate_customer_report(processed)["unique_customers"] == ["Ali"]


def test_apply_discount_must_be_true_or_false():
    order = make_order(LAPTOP_ITEM)
    for bad in ["no", "", 0, 1, None]:
        try:
            process_order(order, get_products(), apply_discount=bad)
        except TypeError:
            continue
        raise AssertionError(f"TypeError expected for apply_discount={bad!r}")
    try:
        process_order(order, get_products(), include_shipping="no")
    except TypeError:
        return
    raise AssertionError("TypeError expected for include_shipping='no'")


def test_options_are_checked_once_at_the_top_of_process_all_orders():
    for orders in [get_orders(), []]:  # even with nothing to process
        try:
            process_all_orders(orders, get_products(), aply_discount=False)
        except ValueError:
            continue
        raise AssertionError("ValueError expected")
    try:
        process_all_orders(get_orders(), get_products(), apply_discount="no")
    except TypeError:
        return
    raise AssertionError("TypeError expected")


def test_customer_names_are_normalised():
    products = get_products()
    orders = [
        make_order(
            [{"product_id": "P004", "quantity": 1}], customer="Ali", order_id="A"
        ),
        make_order(
            [{"product_id": "P004", "quantity": 1}], customer=" ali ", order_id="B"
        ),
        make_order(
            [{"product_id": "P004", "quantity": 1}], customer="ALI", order_id="C"
        ),
    ]
    processed = process_all_orders(orders, products)
    assert all(r["customer"] in ("Ali", "ali", "ALI") for r in processed)
    assert processed[1]["customer"] == "ali"  # stored stripped
    report = generate_customer_report(processed)
    assert report["unique_customers"] == ["Ali"]
    assert list(report["spending"]) == ["Ali"]  # one customer, spending added together
    assert report["top_customers"] == ["Ali"]


def test_zero_discount_is_printed_without_minus():
    assert format_discount(0) == "$0.00"
    assert format_discount(187.5) == "-$187.50"


def test_pending_orders_do_not_reserve_stock():
    # documented assumption: pending 10 laptops, then paid 10 laptops -> both accepted
    products = get_products()
    orders = [
        make_order(
            [{"product_id": "P001", "quantity": 10}], status="pending", order_id="A"
        ),
        make_order(
            [{"product_id": "P001", "quantity": 10}], status="paid", order_id="B"
        ),
    ]
    results = process_all_orders(orders, products)
    assert [r["status"] for r in results] == ["pending", "paid"]
    assert products["P001"]["stock"] == 0


def test_product_report_skips_malformed_catalogue_entries():
    processed = []
    bad_catalogues = [
        None,
        {"P001": None},
        {"P001": {"name": "Laptop", "category": "Electronics", "price": 1200}},
        {"P001": "not a product dictionary"},
    ]
    for catalogue in bad_catalogues:
        report = generate_product_report(processed, catalogue)
        assert report["low_stock"] == []


def test_sales_report_survives_malformed_catalogue_entries():
    processed = []
    for catalogue in [None, {"P001": None}, {"P001": {"stock": "50"}}]:
        report = generate_sales_report(processed, catalogue)
        assert "Low Stock Products:" in report


def test_huge_integer_is_a_valid_non_negative_number():
    assert is_non_negative_number(10**1000) is True
    assert is_non_negative_number(-(10**1000)) is False


def test_non_finite_floats_are_rejected():
    assert is_non_negative_number(float("inf")) is False
    assert is_non_negative_number(float("nan")) is False


def test_duplicate_order_id_ignores_case_and_spaces():
    orders = [
        make_order(LAPTOP_ITEM, order_id="ORD1"),
        make_order(LAPTOP_ITEM, order_id="ord1"),
        make_order(LAPTOP_ITEM, order_id=" ORD1 "),
    ]
    results = process_all_orders(orders, get_products())
    assert [r["status"] for r in results] == ["paid", "rejected", "rejected"]


def test_unique_customers_are_sorted_ignoring_case():
    orders = [
        make_order(LAPTOP_ITEM, customer="zed", order_id="A"),
        make_order(LAPTOP_ITEM, customer="Bob", order_id="B"),
        make_order(LAPTOP_ITEM, customer="adam", order_id="C"),
    ]
    processed = process_all_orders(orders, get_products())
    assert generate_customer_report(processed)["unique_customers"] == [
        "adam",
        "Bob",
        "zed",
    ]


def test_overflowing_float_total_is_rejected():
    products = get_products()
    products["P001"]["price"] = 1e308
    products["P001"]["stock"] = 5
    result = process_order(
        make_order([{"product_id": "P001", "quantity": 2}]), products
    )  # 1e308 * 2 = inf
    assert result["status"] == "rejected"
    assert result["total"] == 0 and "not a finite number" in result["errors"][0]
    assert products["P001"]["stock"] == 5  # stock untouched


def test_huge_integer_total_is_rejected():
    products = get_products()
    products["P001"]["price"] = 10**400
    result = process_order(make_order(LAPTOP_ITEM), products)
    assert result["status"] == "rejected"
    assert "not a finite number" in result["errors"][0]
    assert products["P001"]["stock"] == 10
    batch = process_all_orders([make_order(LAPTOP_ITEM, order_id="X1")], products)
    assert (
        batch[0]["status"] == "rejected"
        and "not a finite number" in batch[0]["errors"][0]
    )


def test_low_stock_boundary_is_inclusive():
    products = {
        "A": {"name": "Edge", "price": 1, "category": "X", "stock": 10},
        "B": {"name": "Above", "price": 1, "category": "X", "stock": 11},
    }
    report = generate_product_report([], products)
    names = [p["name"] if isinstance(p, dict) else p for p in report["low_stock"]]
    assert any("Edge" in str(n) for n in names) and not any(
        "Above" in str(n) for n in names
    )


def test_line_totals_are_rounded_to_cents():
    from calculations import calculate_line_totals

    products = {"A": {"name": "Pen", "price": 0.1, "category": "X", "stock": 9}}
    lines = calculate_line_totals(
        make_order([{"product_id": "A", "quantity": 3}]), products
    )
    assert lines[0]["line_total"] == 0.3


def test_payment_status_is_exact_match():
    for status in ["Paid", " paid", "PAID"]:
        assert validate_order(make_order(LAPTOP_ITEM, status=status), get_products())


def test_order_above_maximum_amount_is_rejected_and_report_stays_finite():
    products = get_products()
    products["P001"]["price"] = 1e300
    products["P001"]["stock"] = 100
    orders = [make_order(LAPTOP_ITEM, order_id=f"BIG{i}") for i in range(3)]
    results = process_all_orders(orders, products)
    assert [r["status"] for r in results] == ["rejected"] * 3
    assert "maximum" in results[0]["errors"][0]
    assert products["P001"]["stock"] == 100
    report = generate_sales_report(results, products)
    assert "inf" not in report and "nan" not in report


def test_price_with_fraction_of_a_cent_is_rejected():
    # 199.995 would round to a $200.00 subtotal and wrongly get the 5% discount.
    for price in [199.995, 499.999, 0.005, 0.015, 1.005, 1e-05]:
        products = get_products()
        products["P002"]["price"] = price
        order = make_order([{"product_id": "P002", "quantity": 1}])
        errors = validate_order(order, products)
        assert any("2 decimal places" in e for e in errors), price
        assert process_order(order, products)["status"] == "rejected"


def test_prices_with_at_most_two_decimals_are_accepted():
    for price in [0, 25, 19.99, 0.01, 199.9, 1200.5]:
        assert (
            validate_product({"name": "X", "category": "C", "price": price, "stock": 1})
            == []
        ), price


def test_money_sum_has_no_float_drift():
    # With plain floats, 1,000 amounts just under the limit were $15.25 off.
    assert add_amounts(*[849999999999.15] * 1000) == 849999999999150.0
    assert add_amounts(*[0.1] * 10) == 1.0


def test_half_cents_round_up_the_same_way_every_time():
    assert calculate_discount(200.1) == 10.01  # 10.005 -> 10.01
    assert calculate_discount(200.3) == 10.02  # 10.015 -> 10.02
    assert calculate_discount(200.2) == 10.01  # 10.01 exactly


def test_gigantic_integers_in_error_messages_do_not_crash():
    # repr() of an int with 4300+ digits raises ValueError; validation must not.
    huge = 10**5000
    bad_orders = [
        make_order([{"product_id": "P001", "quantity": huge}]),
        make_order(LAPTOP_ITEM, status=huge),
        make_order([{"product_id": huge, "quantity": 1}]),
    ]
    for order in bad_orders:
        errors = validate_order(order, get_products())
        assert errors and all(len(error) < 300 for error in errors)
        assert process_order(order, get_products())["status"] == "rejected"
    products = get_products()
    products["P001"]["name"] = huge
    assert validate_product(products["P001"])


def test_very_long_text_is_shortened_in_error_messages():
    order = make_order(LAPTOP_ITEM, status="x" * 5000)
    errors = validate_order(order, get_products())
    assert len(errors) == 1 and len(errors[0]) < 200 and errors[0].endswith("...")


# ------------------------------------------------------------------ runner
def run_all_tests():
    tests = [
        (name, func) for name, func in globals().items() if name.startswith("test_")
    ]
    passed = 0
    for name, func in tests:
        try:
            func()
            print(f"PASS  {name}")
            passed += 1
        except AssertionError as error:
            print(f"FAIL  {name}  {error}")
        except Exception as error:
            # One unexpected exception should not prevent the remaining tests.
            print(f"ERROR {name}  {type(error).__name__}: {error}")
    print(f"\n{passed}/{len(tests)} tests passed")
    return passed == len(tests)


if __name__ == "__main__":
    import sys

    sys.exit(0 if run_all_tests() else 1)
