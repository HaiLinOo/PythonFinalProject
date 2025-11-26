# this code generates 3 years of sales orders

import csv
import random
from datetime import datetime, timedelta
import os

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "..", "data")
SALES_FILE = os.path.join(DATA_FOLDER, "sales_orders.csv")
INVENTORY_FILE = os.path.join(DATA_FOLDER, "laptop_inventory.csv")

def load_inventory():
    '''Load product_ids from the inventory file.'''
    products = []
    with open(INVENTORY_FILE, mode='r', newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            products.append(row['product_id'])
    return products

def generate_random_sales():
    '''Generate random sales orders for the past 3 years.'''
    products = load_inventory()

    # Date range: 2023 -> 2025
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 12, 31)
    delta_days = (end_date - start_date).days

    rows = []

    for _ in range(1500):  # Generate 1500 random orders across 3 years
        random_day = start_date + timedelta(days=random.randint(0, delta_days))
        product_id = random.choice(products)
        quantity = random.randint(1, 5)  # Random quantity between 1 and 5

        # seasonal demand modeling: increase sales in Oct, Nov & Dec
        if random_day.month in [10, 11, 12]:
            quantity += random.choice([1, 2]) 

        rows.append({
            'order_id': f"SO{random.randint(100000, 999999)}",
            'order_date': random_day.strftime("%Y-%m-%d"),
            'product_id': product_id,
            'quantity': quantity,
        })


    # Write to CSV
    with open(SALES_FILE, mode='w', newline="", encoding="utf-8") as file:
        fieldnames = ['order_id', 'order_date', 'product_id', 'quantity']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows) 

    print("Sales order history generated successfully.")
