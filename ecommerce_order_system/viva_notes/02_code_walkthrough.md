# 02 - Code Walkthrough (File by file)

## config.py
Saare business numbers ek jagah. Agar kal discount 15% se 20% karna ho to sirf yahan badlo.
- `DISCOUNT_TIERS` : list of tuples `(minimum, rate)`. Upar se neeche check hota hai, pehla match jeetta hai.
- `VALID_PAYMENT_STATUSES` : **set** `{"paid","pending"}`.

## data.py
Products aur orders **functions** ke andar hain (`get_products()`, `get_orders()`), global variable nahi.
Faida: har baar fresh data milta hai, purana change hua data dobara use nahi hota.

## utils.py
- `add_amounts(*amounts)` : **\*args** wala function. Kitni bhi values le sakta hai, jama karke round karta hai.
  `add_amounts(subtotal, -discount, shipping)` -> total.
- `multiply_money(price, quantity)` : price x quantity (ya subtotal x discount rate) `Decimal` mein, cents tak round (half cent upar). `round_money()` isi ka rounding wala hissa hai.
- `format_money(1062.5)` -> `"$1,062.50"`.

## calculations.py
- `calculate_line_totals(order, products)` : har item ka price x quantity (**list comprehension**).
- `calculate_order_subtotal()` : line totals ko jama karta hai.
- `get_discount_rate(subtotal)` : tiers par loop; pehla match return.
- `calculate_discount(subtotal)` : discount ki **amount** (rate x subtotal).
- `calculate_shipping(subtotal)` : >= 500 free, warna 20.
> Yeh functions maan kar chalte hain ke order pehle validate ho chuka hai.

## validation.py  (sabse important)
`validate_order(order, products)` **kabhi crash nahi karta**. Yeh errors ki **list** return karta hai:
- khali list `[]` = order theek
- list mein text = order mein masla

Checks (order mein):
1. Order dictionary hai?
2. Customer ka naam hai?
3. payment_status "paid" ya "pending" hai?
4. Items list hai aur khali to nahi?
5. Har item: product_id exist karta hai? quantity positive **int** hai? (string, float, True bhi reject)
6. Stock check: agar ek hi product do lines mein ho to quantity **jama** karke stock se compare hoti hai.

## inventory.py
- `update_inventory(order, products)` : stock kam karta hai. Dictionary mutable hai, isliye original products badal jata hai.
- `copy_products()` : **dictionary comprehension** se independent copy (tests ke liye).

## processing.py
`process_order(order, products, **options)`:
1. Options check: `include_shipping`, `apply_discount` (default dono True). Galat naam (typo) par `ValueError`.
2. Validate. Errors hon to `status="rejected"` result.
3. Calculate: subtotal, discount (agar apply_discount), shipping (agar include_shipping), total.
4. Agar `paid` -> `update_inventory()`. Pending/rejected par stock nahi ghatta.
5. Result dictionary return.

`process_all_orders()` orders ko **ek ek karke (sequential)** process karta hai, kyunke pehle order ne stock kam kiya to doosre order ko naya stock dikhna chahiye.

## reports.py
- `get_paid_orders()` : sirf paid orders.
- `get_unique_customers()` : **set comprehension** - Ali do baar order kare to ek hi gina jata hai.
- `make_low_stock_checker(threshold)` : **closure** (LEGB ka "E").
- `generate_customer_report()` : har customer ka kharcha (paid only), **lambda** se sort, tie handle.
- `generate_product_report()` : units sold, top product (tie-aware), low-stock list, categories (**set**).
- `generate_sales_report()` : final text report jo sir ke diye format mein hai.

## main.py
Data lo -> `process_all_orders` -> report print -> order details -> extra info -> **kwargs demo.
`if __name__ == "__main__":` ka matlab: file direct run ho tabhi `main()` chale; import par na chale.
