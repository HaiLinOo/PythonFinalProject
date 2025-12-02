from inventory.inventory_manager import InventoryManager


class StockConfigurator:
    """Interactive helper to configure critical stock levels for products.

    Accepts an `InventoryManager` instance to operate on the shared dataset.
    If no manager is provided it will create one (backwards compatible).
    """

    def __init__(self, manager=None):
        self.manager = manager if manager is not None else InventoryManager()

    def define_critical_stock(self, product_id):
        """Ask user to set a critical stock level for a specific item.
        
        Returns True on success, False on failure or invalid input.
        """
        pid = str(product_id)
        if pid not in self.manager.products:
            print(f"❌ Product ID {product_id} not found.")
            return False

        product = self.manager.products[pid]
        print(f"\nConfiguring critical stock for: {product['product']} (Current stock: {product['current_stock']})")

        try:
            level = int(input("👉 Define critical stock level: "))
        except ValueError:
            print("❌ Invalid input. Must be a number.")
            return False

        if level < 0:
            print("❌ Critical stock level must be non-negative.")
            return False

        # Update the shared InventoryManager instance
        product["reorder_level"] = level
        print(f"✅ Critical stock level for {product['product']} set to {level} pcs.")

        # Save changes back to CSV
        self.manager._save_to_csv()
        return True
