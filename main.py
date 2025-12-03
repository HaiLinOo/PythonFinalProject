# main directory

from inventory.inventory_manager import InventoryManager
from orders.sales_manager import SalesManager
from orders.sales_history import generate_random_sales
from orders.purchase_manager import purchase_dashboard, show_purchases
from orders.sales_analytics import show_dashboard
from inventory.stock_configurator import StockConfigurator


def main_menu():
    inventory = InventoryManager()
    sales = SalesManager(inventory)
    configurator = StockConfigurator(inventory)  # use shared InventoryManager instance

    while True:
        print("\n=== INVENTORY MANAGEMENT SYSTEM ===")
        print("1. Inventory Management")
        print("2. Sales Management")
        print("3. Purchase Management")
        print("4. Exit ")
        choice = input("Select an option: ").strip()

        if choice == "1":
            # Inventory sub-menu (loop until user returns to main menu)
            while True:
                print("\n--- Inventory Management---")
                print("A. View Current Stock Levels")
                print("B. Configure Critical Stock Levels")
                print("C. Update Stock Levels")
                print("D. Low Stock Alerts")
                print("E. Back to Main Menu")
                sub_choice = input("Select an option: ").strip().upper()

                if sub_choice == "A":
                    inventory.show_inventory()
                elif sub_choice == "B":
                    pid = input("Enter Product ID to configure: ").strip()
                    configurator.define_critical_stock(pid)
                elif sub_choice == "C":
                    pid = input("Enter Product ID to update: ").strip()
                    delta = input("Enter stock change (positive to add, negative to remove): ").strip()
                    inventory.update_stock(pid, delta)
                elif sub_choice == "D":
                    inventory.check_low_stock()
                    print("\n--- Low Stock Products ---")
                    low_stock = inventory.check_low_stock()
                    if not low_stock:
                        print("All products are above critical stock levels.")
                    else:
                        print(f"{'ID':<6} {'Product Name':<25} {'Stock':<8} {'Critical':<10}")
                        print("-" * 55)
                        for pid, info in low_stock:
                            print(f"{pid:<6} {info['product']:<25} {info['current_stock']:<8} {info['reorder_level']:<10}")

                elif sub_choice == "E":
                    break
                else:
                    print("❌ Invalid sub-choice. Try again.")

        elif choice == "2":
             # Sales sub-menu (loop until user returns to main menu)
            while True:
                print("\n--- Sales Management---")
                print("A. Create Sales Order")
                print("B. View Sales Orders")
                print("C. Show Sales Dashboard")
                print("D. Generate 3-Year Sales History")
                print("E. Back to Main Menu")
                sub_choice2 = input("Select an option: ").strip().upper()
                if sub_choice2 == "A":
                    # fully working CLI for sales order creation
                    sales.create_order_cli()
                elif sub_choice2 == "B":
                    sales.show_orders()
                elif sub_choice2 == "C":
                    show_dashboard()
                elif sub_choice2 == "D":
                    generate_random_sales()
                elif sub_choice2 == "E":
                    break
                else:
                    print("❌ Invalid sub-choice. Try again.")

        elif choice == "3":
              # Sales sub-menu (loop until user returns to main menu)
            while True:
                print("\n--- Purchase Management---")
                print("A. Monthly View Purchase Order")
                print("B. View Purchase Orders")
                print("C. Create Critical Stock Level Purchase Orders")
                print("D. Show Purchase Dashboard")
                print("E. Back to Main Menu")
                sub_choice3 = input("Select an option: ").strip().upper()
                if sub_choice3 == "A": 
                     # Prompt for optional month/year filter
                    m = input("Enter month (1-12) to filter, or press Enter for all: ").strip()
                    y = input("Enter year (e.g. 2025) to filter, or press Enter for all: ").strip()
                    month = int(m) if m.isdigit() else None
                    year = int(y) if y.isdigit() else None
                    show_purchases(month=month, year=year)

                elif sub_choice3 == "B":
                    show_purchases()
                elif sub_choice3 == "C":
                    low_stock = inventory.check_low_stock()
                    if not low_stock:
                        print("All products are above critical stock levels.")
                    else:
                        for pid, info in low_stock:
                            needed_qty = info["reorder_level"] * 2 - info["current_stock"]
                            if needed_qty > 0:
                                inventory.reorder(pid, quantity=needed_qty)
                elif sub_choice3 == "D":
                    purchase_dashboard()
                elif sub_choice3 == "E":
                    break

        elif choice == "4":
            print("Bye!")
            break
        else:
            print("❌ Invalid choice. Try again.")


if __name__ == "__main__":
    main_menu()
