# 05 - Edge Cases (Assessment mein jo zaroori the)

Har case ka test `test_cases.py` mein hai. Chalane ke liye: `python test_cases.py` (62 tests).

| # | Edge case | Kya hota hai | Test |
|---|---|---|---|
| 1 | Unknown product ID (P999) | Order **rejected**, error "unknown product ID" | test_unknown_product |
| 2 | Quantity = 0 | Rejected | test_zero_quantity |
| 3 | Quantity negative | Rejected | test_negative_quantity |
| 4 | Quantity > stock | Rejected ("Insufficient stock...") | test_quantity_more_than_stock |
| 5 | Order mein items nahi | Rejected ("Order has no items") | test_no_items |
| 6 | Invalid payment status ("refunded") | Rejected | test_invalid_payment_status |
| 7 | Products dictionary khali | Har item "unknown product" -> rejected, crash nahi | test_empty_products_dictionary |
| 8 | Orders list khali | Report sab 0, Top Customer/Product "N/A" | test_empty_orders_list |
| 9 | Ek customer ke kai orders | Spending jama hoti hai, unique customer set mein ek baar | test_multiple_orders_same_customer |
| 10 | Top product mein tie | Dono ke naam dikhte hain | test_tie_in_top_selling_product |
| 11 | Koi low-stock nahi | "- None" print hota hai | test_no_low_stock_products |

## Extra cases jo maine khud sochay (marks ke liye acha hai)
- Quantity string `"2"`, float `2.5`, `True`, `None` -> reject
- Order dictionary hi na ho (`None`, `5`, `"text"`) -> crash nahi
- **Ek hi product do lines mein** (6 + 6 laptop, stock 10) -> quantity jama karke check, reject
- Exact stock (10 maange, 10 hain) -> allowed
- Pehla paid order stock kam kare, doosra usi stock se zyada mange -> doosra reject (sequential processing)
- Galat option naam (`aply_discount`) -> `ValueError` (typo chhupta nahi)
- Pending order: stock nahi ghatta, revenue/sales mein nahi (pending order stock **reserve nahi** karta)
- **Duplicate order ID** -> doosra order rejected (`seen_ids` set), stock/revenue do baar nahi badhte
- **Order ID missing / None / khali** -> rejected (customer jaisa hi check)
- **Product data kharab** (stock/category missing, price `"25"`, negative price, stock `"50"`) -> sirf wohi order rejected, baqi batch chalta hai
- `products=None` -> crash nahi, order rejected
- **Rejected order ka customer `None` / `123`** -> result mein `"UNKNOWN"`, report crash nahi hoti, unique customers mein nahi aata
- `apply_discount="no"` -> `TypeError` (sirf `True`/`False` allowed)
- `"Ali"` aur `" ali "` -> ek hi customer (`strip()` + `casefold()`)
- Report ke liye kharab catalogue entry (stock missing, `products=None`) -> low-stock list us entry ko skip karti hai, report crash nahi hoti
- Price with more than 2 decimals (`199.995`, `0.005`) -> reject (warna subtotal $200.00 ban kar galat 5% discount milta)
- Bohot bara int (4300+ digits) quantity/status/product_id -> reject, error message mein `<int too large to show>` (repr crash nahi karta)
- Price `nan` / `inf` -> reject; bohot bara int price bhi `OverflowError` ke bajaye sahi check hota hai
- Discount 0 ho to `$0.00` print hota hai, `-$0.00` nahi

## Viva mein "crash kyun nahi hota?" ka jawab
`validate_order` koi exception raise nahi karta. Har masla ek list mein jama karta hai. Hum pehle type check karte hain (`isinstance`) phir value check, isliye `None` ya galat type par bhi error nahi aata, bas order reject ho jata hai.
- **Overflow** (`1e308 x 2` = inf, ya integer price `10**400`) -> order reject, stock nahi badalta
- **Payment status** `"Paid"` / `" paid"` -> reject (exact match; ID/customer se alag rule)
