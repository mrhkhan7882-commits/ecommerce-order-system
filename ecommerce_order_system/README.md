# E-Commerce Order Processing System

Python Intern Real-World Assessment: order validation, discounts, shipping,
payment handling, inventory update and sales report.
Only core Python is used (no classes, no external libraries, no frameworks).

## How to run
Python 3.8+ is required (check with `python --version`). Run these from inside the `ecommerce_order_system` folder.

```
python main.py          # full report + order details
python test_cases.py    # 62 edge-case tests
python legb_demo.py     # LEGB scope demo
```
(On Mac/Linux use `python3`.)

## Project structure
| File | Purpose |
|---|---|
| `config.py` | Business rules (discount tiers, shipping, low-stock limit) |
| `data.py` | Starter products and orders |
| `utils.py` | `add_amounts(*args)`, `multiply_money()`, `round_money()` (exact `Decimal` money maths), `format_money()`, `format_discount()` |
| `calculations.py` | Subtotal, discount, shipping |
| `validation.py` | `validate_order()` - never crashes, checks the order AND its product data, returns list of errors |
| `inventory.py` | Stock update, copy of products |
| `processing.py` | `process_order(order, products, **options)` and `process_all_orders()` |
| `reports.py` | Customer, product and sales report |
| `main.py` | Program entry point |
| `test_cases.py` | Plain `assert` tests |
| `legb_demo.py` | Local / Enclosing / Global / Built-in demo |
| `viva_notes/` | Viva preparation notes |

## Assumptions
- Total = subtotal - discount + shipping. Discount and shipping are decided from the **subtotal**.
- **Revenue** = sum of final totals of **paid** orders (shipping included).
- **Pending** orders are valid but NOT counted in revenue / sales / top customer, and stock is NOT reduced.
- **Rejected** orders: invalid data, stock problem or invalid payment status.
- Orders are processed one by one, so stock reduced by an earlier paid order affects later orders.
- Top customer = highest spending on paid orders. Top product = most units sold in paid orders. Ties are all shown.
- Low stock = stock <= 10 (change `LOW_STOCK_THRESHOLD` in `config.py`).
- **Pending orders do NOT reserve stock.** Stock is checked for a pending order, but only paid orders reduce it,
  so a pending order for 10 laptops and a later paid order for 10 laptops are both accepted.
- **Order ID** must be non-empty text. An ID that was already accepted (paid or pending) is rejected as a duplicate; case and surrounding spaces are ignored ("ORD1", " ord1 " are the same ID).
  A rejected order does not use up its ID, so a corrected order can be sent again with the same ID.
- **Customer** must be non-empty text. Names are stored with spaces removed, and "Ali", " ali " and "ALI" count as ONE customer.
  Only valid (paid / pending) orders appear in the unique-customers list.
- **Product data** used by an order is validated: `name` and `category` non-empty text, `price` a number >= 0,
  `stock` a whole number >= 0. A bad product rejects only the orders that use it; the rest of the batch continues.
- **Options** (`apply_discount`, `include_shipping`) must be exactly `True` or `False` (`"no"` raises `TypeError`),
  and unknown names raise `ValueError`. They are checked once at the top of `process_all_orders`.
- **Payment status** must be exactly `"paid"` or `"pending"` (lower-case). Unlike order IDs and customer names, it is NOT trimmed or case-folded: `"Paid"` and `" paid"` are rejected.
- **Overflow / size limit:** an order whose line total, subtotal, discount, shipping or total is not finite (e.g. `1e308 x 2`, or an integer price like `10**400`), or whose subtotal or total is above `MAX_ORDER_AMOUNT` (1 trillion, in `config.py`), is rejected before stock changes.
- **Money** is calculated with `decimal.Decimal` (in `utils.py`) and rounded to whole cents, half a cent rounds up. Results are returned as plain numbers. A product **price with more than 2 decimal places** (e.g. `199.995`) is rejected, because it could push a subtotal across a discount or free-shipping boundary.
