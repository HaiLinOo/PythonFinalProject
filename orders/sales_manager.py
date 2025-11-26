# orders/sales_manager.py
class DummySalesCLIError(Exception):
    pass

class SalesManager:
    def __init__(self, inventory_manager):
        self.inventory = inventory_manager
        self.orders = []

    def create_order_cli(self):
        # very simple interactive CLI for now
        pid = input("Enter product id (e.g., P001): ").strip()
        if pid not in self.inventory.products:
            print("Product not found.")
            return
        qty_text = input("Enter quantity: ").strip()
        try:
            qty = int(qty_text)
        except ValueError:
            print("Invalid quantity.")
            return

        # check stock
        stock = self.inventory.products[pid]["stock"]
        if qty > stock:
            print(f"Not enough stock (available: {stock}). Aborting order.")
            return

        # deduct
        self.inventory.products[pid]["stock"] = stock - qty
        # save back to file (optional, simple approach)
        try:
            import json, os
            path = os.path.join(os.path.dirname(__file__), "..", "data", "products.json")
            path = os.path.abspath(path)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.inventory.products, f, indent=2)
        except Exception as e:
            print("Warning: couldn't save products:", e)

        order = {"product_id": pid, "quantity": qty}
        self.orders.append(order)
        print("Order created:", order)

    def show_orders(self):
        if not self.orders:
            print("No sales orders yet.")
            return
        print("\n--- Sales Orders ---")
        for i, o in enumerate(self.orders, start=1):
            print(f"{i}. {o['product_id']} x {o['quantity']}")