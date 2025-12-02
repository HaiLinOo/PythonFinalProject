# inventory/inventory_manager.py
import pandas as pd
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "laptop_inventory.csv"

class InventoryManager:
    def __init__(self):
        # try to load products, if not present create sample
        self.products = {}
        self._load_from_csv()

    def _load_from_csv(self):
        if not DATA_FILE.exists():
            print(f"Data file not found: {DATA_FILE}")
            return
        df = pd.read_csv(DATA_FILE, dtype={"product_id": str}) 
        # normalize and convert to dict
        for _, row in df.iterrows():
            pid = str(row["product_id"])
            self.products[pid] = {
                "company": row.get("company", ""),
                "product": row.get("product", ""),
                "type": row.get("type", ""),
                "cpu": row.get("cpu", ""),
                "gpu": row.get("gpu", ""),
                "price": float(row.get("price", 0) or 0),
                "current_stock": int(row.get("current_stock", 0) or 0),
                "reorder_level": int(row.get("reorder_level", 0) or 0),
                "reorder_quantity": int(row.get("reorder_quantity", 0) or 0),
            }
        

    def show_inventory(self):
        print("\n--- Current Inventory ---")
        print(f"{'ID':<6} {'Product Name':<25} {'Stock':<8} {'Price':<10}")
        print("-" * 50)
        for pid, info in sorted(self.products.items()):
            print(f"{pid:<6} {info['product']:<25} {info['current_stock']:<8} {info['price']:<10.2f}")

    def update_stock(self, product_id, delta):
        pid = str(product_id)
        if pid not in self.products:
            raise KeyError(f"Product ID {product_id} not found in inventory.")
        self.products[pid]["current_stock"] += int(delta)
        return self.products[pid]["current_stock"]
    
    def check_low_stock(self):
        low = []
        for pid, info in self.products.items():
            if info["current_stock"] <= info["reorder_level"]:
                low.append((pid, info))
        return low

    # save updates to CSV
    def _save_to_csv(self):
        import pandas as pd

        df = pd.DataFrame.from_dict(self.products, orient='index')
        df.insert(0, "product_id", df.index)
        df.to_csv(DATA_FILE, index=False)
    
    # Reorder function
    def reorder(self, product_id, quantity=None):
        """Reorder stock for a product.

        If `quantity` is provided, use it as a minimum to reorder, 
        But still ensure the inventory ends up with at least reorder_level
        (or reorder_quantity) in stock after fulfilling the current demand.

        If `quantity` is None, reorder the default reorder_quantity.
        """
        pid = str(product_id)

        if pid not in self.products:
            raise KeyError(f"Reorder fail: Product {pid} not found in inventory.")
            return False

        product = self.products[pid]

        current_stock = int(product.get("current_stock", 0) or 0)
        reorder_level = int(product.get("reorder_level", 0) or 0)
        default_reorder_qty = int(product.get("reorder_quantity", 0) or 0)

        # ===1. Determine base quantity to reorder===
        if quantity is None:
            # use default reorder quantity
            wanted_qty = default_reorder_qty
        else:
            # quantity passed from SalesManager (e.g., the needed amount)
            wanted_qty = int(quantity)
            
        # ===2. Ensure minimum stock after purchase ===
        # we want:
        #   final_stock >= reorder_level
        #
        #   final_stock = current_stock + ordered_qty
        # so:
        #   ordered_qty >= reorder_level - current_stock
        min_required_to_reach_level = reorder_level - current_stock
        if min_required_to_reach_level < 0:
            min_required_to_reach_level = 0
        
        # The reorder quantity MUST satisfy BOTH conditions
        # - the explicitly requested quantity (sales demand)
        # - the minimum required to reach reorder level
        final_quantity = max(wanted_qty, min_required_to_reach_level)

        if final_quantity <= 0:
            print("No reorder needed. Stock is already above minimum level.")
            return True
        
        # ===3. Apply reorder ===
        new_stock = current_stock + final_quantity
        product["current_stock"] = new_stock

        print(f"Reordered {final_quantity} units of {product['product']}. New stock: {new_stock})")

        self._save_to_csv()
        return True
    

        # Record the purchase (reorder) to the purchase manager CSV
        try:
            from orders.purchase_manager import record_purchase
            purchase_id, purchase_date = record_purchase(pid, qty, unit_cost=info.get('price', 0))
            print(f"Recorded purchase {purchase_id} on {purchase_date}.")
        except Exception:
            # non-fatal: if purchase recording fails, proceed but notify
            print("Warning: failed to record purchase in purchase_orders.csv")

        return True

    
