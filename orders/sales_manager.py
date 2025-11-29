# orders/sales_manager.py
import csv
import random
from datetime import datetime
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

        # Check Stock
        stock = self.inventory.products[pid]["current_stock"]

        # For the case: Not enough stock -> offer to reorder
        if qty > stock:
            print(f"Not enough stock (available: {stock}).")
            
            # SHow reorder option
            info = self.inventory.products[pid]
            print(f"Suggested reorder quantity: {info['reorder_quantity']} units.")
            
            choice = input("Do you want to reorder? (y/n): ").strip().lower()
            if choice == 'y':
                self.inventory.reorder(pid)
                stock = self.inventory.products[pid]["current_stock"]
                print(f"Stock updated. Current Stock: {stock}")
            else:
                print("Order aborted.")
                
            #  Re-check stock after reorder
            if qty > stock:
                print(f"Still not enough stock after reorder (available: {stock}). Order aborted.")
                return
        
        # Now stock is sufficient -> process order
        self.inventory.products[pid]["current_stock"] -= qty
        self.inventory._save_to_csv()

        # Build order with id and date so CSV rows match existing format
        order_id = f"SO{random.randint(100000, 999999)}"
        order_date = datetime.now().strftime("%Y-%m-%d")
        order = {"order_id": order_id, "order_date": order_date, "product_id": pid, "quantity": qty}
        self.orders.append(order)
        print("Order created:", order)
        
        #  Deduct Stock in inventory
        new_stock = self.inventory.update_stock(pid, qty)
        print(f"Stock updated. New stock for {pid}: {new_stock}")

        # Save order to CSV
        # Save order to CSV using the full fieldset
        self._save_order_to_csv(order)

        # Low-Stock Check
        product = self.inventory.products[pid]
        if new_stock <= product["reorder_level"]:
            print("\n!!! LOW STOCK WARNING !!!")
            print(f"{product['product']} has only {new_stock} units left.")
            print(f"Suggested reorder quantity: {product['reorder_quantity']} units.\n")
                  
        # already appended above; just confirm
        print("Sales order created:", order)

    def _save_order_to_csv(self, order):
        file_exists = SALES_FILE.exists()
        # Ensure CSV has columns: order_id, order_date, product_id, quantity
        fieldnames = ['order_id', 'order_date', 'product_id', 'quantity']
        with open(SALES_FILE, mode='a', newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            # filter order dict to only these keys to avoid extra keys
            row = {k: order.get(k, '') for k in fieldnames}
            writer.writerow(row)

    def show_orders(self):
        print("\n--- Sales Orders ---")
        
        if not self.orders:
            print("No sales orders found.")
            return

        for order in self.orders:
            product_price = self.inventory.products[order['product_id']]['price']
            total_price = product_price * order['quantity']
            print(
                f"Order ID: {order['order_id']}, "
                f"Product ID: {order['product_id']}, "
                f"Quantity: {order['quantity']}, "
                f"Total Price: {total_price}, "
                f"Date: {order['order_date']}"
            )