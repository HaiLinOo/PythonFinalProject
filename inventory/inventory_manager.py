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
        print("ID | Product Name | Stock | Price")
        print("-------------------------------")
        for pid, info in sorted(self.products.items()):
            print(f"{pid} | {info["product"]} | {info["current_stock"]} | {info["price"]}")

def updata_stock(self, product_id, delta):
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

