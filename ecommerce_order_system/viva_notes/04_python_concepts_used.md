# 04 - Python Concepts Jo Project Mein Use Huay

Har concept: **kya hai -> project mein kahan -> example**

## 1. Functions
Code ko chhote logical tukron mein todna. Har function ek hi kaam karta hai.
Kahan: poore project mein (calculate_discount, validate_order ...).

## 2. `*args`
Function ko kitni bhi positional values dene ki ijazat. Andar woh **tuple** ban jati hain.
Kahan: `utils.add_amounts(*amounts)`.
```python
add_amounts(100, -15, 20)           # 105
add_amounts(*[10, 20, 30])          # list ko unpack karke bhejna
```

## 3. `**kwargs`
Naam wale options kitne bhi. Andar woh **dictionary** ban jate hain.
Kahan: `processing.process_order(order, products, **options)`.
```python
process_order(order, products, apply_discount=False)
```
`options.get("apply_discount", True)` -> option na diya ho to default True.

## 4. Lambda
Chhota unnamed function. Sorting ke liye `key=` mein.
Kahan: reports.py
```python
sorted(spending.items(), key=lambda pair: (-pair[1], pair[0]))
```
Matlab: pehle amount ke hisaab se **bara -> chhota** (minus laga kar), barabar ho to naam A->Z.

## 5. List comprehension
```python
paid = [order for order in processed_orders if order["status"] == "paid"]
```
Loop + append ka chhota aur saaf tareeqa.

## 6. Dictionary comprehension
```python
{pid: dict(info) for pid, info in products.items()}   # inventory.copy_products
```

## 7. Set
Duplicates khatam, aur `in` check tez.
- `VALID_PAYMENT_STATUSES = {"paid", "pending"}`
- `{order["customer"] for order in processed_orders}` -> unique customers
- `set(options) - ALLOWED_OPTIONS` -> galat options dhoondna (set difference)
- `categories_sold` -> unique categories

## 8. LEGB (variable dhoondne ka order)
**L**ocal -> **E**nclosing -> **G**lobal -> **B**uilt-in

| Scope | Matlab | Example |
|---|---|---|
| Local | function ke andar ka variable | `shipping_fee = 5` function ke andar |
| Enclosing | bahar wale function ka variable | `discount_rate` jo `inner()` use karta hai |
| Global | file ke upar wala variable | `shipping_fee = 20` |
| Built-in | Python ke apne naam | `len`, `sum`, `max` |

- `legb_demo.py` mein har ek ka demo hai (plus `global` aur `nonlocal` keywords).
- Asal project mein **global variables par dependency nahi**: data function arguments se pass hota hai.
- `reports.make_low_stock_checker(threshold)` **closure** hai: andar wala `is_low()` bahar wale function ka `threshold` yaad rakhta hai.

## 9. Dictionary `.get()`
`requested.get(product_id, 0) + quantity` -> key na ho to 0 se shuru. KeyError nahi aata.

## 10. `isinstance()`
Type check: `isinstance(quantity, int)`. Bool alag se reject kiya kyunke Python mein `True == 1`.

## 11. f-strings
`f"Total: {total}"`, `f"{amount:,.2f}"` -> 1,062.50

## 12. `if __name__ == "__main__":`
File direct chalane par hi code chale, import par nahi.

## 13. `enumerate(items, start=1)`
Loop mein item ke saath position number (error message mein "Item 2: ...").

## 14. Mutable objects
Dictionary function mein pass hoti hai to **wahi object** badalta hai (reference). Isi liye `update_inventory` original `products` ka stock kam kar deta hai.
