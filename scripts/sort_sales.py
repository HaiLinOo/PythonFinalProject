import csv
from datetime import datetime
from pathlib import Path

SALES_FILE = Path(__file__).parent.parent / "data" / "sales_orders.csv"

def parse_date(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    return None

def main():
    if not SALES_FILE.exists():
        print(f"Sales file not found: {SALES_FILE}")
        return
    with open(SALES_FILE, mode='r', newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r['_parsed'] = parse_date(r.get('order_date', ''))
    rows.sort(key=lambda r: (r['_parsed'] is None, r['_parsed']))
    fieldnames = ['order_id', 'order_date', 'product_id', 'quantity']
    with open(SALES_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, '') for k in fieldnames})
    print(f"Sorted {SALES_FILE} by order_date., backed up to sales_orders.csv.bak if you made a copy")

if __name__ == "__main__":
    main()