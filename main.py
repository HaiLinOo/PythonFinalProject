# main directory

from inventory.inventory_manager import InventoryManager
from orders.sales_manager import SalesManager
from orders.sales_manager import DummySalesCLIError

def main_menu():
    inventory = InventoryManager()
    sales = SalesManager(inventory)

    while True:
        print("\n=== INVENTORY MANAGEMENT SYSTEM ===")
        print("1. View Inventory")
        print("2. Create Sales Order")
        print("3. View Sales Orders")
        print("4. Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            inventory.show_inventory()
        elif choice == "2":
            try:
                sales.create_order_cli()
            except DummySalesCLIError:
                # for the very first step you may not have real logic yet
                print("Sales CLI not implemented yet. This is a placeholder.")
        elif choice == "3":
            sales.show_orders()
        elif choice == "4":
            print("Bye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main_menu()