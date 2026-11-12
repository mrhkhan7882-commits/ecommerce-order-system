# 07 - Demo Script aur Tips

## Run karne ke commands
```
python main.py          # report + details
python test_cases.py    # all tests passed dikhna chahiye
python legb_demo.py     # LEGB demo
```
Windows par `python`, Mac/Linux par `python3`.

## Sir ko demo kaise dikhana hai (5 minute)
1. **Folder kholo** - files ka naqsha batao (01_project_overview.md ka table).
2. **`python main.py` chalao** - report dikhao. Numbers batao: revenue $1,510, discount $210, shipping $20.
3. **ORD003 dikhao** - "yeh pending hai, isliye revenue mein nahi, stock bhi nahi ghata (Mouse 48 hai, 43 nahi)".
4. **`python test_cases.py` chalao** - "62 tests, sab edge cases cover".
5. **Code dikhao**: `validation.py` (crash nahi hota), `processing.py` (**kwargs), `reports.py` (lambda, set, closure).
6. **`python legb_demo.py`** - LEGB.

## Live thori si cheez try karo (impress karne ke liye)
`python` interactive mein:
```python
from data import get_products
from processing import process_order
p = get_products()
order = {"order_id": "X1", "customer": "Sara",
         "items": [{"product_id": "P999", "quantity": 1}],
         "payment_status": "paid"}
print(process_order(order, p)["errors"])
```
Output: `["Item 1: unknown product ID 'P999'"]`

## Tips
- Jo cheez samajh na aaye wahan honestly kaho: "Sir, yeh part main dobara samjhata hoon" - phir code kholkar line by line batao.
- Code **khud ek baar line by line parho**. Sab se pehle: validation.py -> calculations.py -> processing.py -> reports.py.
- 06_viva_questions_answers.md ke jawab apne alfaaz mein yaad karo, ratta mat lagao.
- Sir change maange to 06 ki file ka section C dekho (kahan kya badlna hai).
- Python version: 3.8 ya naya.

## Parhne ka plan (1 din mein)
| Waqt | Kaam |
|---|---|
| 30 min | 01 aur 03 parho (flow + numbers) |
| 1 ghanta | Code files line by line parho (02 saath rakho) |
| 30 min | 04 (concepts) - har example khud chala kar dekho |
| 30 min | 05 aur test_cases.py chalao |
| 30 min | 06 ke jawab apne alfaaz mein bolo |
