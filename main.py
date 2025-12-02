# main directory

from inventory.inventory_manager import InventoryManager
from orders.sales_manager import SalesManager
from orders.sales_history import generate_random_sales
from orders.purchase_manager import show_purchases
from orders.sales_analytics import show_dashboard
from inventory.stock_configurator import StockConfigurator


def main_menu():
    inventory = InventoryManager()
    sales = SalesManager(inventory)
    configurator = StockConfigurator(inventory)  # use shared InventoryManager instance

    while True:
        print("\n=== INVENTORY MANAGEMENT SYSTEM ===")
        print("1. Inventory Management")
        print("2. Create Sales Order")
        print("3. View Sales Orders")
        print("4. View Purchase Orders")
        print("5. Generate 3-Year Sales History")
        print("6. Show Sales Dashboard")
        print("7. Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            # Inventory sub-menu (loop until user returns to main menu)
            while True:
                print("\n--- Inventory ---")
                print("A. View Current Stock Levels")
                print("B. Configure Critical Stock Levels")
                print("C. Back to Main Menu")
                sub_choice = input("Select an option: ").strip().upper()

                if sub_choice == "A":
                    inventory.show_inventory()
                elif sub_choice == "B":
                    pid = input("Enter Product ID to configure: ").strip()
                    configurator.define_critical_stock(pid)
                elif sub_choice == "C":
                    break
                else:
                    print("❌ Invalid sub-choice. Try again.")

        elif choice == "2":
            # fully working CLI for sales order creation
            sales.create_order_cli()

        elif choice == "3":
            sales.show_orders()

        elif choice == "4":
            # Prompt for optional month/year filter
            m = input("Enter month (1-12) to filter, or press Enter for all: ").strip()
            y = input("Enter year (e.g. 2025) to filter, or press Enter for all: ").strip()
            month = int(m) if m.isdigit() else None
            year = int(y) if y.isdigit() else None
            show_purchases(month=month, year=year)

        elif choice == "5":
            generate_random_sales()

        elif choice == "6":
            show_dashboard()

        elif choice == "7":
            print("Bye!")
            break
        else:
            print("❌ Invalid choice. Try again.")


if __name__ == "__main__":
    main_menu()
