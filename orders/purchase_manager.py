import csv
from pathlib import Path
from datetime import datetime
import random

PURCHASE_FILE = Path(__file__).parent.parent / "data" / "purchase_orders.csv"


def _ensure_header():
    if not PURCHASE_FILE.exists():
        PURCHASE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PURCHASE_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['purchase_id', 'purchase_date', 'product_id', 'quantity', 'unit_cost', 'total_cost'])
            writer.writeheader()


def record_purchase(product_id, quantity, unit_cost=0.0):
    """Record a purchase (reorder) into `data/purchase_orders.csv`.

    Returns the generated purchase_id and purchase_date.
    """
    _ensure_header()
    purchase_id = f"PO{random.randint(100000, 999999)}"
    purchase_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    qty = int(quantity)
    unit = float(unit_cost or 0.0)
    total = round(unit * qty, 2)

    row = {
        'purchase_id': purchase_id,
        'purchase_date': purchase_date,
        'product_id': product_id,
        'quantity': qty,
        'unit_cost': unit,
        'total_cost': total,
    }

    with open(PURCHASE_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['purchase_id', 'purchase_date', 'product_id', 'quantity', 'unit_cost', 'total_cost'])
        writer.writerow(row)

    return purchase_id, purchase_date


def view_purchases(month=None, year=None):
    """Return a list of purchase rows optionally filtered by month and year.

    `month` (1-12) and `year` (e.g., 2025) are integers.
    """
    if not PURCHASE_FILE.exists():
        return []

    rows = []
    with open(PURCHASE_FILE, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            # parse date
            try:
                dt = datetime.strptime(r.get('purchase_date', ''), "%Y-%m-%d %H:%M:%S")
            except Exception:
                # try fallback date-only
                try:
                    dt = datetime.strptime(r.get('purchase_date', ''), "%Y-%m-%d")
                except Exception:
                    dt = None

            if dt is not None:
                if month and dt.month != int(month):
                    continue
                if year and dt.year != int(year):
                    continue

            # normalize numeric types
            r['quantity'] = int(r.get('quantity', 0) or 0)
            r['unit_cost'] = float(r.get('unit_cost', 0) or 0)
            r['total_cost'] = float(r.get('total_cost', 0) or 0)
            rows.append(r)

    return rows


def show_purchases(month=None, year=None):
    rows = view_purchases(month=month, year=year)
    if not rows:
        print("No purchase orders found for the given period.")
        return

    print(f"{'Purchase ID':12} {'Date':20} {'Product ID':10} {'Qty':5} {'Unit':8} {'Total':10}")
    print('-' * 70)
    for r in rows:
        print(f"{r.get('purchase_id',''):12} {r.get('purchase_date',''):20} {r.get('product_id',''):10} {r.get('quantity',0):<5} {r.get('unit_cost',0):8.2f} {r.get('total_cost',0):10.2f}")
