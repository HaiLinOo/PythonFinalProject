# orders/sales_manager.py
import csv
import random
import re
from datetime import datetime
from pathlib import Path

SALES_FILE = Path(__file__).parent.parent / "data" / "sales_orders.csv"

def _parse_order_date(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    return None

def sort_sales_by_date():
    if not SALES_FILE.exists():
        return
    with open(SALES_FILE, mode='r', newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r['_parsed_date'] = _parse_order_date(r.get('order_date', ''))
    rows.sort(key=lambda r: (r['_parsed_date'] is None, r['_parsed_date']))
    fieldnames = ['order_id', 'order_date', 'product_id', 'quantity']
    with open(SALES_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, '') for k in fieldnames})

def get_next_order_id():
    # ensure file is sorted so the last row is the latest by date
    try:
        sort_sales_by_date()
    except Exception:
        pass
    last_id = None
    if SALES_FILE.exists():
        with open(SALES_FILE, mode='r', newline='', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
            if rows:
                last_id = rows[-1].get('order_id')
    if not last_id:
        return "SO1"
    m = re.match(r"(\D*)(\d+)$", last_id)
    if m:
        prefix, num = m.group(1), int(m.group(2))
        return f"{prefix}{num+1}"
    else:
        return "SO1"

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
            product = self.inventory.products[pid]
            reorder_level = int(product.get("reorder_level", 0) or 0)
            reorder_qty = int(product.get("reorder_quantity", 0) or 0)

            # decide your minimum target after sale
            target_after_sale = reorder_level # or reorder_qty

            # how much stock is required in total before sale?
            total_required_before_sale = qty + target_after_sale

            needed = total_required_before_sale - stock
            if needed <= 0:
                needed = 0
            
            print(f"Not enough stock (available: {stock}).")
            print(f"To fullfill this sale AND keep minimum stock, you should reorder:  {needed} units to fulfill this order and maintain minimum stock levels.")
    

            # Ask to reorder the minimal required stock first
            choice = input(f"Do you want to reorder the minimum required ({needed}) now? (y/n): ").strip().lower()
            if choice == 'y':
                # Use the inventory.reorder with explicit quantity
                success = self.inventory.reorder(pid, quantity=needed)
                if success:
                    stock = self.inventory.products[pid]["current_stock"]
                    print(f"Stock updated. Current Stock: {stock}")
                else:
                    print("Reorder failed. Order aborted.")
                    return
            else:
                # offer full reorder_quantity fallback if configured
                info = self.inventory.products[pid]
                fallback = int(info.get('reorder_quantity', 0) or 0)
                if fallback > 0:
                    choice2 = input(f"Reorder minimum declined. Reorder default ({fallback}) instead? (y/n): ").strip().lower()
                    if choice2 == 'y':
                        success = self.inventory.reorder(pid, quantity=fallback)
                        if success:
                            stock = self.inventory.products[pid]["current_stock"]
                            print(f"Stock updated. Current Stock: {stock}")
                        else:
                            print("Reorder failed. Order aborted.")
                            return
                    else:
                        print("Order aborted.")
                        return
                else:
                    print("Order aborted.")
                    return
        
        # Now stock is sufficient -> process order
        self.inventory.products[pid]["current_stock"] -= qty
        self.inventory._save_to_csv()

        # Build order with id and date so CSV rows match existing format
        order_id = get_next_order_id()
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

    def show_orders(self, read_from_csv=True):
        """Display sales orders. By default, read and display rows from the CSV file if present.

        If `read_from_csv` is False the method will display in-memory `self.orders` only.
        """
        print("\n--- Sales Orders ---")

        rows = []
        if read_from_csv and SALES_FILE.exists():
            try:
                with open(SALES_FILE, mode='r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        # normalize numeric types
                        r['quantity'] = int(r.get('quantity', 0) or 0)
                        rows.append(r)
            except Exception as e:
                print("Failed to read sales CSV:", e)

        # Append in-memory orders that may not yet be persisted
        for o in self.orders:
            # avoid duplicating rows if already read from CSV (by order_id)
            if not any(r.get('order_id') == o.get('order_id') for r in rows):
                rows.append(o)

        if not rows:
            print("No sales orders found.")
            return

        # Print a simple table header
        print(f"{'Order ID':12} {'Date':20} {'Product ID':10} {'Qty':5} {'Total':10}")
        print('-' * 65)
        for r in rows:
            pid = r.get('product_id', '')
            qty = int(r.get('quantity', 0) or 0)
            order_date = r.get('order_date', '')
            order_id = r.get('order_id', '')
            price = 0
            try:
                price = float(self.inventory.products.get(pid, {}).get('price', 0) or 0)
            except Exception:
                price = 0
            total = price * qty
            print(f"{order_id:12} {order_date:20} {pid:10} {qty:<5} {total:10.2f}")
    