# 06 - Viva Questions aur Jawab

## A. Project ke barey mein

**Q1. Aapka project kya karta hai?**
Orders validate karta hai, subtotal/discount/shipping nikalta hai, paid orders par stock kam karta hai aur sales report banata hai.

**Q2. Aapne code alag files mein kyun toda?**
Har file ka ek kaam hai (calculations, validation, reports...). Isse code padhna, test karna aur badalna aasaan hota hai. Rule badalna ho to `config.py`, report badalni ho to `reports.py`.

**Q3. Pending order ke saath kya hota hai?**
Order valid hota hai aur uske amounts nikalte hain, lekin woh revenue/sales/top customer mein count nahi hota aur stock kam nahi hota, kyunke payment abhi nahi hui.

**Q4. Stock kab kam hota hai?**
Sirf jab order validate ho **aur** paid ho. `process_order` mein `if status == "paid": update_inventory(...)`.

**Q5. Orders sequential kyun process kiye?**
Pehle paid order se stock kam hota hai. Agar doosra order usi product ka ho to usay naya stock dikhna chahiye, warna overselling ho sakti hai.

**Q6. Invalid order par crash kyun nahi hota?**
`validate_order` exception raise nahi karta, errors ki list return karta hai. Types pehle check hote hain.

**Q7. Total revenue mein shipping kyun shamil hai?**
Customer shipping bhi ada karta hai, to woh collected paisa hai. Yeh meri assumption hai aur README mein likhi hai. Agar sir chahein to sirf `subtotal - discount` bhi ginwa sakta hoon (sirf `generate_sales_report` mein ek line badlegi).

**Q8. Top selling product tie ho to?**
Sab tied products dikhata hoon. Starter data mein Mouse aur Keyboard dono ke 2-2 units hain, isliye output "Keyboard, Mouse (tie - 2 units each)" aata hai.

**Q9. Discount subtotal par kyun, shipping subtotal par kyun?**
Assessment ke rules subtotal par likhe hain. ORD002 ka subtotal 450 hai, discount ke baad 427.50 hota, lekin shipping 450 < 500 hone se $20 lagti hai.

## B. Python concepts

**Q10. `*args` aur `**kwargs` mein farq?**
`*args` = bina naam ki values (tuple). `**kwargs` = naam wali values (dictionary). Project: `add_amounts(*amounts)` aur `process_order(..., **options)`.

**Q11. `**kwargs` project mein kahan use kiya?**
`process_order(order, products, apply_discount=False, include_shipping=False)`. Default dono True. Galat naam par ValueError.

**Q12. Lambda kya hai? Kahan use kiya?**
Chhota anonymous function. Report ranking sort karne mein `key=lambda pair: (-pair[1], pair[0])`.

**Q13. List comprehension ka faida?**
Chhota, saaf code. `[o for o in orders if o["status"] == "paid"]`. Jahan logic zyada complex ho wahan normal loop use kiya (jaise validate_order) taake readable rahe.

**Q14. Set kyun use kiya?**
Duplicates hatane ke liye (unique customers, categories) aur tez membership check ke liye (valid payment statuses).

**Q15. LEGB samjhao.**
Python variable ko Local, phir Enclosing, phir Global, phir Built-in scope mein dhoondta hai. Demo: `legb_demo.py`. Project mein globals se bacha hai; data arguments se pass hota hai. Closure example: `make_low_stock_checker`.

**Q16. Global variable kyun na use kiya?**
Kyunke function ka output kisi chhupay hue variable par depend na kare. Arguments se pass karne par function ko test karna aasaan hai.

**Q17. Closure kya hai?**
Andar wala function jo bahar wale function ke variable ko yaad rakhta hai, bahar wala function khatam hone ke baad bhi. `make_low_stock_checker(10)` ek `is_low()` function return karta hai jo `threshold=10` yaad rakhta hai.

**Q18. `if __name__ == "__main__":` kyun?**
File direct chalayein to `main()` chale; kisi aur file se import karein to na chale.

**Q19. `.get()` aur `[]` mein farq?**
`d["x"]` key na ho to KeyError. `d.get("x", 0)` default return karta hai.

**Q20. Mutable aur immutable?**
List/dict/set mutable (jagah par badal sakte hain). int/str/tuple immutable. Isi liye `update_inventory` mein pass ki hui `products` dictionary ka stock badal jata hai.

**Q21. Bool ko quantity ke taur par reject kyun kiya?**
Python mein `True` asal mein int hai (`True == 1`). Warna `quantity=True` valid ho jata.

**Q22. Float se paise ka masla?**
`0.1 + 0.2 = 0.30000000000000004`. Float 0.1 ko exact store nahi kar sakta, aur hazaron orders jama karne par farq barhta jata hai (1,000 orders ke total mein $15.25 ka farq aaya). Isliye hum `Decimal` se hisab karte hain (`utils.py`) aur cents tak round karte hain; price mein 2 se zyada decimal places reject hote hain.

## C. Agar sir kahein "yahan change karke dikhao"

| Sir ka sawal | Kahan badlein |
|---|---|
| Discount 15% se 20% | `config.py` -> `DISCOUNT_TIERS` |
| Shipping $20 se $30 | `config.py` -> `SHIPPING_FEE` |
| Low stock limit 5 | `config.py` -> `LOW_STOCK_THRESHOLD = 5` |
| Naya payment status "failed" | `config.py` -> `VALID_PAYMENT_STATUSES` (set mein add) |
| Revenue mein shipping na ho | `reports.py` -> `generate_sales_report` mein revenue line |
| Naya product | `data.py` -> `get_products()` mein ek entry |
| Discount band karke chalana | `process_order(order, products, apply_discount=False)` |

## D. Mushkil sawal (tayyari ke liye)
- **Agar 2 customers ka spending barabar ho?** Dono top customers mein aate hain (tie handle hai).
- **Agar order ID duplicate ho?** `process_all_orders` mein `seen_ids` set hai. Jo ID pehle accept (paid/pending) ho chuki ho, uska doosra order "Duplicate order ID" ke saath reject hota hai. Isliye stock aur revenue do baar nahi badhte. Rejected order ID use nahi karta, to sahi karke dobara bheja ja sakta hai.
- **Agar ek product ka data kharab ho (price string, stock missing)?** `validate_order` us product ko check karta hai aur sirf wohi order reject hota hai. Upar se `process_all_orders` mein try/except bhi hai, to ek order poora batch nahi rokta.
- **Agar class use karne ki ijazat hoti?** `Order`, `Product` classes banate; abhi assessment mein mana hai, isliye dictionaries.
- **Database hota to?** Stock update transaction mein hota taake do orders ek saath stock na kharab karein.
