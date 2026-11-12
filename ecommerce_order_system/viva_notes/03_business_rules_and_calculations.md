# 03 - Business Rules aur Calculations

## Discount (subtotal par)
| Subtotal | Discount |
|---|---|
| >= 1000 | 15% |
| >= 500 | 10% |
| >= 200 | 5% |
| baqi | 0% |

Boundary examples: 199.99 -> 0% | 200 -> 5% | 500 -> 10% | 1000 -> 15%

## Shipping (subtotal par, discount se pehle wala)
- subtotal >= 500 -> **free**
- subtotal < 500 -> **$20**

## Total formula
```
total = subtotal - discount + shipping
```

## Example (ORD002)
- Keyboard 2 x 75 = 150, Monitor 1 x 300 = 300
- Subtotal = 450
- Discount: 450 >= 200 -> 5% = 22.50
- Shipping: 450 < 500 -> 20
- Total = 450 - 22.50 + 20 = **447.50**

## Payment rules
| Status | Revenue? | Stock kam? | Report mein |
|---|---|---|---|
| paid | Haan | Haan | Paid Orders |
| pending | Nahi | Nahi | Pending Orders |
| invalid (jaise "refunded") | Nahi | Nahi | Rejected Orders |
| validation fail | Nahi | Nahi | Rejected Orders |

## Meri assumptions (sir pooche to yeh batana)
1. **Revenue** = paid orders ka final total (shipping shamil, discount ke baad).
2. Discount aur shipping dono **subtotal** se decide hote hain (assessment mein yahi likha hai).
3. **Top customer** = paid orders mein sab se zyada kharch karne wala.
4. **Top selling product** = paid orders mein sab se zyada units. Agar barabar hon to **sab tie wale dikhaye** (starter data mein Mouse aur Keyboard dono 2-2 hain).
5. **Low stock** = stock <= 10 (config.py mein badal sakte hain).
6. Pending order ka stock check hota hai (validation), lekin stock kam nahi hota. Yaani **pending order stock reserve nahi karta**: pending 10 laptop ke baad paid 10 laptop bhi accept ho jata hai.

## Rounding
Paise ke hisaab mein float ki choti galtiyan aa sakti hain (jaise 0.1 + 0.2), isliye hisab `Decimal` mein hota hai (`add_amounts`, `multiply_money` in `utils.py`) aur cents tak round hota hai (half cent upar).
Price mein 2 se zyada decimal places (jaise `199.995`) validation mein reject hote hain, taake rounding discount/shipping ki hadd paar na karwa de.
