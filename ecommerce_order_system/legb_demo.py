"""
legb_demo.py
------------
Demonstrates LEGB: Local -> Enclosing -> Global -> Built-in
Python looks for a variable name in this order.
Run:  python legb_demo.py
"""

shipping_fee = 20  # G: Global scope (module level)


def local_demo():
    shipping_fee = 5  # L: Local variable. Hides the global one, does NOT change it.
    return shipping_fee


def enclosing_demo():
    discount_rate = 0.10  # E: belongs to the outer function

    def inner(subtotal):
        # inner has no discount_rate of its own -> Python finds it in the
        # ENCLOSING scope
        return subtotal * discount_rate

    return inner(500)


def builtin_demo(prices):
    # len, sum, max are BUILT-IN names (the last place Python looks)
    return len(prices), sum(prices), max(prices)


def global_keyword_demo():
    # without this line, the assignment below would create a LOCAL variable
    global shipping_fee
    shipping_fee = 99


def nonlocal_demo():
    counter = 0

    def add_one():
        nonlocal counter  # change the variable of the ENCLOSING function
        counter += 1

    add_one()
    add_one()
    return counter


if __name__ == "__main__":
    print("Global shipping_fee at start :", shipping_fee)
    print("Local  (inside function)     :", local_demo())
    print("Global after local_demo()    :", shipping_fee, "(unchanged)")
    print("Enclosing (10% of 500)       :", enclosing_demo())
    print("Built-in (len, sum, max)     :", builtin_demo([25, 75, 300]))
    print("nonlocal counter             :", nonlocal_demo())
    global_keyword_demo()
    print("Global after 'global' keyword:", shipping_fee, "(changed)")
    print()
    print("In the real project we avoid globals: data is passed as function")
    print("arguments, and reports.make_low_stock_checker() uses a closure (E).")
