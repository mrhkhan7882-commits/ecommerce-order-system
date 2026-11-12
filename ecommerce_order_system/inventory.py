"""
inventory.py
------------
Everything that touches stock.
"""


def copy_products(products):
    """Independent copy (dict comprehension) so tests can't spoil the original."""
    return {product_id: dict(info) for product_id, info in products.items()}


def update_inventory(order, products):
    """
    Reduce stock for every item of a SUCCESSFULLY processed order.
    NOTE: this changes the `products` dictionary directly (dictionaries are mutable).
    """
    for item in order["items"]:
        products[item["product_id"]]["stock"] -= item["quantity"]
