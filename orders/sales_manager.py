# orders/sales_manager.py
import csv
from pathlib import Path

SALES_FILE = Path(__file__).parent.parent / "data" / "sales_orders.csv"


class SalesManager:
    def __init__(self, inventory_manager):
        self.inventory = inventory_manager
        self.orders = []

    def create_order_cli(self):
        print("\n--- Create New Sales Order ---")

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
        stock = self.inventory.products[pid]["current_stock"]
        if qty > stock:
            print(f"Not enough stock (available: {stock}). Aborting order.")
            return

        #  Deduct Stock in inventory
        new_stock = self.inventory.update_stock(pid, qty)
        print(f"Stock updated. New stock for {pid}: {new_stock}")

        # Save order to CSV
        order= {
            "product_id": pid,
            "quantity": qty,
        }
        self._save_order_to_csv(order)

        # Low-Stock Check
        product = self.inventory.products[pid]
        if new_stock <= product["reorder_level"]:
            print("\n!!! LOW STOCK WARNING !!!")
            print(f"{product['product']} has only {new_stock} units left.")
            print(f"Suggested reorder quantity: {product['reorder_quantity']} units.\n")
                  
        self.orders.append(order)
        print("Sales order created:", order)

    def _save_order_to_csv(self, order):
        file_exists = SALES_FILE.exists()

        with open(SALES_FILE, mode='a', newline="", encoding="utf-8") as f:
            fieldnames = ['product_id', 'quantity']
            writer = csv.DictWriter(f, fieldnames=['product_id', 'quantity'])
            if not file_exists:
                writer.writeheader()
            writer.writerow(order)
