# 01 - Project Overview (Pehle yeh parho)

## Project kya hai?
Ek chhoti e-commerce website ka **order processing logic**. Koi website ya database nahi, sirf Python functions.
Program yeh karta hai:
1. Products aur orders leta hai (dictionaries / lists mein)
2. Har order ko **validate** karta hai (product sahi hai? quantity sahi hai? stock hai?)
3. **Subtotal** nikalta hai (price x quantity)
4. **Discount** lagata hai
5. **Shipping** nikalta hai
6. **Payment status** dekhta hai (paid / pending)
7. Sirf kamyab **paid** order par **stock kam** karta hai
8. Aakhir mein **Sales Report** print karta hai

## Sir ko 30 second mein kaise batana hai
> "Sir, yeh project orders ko process karta hai. Pehle har order validate hota hai, phir subtotal, discount aur shipping calculate hoti hai. Agar order paid hai to stock kam hota hai aur revenue mein count hota hai. Pending order revenue mein count nahi hota aur stock bhi kam nahi hota. Invalid order reject ho jata hai lekin program crash nahi hota. Aakhir mein sales report banti hai. Maine code ko functions aur alag files mein toda hai taake saaf aur maintainable rahe."

## Flow (ek order ka safar)
```
order aata hai
   |
validate_order()  --- errors? ---> status = "rejected"  (stock nahi ghatta)
   | (sab theek)
calculate subtotal -> discount -> shipping -> total
   |
payment_status ?
   |-- "paid"    -> stock kam hota hai, revenue mein count
   |-- "pending" -> stock NAHI ghatta, revenue mein count NAHI
```

## Files ka naqsha
| File | Ek line mein kaam |
|---|---|
| config.py | Business rules ke numbers (15%, 10%, $20 ...) |
| data.py | Starter products/orders |
| utils.py | Chhote helpers: add_amounts(*args), format_money() |
| calculations.py | Subtotal, discount, shipping |
| validation.py | Order check karna |
| inventory.py | Stock update |
| processing.py | Ek order process karna (**kwargs yahan hai) |
| reports.py | Reports (lambda, set, closure yahan hain) |
| main.py | Program start karna |
| test_cases.py | Edge cases test |
| legb_demo.py | LEGB samjhane ke liye |

## Sample output ke numbers (yaad kar lo)
| Order | Subtotal | Discount | Shipping | Total | Status |
|---|---|---|---|---|---|
| ORD001 (Ali) | 1250 | 187.50 (15%) | 0 | 1062.50 | paid |
| ORD002 (Ahmed) | 450 | 22.50 (5%) | 20 | 447.50 | paid |
| ORD003 (Ali) | 125 | 0 | 20 | 145 | pending (count nahi) |

- Total Revenue = 1062.50 + 447.50 = **$1,510.00**
- Total Discount = 187.50 + 22.50 = **$210.00**
- Total Shipping = 0 + 20 = **$20.00**
- Top Customer = **Ali** ($1062.50)
- Top Product = **Keyboard aur Mouse (tie, 2-2 units)**
- Low stock = **Laptop (9 bacha)**
