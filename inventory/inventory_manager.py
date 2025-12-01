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

        If `quantity` is provided, reorder exactly that amount; otherwise
        use the product's configured `reorder_quantity`.
        """
        pid = str(product_id)

        if pid not in self.products:
            raise KeyError(f"Product ID {product_id} not found in inventory.")
            return False

        info = self.products[pid]
        qty = int(quantity) if quantity is not None else int(info.get("reorder_quantity", 0) or 0)

        if qty <= 0:
            print("Reorder quantity must be greater than zero. No action taken.")
            return False

        info["current_stock"] += qty
        print(f"Reordered {qty} units of {info['product']}. (New stock: {info['current_stock']})")
        self._save_to_csv()
        # Record the purchase (reorder) to the purchase manager CSV
        try:
            from orders.purchase_manager import record_purchase
            purchase_id, purchase_date = record_purchase(pid, qty, unit_cost=info.get('price', 0))
            print(f"Recorded purchase {purchase_id} on {purchase_date}.")
        except Exception:
            # non-fatal: if purchase recording fails, proceed but notify
            print("Warning: failed to record purchase in purchase_orders.csv")

        return True

    
